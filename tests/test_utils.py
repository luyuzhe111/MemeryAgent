import logging
import os

from utils import (
    build_character_instructions,
    get_available_characters,
    get_output_directory,
    get_output_path,
)


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


def test_get_output_directory():
    """Test output directory selection based on environment."""
    # Test local environment (no RAILWAY_ENVIRONMENT_NAME)
    if "RAILWAY_ENVIRONMENT_NAME" in os.environ:
        del os.environ["RAILWAY_ENVIRONMENT_NAME"]

    assert get_output_directory() == "output_images"

    # Test Railway environment
    os.environ["RAILWAY_ENVIRONMENT"] = "production"
    assert get_output_directory() == "/data/output_images"

    # Clean up
    if "RAILWAY_ENVIRONMENT_NAME" in os.environ:
        del os.environ["RAILWAY_ENVIRONMENT_NAME"]


def test_get_output_path():
    """Test output path generation."""
    # Ensure we're in local mode
    if "RAILWAY_ENVIRONMENT_NAME" in os.environ:
        del os.environ["RAILWAY_ENVIRONMENT_NAME"]

    # Test basic functionality
    result = get_output_path("test.png")
    assert result.endswith("output_images/test.png")
    assert os.path.exists("output_images")  # Directory should be created
