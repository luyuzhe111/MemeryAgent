import base64
import logging
import os

import httpx
import matplotlib.font_manager as fm
from agents import function_tool
from PIL import Image, ImageDraw, ImageFont

from utils import get_output_path

# Configure logging for tool calls only
tool_logger = logging.getLogger("tool_call")
tool_logger.setLevel(logging.INFO)

# Only add handler if it doesn't already exist (prevents duplicate logs)
if not tool_logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    tool_logger.addHandler(handler)
    tool_logger.propagate = False  # Don't pass to root logger


def get_font(size: int) -> ImageFont.FreeTypeFont:
    """
    Get font - try bundled Montserrat first, then fallback to bold italic sans-serif.

    Args:
        size: Font size in pixels

    Returns:
        PIL ImageFont object
    """
    # Try bundled Montserrat Bold Italic font
    bundled_font_path = os.path.join(
        os.path.dirname(__file__), "..", "assets", "fonts", "Montserrat-BoldItalic.ttf"
    )
    if os.path.exists(bundled_font_path):
        try:
            return ImageFont.truetype(bundled_font_path, size)
        except OSError:
            pass

    # Fallback to system bold italic sans-serif
    try:
        font_path = fm.findfont(
            fm.FontProperties(family="sans-serif", weight="bold", style="italic")
        )
        return ImageFont.truetype(font_path, size)
    except OSError:
        return ImageFont.load_default()


def add_watermark(image_path: str) -> bool:
    """
    Add @memery_labs watermark in white text to the bottom right of an image.

    Args:
        image_path: Path to the image file to watermark

    Returns:
        True if successful, False otherwise
    """
    try:
        with Image.open(image_path) as img:
            # Convert to RGBA for transparency support
            if img.mode != "RGBA":
                img = img.convert("RGBA")

            # Create a transparent overlay for the text
            overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(overlay)

            # Watermark text
            watermark_text = "@memery_labs"

            # Calculate font size to be 1/24 of image height
            font_size = img.height // 24

            # Get font using our cross-platform function
            font = get_font(font_size)

            # Get text dimensions
            text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

            # Position text in bottom right with padding
            padding = 20
            x = img.width - text_width - padding
            y = img.height - text_height - padding

            # Draw the watermark text in white (no background)
            draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 255))

            # Composite the overlay onto the original image
            watermarked = Image.alpha_composite(img, overlay)

            # Convert back to RGB for saving (most formats don't support RGBA)
            if watermarked.mode == "RGBA":
                rgb_img = Image.new("RGB", watermarked.size, (255, 255, 255))
                rgb_img.paste(watermarked, mask=watermarked.split()[-1])
                watermarked = rgb_img

            watermarked.save(image_path)
            tool_logger.info(
                f"Watermark '@memery_labs' added successfully to {image_path}"
            )
            return True

    except Exception as e:
        tool_logger.error(f"Failed to add watermark: {str(e)}")
        return False


async def _create_composite_image_impl(
    prompt: str,
    image_paths: list[str],
    output_file: str = "output.png",
) -> bool:
    """
    Create a composite image using OpenAI's image editing API.

    Args:
        prompt: Text description of how to combine the images
        image_paths: List of paths to image files
        output_file: Output filename for the generated image

    Returns:
        True if successful, False otherwise
    """

    # Provide context on what images the agent is seeing (based on the file path).
    prompt = f"The images you are seeing are {', '.join(image_paths)}. " + prompt

    # Other guidelines
    prompt = (
        prompt + " Do not include tweet text in the image unless explicitly requested."
    )

    # TODO: Refine the prompt with a model call.

    # Log the function call details
    tool_logger.info(f"Creating composite image with prompt: '{prompt}'")
    tool_logger.info(f"Input images: {image_paths}")
    tool_logger.info(f"Output file: {output_file}")

    # Verify all image files exist
    for path in image_paths:
        if not os.path.exists(path):
            tool_logger.error(f"Image file not found: {path}")
            return False
        tool_logger.info(
            f"Found image file: {path} (size: {os.path.getsize(path)} bytes)"
        )

    files = [("image[]", open(path, "rb")) for path in image_paths]

    try:
        tool_logger.info("Sending request to OpenAI API...")
        async with httpx.AsyncClient(timeout=180) as client:
            try:
                response = await client.post(
                    "https://api.openai.com/v1/images/edits",
                    headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"},
                    # TODO: lower the moderation level for the image edit API when available.
                    data={
                        "model": "gpt-image-1",
                        "prompt": prompt,
                        "quality": "high",
                        "input_fidelity": "high",
                        "moderation": "low",
                        "size": "1536x1024",
                    },
                    files=files,
                )
            except Exception:
                import traceback

                traceback.print_exc()

        if response.status_code == 200:
            tool_logger.info("API request successful")
            result = response.json()

            # Extract and decode base64 image
            if "data" in result and len(result["data"]) > 0:
                tool_logger.info("Extracting image data from response")
                b64_image = result["data"][0]["b64_json"]
                image_data = base64.b64decode(b64_image)

                # Save the image
                with open(output_file, "wb") as f:
                    f.write(image_data)

                tool_logger.info(
                    f"Composite image successfully saved to: {output_file}"
                )

                # Add watermark to the generated image
                if add_watermark(output_file):
                    tool_logger.info("Watermark added to composite image")
                else:
                    tool_logger.warning("Failed to add watermark to composite image")

                print(f"Image saved to: {output_file}")
                return True
            else:
                tool_logger.error("No image data in API response")
                print("Error: No image data in response")
                return False
        else:
            tool_logger.error(f"API request failed with status {response.status_code}")
            tool_logger.error(f"Response: {response.text}")
            print(f"Error: API request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        tool_logger.error(f"Exception occurred: {str(e)}")
        print(f"Error: {str(e)}")
        return False


@function_tool
async def create_composite_image(
    image_paths: list[str],
    prompt: str,
    output_filename: str = "output.png",
) -> str:
    """
    Create a composite image using OpenAI's image editing API.

    Args:
        image_paths: List of paths to image files necessary for generating images.
        prompt: A detailed description of how to edit images listed in the image_paths
        output_filename: Output filename for the generated image

    Returns:
        Full path to the generated image if successful, empty string if failed
    """
    output_path = get_output_path(output_filename)
    success = await _create_composite_image_impl(prompt, image_paths, output_path)
    return output_path if success else ""
