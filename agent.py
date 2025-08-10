import asyncio

from agents import Agent, Runner, trace
from dotenv import load_dotenv

from tools import create_composite_image, download_x_profile_picture


async def main():
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


if __name__ == "__main__":
    asyncio.run(main())
