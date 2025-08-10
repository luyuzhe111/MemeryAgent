import os
from urllib.parse import urlparse

import requests
from agents import function_tool
from dotenv import load_dotenv


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
