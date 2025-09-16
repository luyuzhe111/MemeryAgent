import logging
import os
import time
import uuid

from agents import function_tool
from dotenv import load_dotenv
from google import genai
from google.genai.types import Image

from utils import get_video_output_path

load_dotenv()

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


async def _image_to_video_generation_impl(
    image_path: str,
    output_file: str = "output_video.mp4",
) -> bool:
    """
    Generate a video from an image.

    Args:
        image_path: Path to the input image file
        output_file: Output filename for the generated video

    Returns:
        True if successful, False otherwise
    """

    # Log the function call details
    tool_logger.info("Generating animated video from image")
    tool_logger.info(f"Input image: {image_path}")
    tool_logger.info(f"Output file: {output_file}")

    # Verify the image file exists
    if not os.path.exists(image_path):
        tool_logger.error(f"Image file not found: {image_path}")
        return False

    tool_logger.info(
        f"Found image file: {image_path} (size: {os.path.getsize(image_path)} bytes)"
    )

    try:
        tool_logger.info("Initializing video gen client...")
        client = genai.Client()

        tool_logger.info("Sending video generation request to Veo 3...")

        # Generate video with Veo 3 from an image
        operation = client.models.generate_videos(
            model="veo-3.0-fast-generate-001",
            image=Image.from_file(location=image_path),
        )

        tool_logger.info(f"Video generation operation started: {operation.name}")

        # Poll the operation status until the video is ready
        max_attempts = 30  # Wait up to 5 minutes (10 second intervals)
        attempt = 0

        while not operation.done and attempt < max_attempts:
            attempt += 1
            tool_logger.info(
                f"Waiting for video generation to complete... (attempt {attempt}/{max_attempts})"
            )
            time.sleep(10)
            operation = client.operations.get(operation)

        if not operation.done:
            tool_logger.error("Video generation timed out")
            return False

        if operation.error:
            tool_logger.error(f"Video generation failed: {operation.error}")
            return False

        # Download the video
        tool_logger.info("Video generation completed, downloading...")
        video = operation.response.generated_videos[0]

        # Download the file content
        client.files.download(file=video.video)

        # Save the video to the specified output file
        video.video.save(output_file)

        tool_logger.info(f"Video successfully saved to: {output_file}")
        print(f"Video saved to: {output_file}")
        return True

    except Exception as e:
        tool_logger.error(f"Exception occurred: {str(e)}")
        print(f"Error: {str(e)}")
        return False


@function_tool
async def generate_video_from_image(
    image_path: str,
    output_filename: str = "output_video.mp4",
) -> str:
    """
    Generate an animated video from an image.

    Args:
        image_path: Path to the input image file (typically from create_composite_image)
        output_filename: Output filename for the generated video

    Returns:
        Full path to the generated video if successful, empty string if failed
    """
    # Ensure the output has .mp4 extension
    if not output_filename.endswith(".mp4"):
        output_filename += ".mp4"

    # Generate unique filename if not specified
    if output_filename == "output_video.mp4":
        unique_id = str(uuid.uuid4())[:8]
        output_filename = f"generated_video_{unique_id}.mp4"

    output_path = get_video_output_path(output_filename)

    success = await _image_to_video_generation_impl(image_path, output_path)
    return output_path if success else ""
