import os
from tools import _create_composite_image_impl


def test_create_composite_image():
    result = _create_composite_image_impl(
        prompt="place two characters in space suit in the space.",
        image_paths=[
            "profile_pics/iamkadense_profile.jpg",
            "profile_pics/yuzhe_lu_profile.jpg"
        ]
    )

    assert result == True, 'image generation failed.'