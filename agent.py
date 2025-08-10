import asyncio

from agents import Agent, Runner, trace
from dotenv import load_dotenv

from tools import create_composite_image, download_x_profile_picture, select_local_image
from utils import build_character_instructions


async def main():
    load_dotenv()

    local_memes = build_character_instructions()

    agent = Agent(
        name="Image generator",
        instructions=f"You are a helpful image generator agent. {local_memes}",
        tools=[
            select_local_image,
            download_x_profile_picture,
            create_composite_image,
        ],
    )

    with trace("Image generation example"):
        print("Generating image, this may take a while...")
        result = await Runner.run(
            agent,
            "generate an image of hosico hugging crybaby in the casino"
            # "generate an image of @iamkadense and @yuzhe_lu in space suits on the moon.",
        )
        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
