import shutil

from tools.image_generation import add_watermark


def test_add_watermark() -> None:
    # Copy test image to output directory for watermarking
    input_path = "tests/test_images/moon_astronauts.png"
    output_path = "output_images/moon_astronauts_watermarked.png"

    # Copy the test image to output location
    shutil.copy(input_path, output_path)

    # Add watermark
    result = add_watermark(output_path)

    assert result, "watermark addition failed."
    print(f"Watermarked image saved to: {output_path}")
