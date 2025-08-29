import asyncio

from agents import Agent, ModelSettings, Runner, trace
from dotenv import load_dotenv
from pydantic import BaseModel

from tools import create_composite_image, download_x_profile_picture
from utils import build_prompt_from_tweet


class ImageResult(BaseModel):
    image_path: str
    description: str


def create_image_generation_agent():
    """Create and return a configured image generation agent."""
    classic_memes = {
        "hosico": "@Hosico_on_sol",
        "200m": "@the200m_bonk",
        "crybaby": "@Crybaby_on_sol",
        "bonk": "@bonk_inu",
    }

    classic_meme_info = "\n".join(
        [f"- {key}: twitter handle {value}" for key, value in classic_memes.items()]
    )

    print(f"background info:\n{classic_meme_info}")

    instructions = (
        # task instruction
        "You are a helpful image generator agent. "
        + "Your task is to generate cool, creative visuals based on tweet contents.\n\n"
        # background knowledge
        + "The following is some info on some classic meme characters you should be aware of:\n"
        + f"{classic_meme_info}\n\n"
        # tool instructions: visual context gathering
        + "You are given the following tool to gather visual context:\n"
        + "- download_x_profile_picture: used for downloading the profile picture of "
        + "twitter accounts. when an account is tagged in the tweet, you should invoke "
        + "this tool with the corresponding twitter handle. if you think the tweet author's "
        + "profile picture is needed for the image generation, use this tool with the author's "
        + "tweeter handle too (e.g., generate an image of me playing soccer). when a classic "
        + "meme listed above is mentioned in the tweet, use this tool on the provided twitter handle.\n\n"
        # tool instructions: image generation
        + "You are given the following tool to generate images based on relevant images:\n"
        + "- create_composite_image: it takes in three inputs, image_paths, prompt, and the output file name. "
        + "image_paths and prompt are particularly important so you should think carefully before specifying them. "
        + "image_paths contains paths of images that you think are needed for generating the new image, "
        + "and prompt is a detailed description of how the images in image_paths should be orchestrated. "
        + "since the profile picture can be anything, from persons, animals, to objects, "
        + "you should avoid describing them as persons. instead, refer to images by either file names or their indices "
        + "(first / second image) as in image_paths.\n"
    )

    return Agent(
        name="Image generator",
        model="gpt-4.1",
        model_settings=ModelSettings(temperature=0.6),
        instructions=instructions,
        tools=[
            download_x_profile_picture,
            create_composite_image,
        ],
        output_type=ImageResult,
    )


tweets = [
    "@theuselesscoin eating @ramen_intern",
    "@iamkadense and @solporttom brainstorming in a conference room, while bonk and hosico playing with each other on the table.",
    "@memery_labs create an image of 200m on a mug",
    "@memery_labs create an image of me and @Hosico_on_sol lounging in the couch",
    "create an image of @AnAverageJoeSol being average",
    "create an image of @dapanji_eth wearing a cap with the @the200m_bonk logo.",
    "create an image of @dapanji_eth wearing a grey fleece vest with a @BluechipDotSol logo",
    "@iamkadense and @solporttom work out hard in the gym.",
    "joe petting bonk",
    "hosico flying",
    "make my profile picture cry.",
    "generate an image of @iamkadense crying tears like crybaby",
    "generate an image of @iamkadense wearing a woolen hat like @dogwifcoin",
    "@EricTrump wearing a woolen hat like @dogwifcoin",
    "generate an image of bitcoin price's skyrocketing",
    "generate an image of @dapanji_eth with hosico.",
    "generate an image of @sydney_sweeney with hosico.",
    "generate an image of hosico hugging crybaby in the casino",
    "generate an image of @iamkadense and @yuzhe_lu in space suits on the moon.",
]

author_name, me_name = "Se7e8", "memery_labs"

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
