import asyncio

from agents import Agent, Runner, trace
from dotenv import load_dotenv
from pydantic import BaseModel

from tools import create_composite_image, download_x_profile_picture, select_local_image
from utils import build_character_instructions, build_prompt_from_tweet


class ImageResult(BaseModel):
    image_path: str
    description: str


def create_image_generation_agent():
    """Create and return a configured image generation agent."""
    local_memes = build_character_instructions()

    instructions = (
        "You are a helpful image generator agent.\n"
        + f"- {local_memes}.\n"
        + "Tool Use Requirements:\n"
        + "- use the download_x_profile_picture tool only "
        + "when the prompt contains X (Twitter) username such as @elonmusk.\n"
        + "- use select_local_image tool when you decide a local meme image is needed."
    )

    return Agent(
        name="Image generator",
        instructions=instructions,
        tools=[
            select_local_image,
            download_x_profile_picture,
            create_composite_image,
        ],
        output_type=ImageResult,
    )


tweets = [
    "make my profile picture cry.",
    "generate an image of @iamkadense crying tears like crybaby",
    "generate an image of @iamkadense wearing a woolen hat like @dogwifcoin",
    "generate an image of @EricTrump wearing a woolen hat like @dogwifcoin",
    "generate an image of bitcoin price's skyrocketing",
    "generate an image of @dapanji_eth with hosico.",
    "generate an image of @sydney_sweeney with hosico.",
    "generate an image of hosico hugging crybaby in the casino",
    "generate an image of @iamkadense and @yuzhe_lu in space suits on the moon.",
]

author_name, me_name = "yuzhe_lu", "MemeryBot"

prompts = [build_prompt_from_tweet(t, author_name, me_name) for t in tweets]


async def main():
    load_dotenv()

    agent = create_image_generation_agent()
    print(agent.instructions)

    with trace("Image generation example"):
        print("Generating image, this may take a while...")
        prompt = prompts[0]
        print(f"prompt:\n{prompt}")
        result = await Runner.run(agent, prompt)
        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
