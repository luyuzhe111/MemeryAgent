import pytest
from dotenv import load_dotenv

from tools.image_generation import _create_composite_image_impl

# Load environment variables from .env file
load_dotenv()


@pytest.mark.asyncio
async def test_create_composite_image() -> None:
    result = await _create_composite_image_impl(
        prompt="place two characters in space suit in the space.",
        image_paths=[
            "profile_pics/iamkadense_profile.jpg",
            "profile_pics/yuzhe_lu_profile.jpg",
        ],
    )

    assert result, "image generation failed."
