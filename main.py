import asyncio
import base64
import tempfile
import webbrowser

from agents import Agent, Runner, trace
from dotenv import load_dotenv

from tools import create_composite_image, download_x_profile_picture


def open_file(path: str) -> None:
    webbrowser.open(f"file://{path}")


async def main():  # type: ignore[no-untyped-def]
    load_dotenv()

    agent = Agent(
        name="Image generator",
        instructions="You are a helpful agent.",
        tools=[
            download_x_profile_picture,
            create_composite_image,
        ],
    )

    with trace("Image generation example"):
        print("Generating image, this may take a while...")
        result = await Runner.run(
            agent,
            "generate an image of @iamkadense and @yuzhe_lu in space suits on the moon.",
        )
        print(result.final_output)
        for item in result.new_items:
            if (
                item.type == "tool_call_item"
                and item.raw_item.type == "image_generation_call"
                and (img_result := item.raw_item.result)
            ):
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    tmp.write(base64.b64decode(img_result))
                    temp_path = tmp.name

                # Open the image
                open_file(temp_path)


if __name__ == "__main__":
    asyncio.run(main())
