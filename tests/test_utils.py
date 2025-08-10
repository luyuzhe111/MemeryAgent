import logging

from utils import build_character_instructions, get_available_characters


def test_get_available_characters():
    """Test listing local memes with the actual memes directory."""
    characters = get_available_characters("memes")

    # Should find the characters you added
    assert isinstance(characters, list)
    assert "crybaby" in characters
    assert "hosico" in characters

    # Should be sorted
    assert characters == sorted(characters)

    logging.info(build_character_instructions())
