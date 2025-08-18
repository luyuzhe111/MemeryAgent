import os
from pathlib import Path


def build_prompt_from_tweet(tweet: str, author_username: str, me_username: str) -> str:
    # remove the tag to avoid confusing the agent
    tweet_content = tweet.replace(f"@{me_username}", "").strip()

    # provide context on the author of the tweet
    prompt = (
        f"The following is a tweet written by @{author_username}.\n\n"
        f'Tweet content: "{tweet_content}"\n\n'
    )

    # additional instructions.
    prompt += "Generate an image based on the tweet."

    return prompt


def get_available_characters(memes_dir: str = "memes") -> list[str]:
    """
    Discover available meme characters by scanning the memes directory.

    Args:
        memes_dir: Path to the memes directory (relative to project root)

    Returns:
        List of character names (directory names in memes folder)
    """
    try:
        memes_path = Path(memes_dir)

        if not memes_path.exists():
            return []

        characters = []
        for item in memes_path.iterdir():
            if item.is_dir():
                characters.append(item.name)

        return sorted(characters)
    except Exception as e:
        print(f"Error scanning memes directory: {e}")
        return []


def build_character_instructions(memes_dir: str = "memes") -> str:
    """
    Build instructions text with available meme characters.

    Returns:
        Formatted string with available characters
    """
    characters = get_available_characters(memes_dir)

    if not characters:
        return "No local meme characters are currently available."

    character_list = ", ".join(characters)
    return f"Locally available meme characters: {character_list}"


def get_output_directory() -> str:
    """
    Get the appropriate output directory based on environment.

    Returns:
        Output directory path for images
    """
    return os.getenv("RAILWAY_VOLUME_MOUNT_PATH", "output_images")


def get_output_path(filename: str) -> str:
    """
    Get the full output path for an image file.

    Args:
        filename: Name of the output file

    Returns:
        Full path to the output file
    """
    output_dir = get_output_directory()
    if not output_dir.startswith("/app"):
        os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, filename)
