import pytest
from dotenv import load_dotenv

from tools.video_generation import _image_to_video_generation_impl

load_dotenv()


@pytest.mark.asyncio
async def test_image_to_video_generation() -> None:
    result = await _image_to_video_generation_impl(
        image_path="assets/examples/trenches.jpeg",
        output_file="output_videos/test_trenches_video.mp4",
    )

    assert result, "video generation failed."
