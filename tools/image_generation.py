import base64
import logging
import os

import requests
from agents import function_tool

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


def _create_composite_image_impl(
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
        response = requests.post(
            "https://api.openai.com/v1/images/edits",
            headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"},
            # TODO: lower the moderation level for the image edit API when available.
            data={"model": "gpt-image-1", "prompt": prompt, "quality": "high"},
            files=files,
        )

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
def create_composite_image(
    prompt: str,
    image_paths: list[str],
    output_filename: str = "output.png",
) -> str:
    """
    Create a composite image using OpenAI's image editing API.

    Args:
        prompt: Text description of how to edit images listed in the image_paths
        image_paths: List of paths to image files
        output_filename: Output filename for the generated image

    Returns:
        Full path to the generated image if successful, empty string if failed
    """
    output_path = get_output_path(output_filename)
    success = _create_composite_image_impl(prompt, image_paths, output_path)
    return output_path if success else ""
