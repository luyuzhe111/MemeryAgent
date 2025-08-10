from pathlib import Path


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
