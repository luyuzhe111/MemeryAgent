import base64
import logging
import os
from urllib.parse import urlparse

import requests
from agents import function_tool
from dotenv import load_dotenv

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
            data={"model": "gpt-image-1", "prompt": prompt},
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
    output_file: str = "output.png",
) -> bool:
    """
    Create a composite image using OpenAI's image editing API.

    Args:
        prompt: Text description of how to edit images listed in the image_paths
        image_paths: List of paths to image files
        output_file: Output filename for the generated image

    Returns:
        True if successful, False otherwise
    """
    return _create_composite_image_impl(prompt, image_paths, output_file)


def _download_x_profile_picture_impl(
    username: str,
    output_dir: str = "profile_pics",
) -> str | None:
    """
    Core implementation for downloading X profile pictures.

    Args:
        username (str): X username (without @)
        output_dir (str): Directory to save the profile picture

    Returns:
        str: Path to the downloaded image file, or None if failed
    """
    load_dotenv()

    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    if not bearer_token:
        raise ValueError("TWITTER_BEARER_TOKEN not found in environment variables")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Headers for Twitter API v2
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
    }

    try:
        # Get user info including profile image URL
        user_url = f"https://api.twitter.com/2/users/by/username/{username}"
        params = {"user.fields": "profile_image_url"}

        response = requests.get(user_url, headers=headers, params=params)
        response.raise_for_status()

        user_data = response.json()

        if "data" not in user_data:
            print(f"User {username} not found")
            return None

        # Get the profile image URL (remove _normal to get full size)
        profile_image_url = user_data["data"]["profile_image_url"]
        full_size_url = profile_image_url.replace("_normal", "")

        # Download the image
        img_response = requests.get(full_size_url)
        img_response.raise_for_status()

        # Determine file extension from URL
        parsed_url = urlparse(full_size_url)
        file_extension = os.path.splitext(parsed_url.path)[1] or ".jpg"

        # Save the image
        filename = f"{username}_profile{file_extension}"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "wb") as f:
            f.write(img_response.content)

        print(f"Profile picture downloaded: {filepath}")
        return filepath

    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None
    except Exception as e:
        print(f"Error downloading profile picture: {e}")
        return None


@function_tool
def download_x_profile_picture(
    username: str,
    output_dir: str = "profile_pics",
) -> str | None:
    """
    Downloads the profile picture of an X (Twitter) user.

    Args:
        username (str): X username (without @)
        output_dir (str): Directory to save the profile picture

    Returns:
        str: Path to the downloaded image file, or None if failed
    """
    return _download_x_profile_picture_impl(username, output_dir)


# Example usage
if __name__ == "__main__":
    # Example: download profile picture for username "elonmusk"
    result = _download_x_profile_picture_impl("elonmusk")
    if result:
        print(f"Success! Image saved to: {result}")
    else:
        print("Failed to download profile picture")
