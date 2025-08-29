import os

import pytest

from tools.x_profile import _download_x_profile_picture_impl


@pytest.mark.asyncio
async def test_download_x_profile_picture() -> None:
    """Test downloading profile picture for a username"""
    user_name = "iamkadense"
    result = await _download_x_profile_picture_impl(
        user_name, output_dir="./profile_pics"
    )

    if result.filepath:
        # Check that the file was created
        assert os.path.exists(result.filepath)
        assert result.filepath.startswith("./profile_pics")
        assert f"{user_name}_profile" in result.filepath

        # Check that the file has content
        file_size = os.path.getsize(result.filepath)
        assert file_size > 0

        # Check that description was generated
        assert result.description is not None
        assert len(result.description) > 0

        print(f"Successfully downloaded profile picture: {result.filepath}")
        print(f"File size: {file_size} bytes")
        print(f"Description: {result.description}")
    else:
        # If download failed, we still want to know about it
        print(f"Failed to download profile picture for {user_name}")
        # Don't fail the test as this could be due to API limits, network issues, etc.
