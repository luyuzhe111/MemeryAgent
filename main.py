import asyncio
import logging
import os
import time

from agents import Agent, Runner, trace

from backend.database.models import BotState, ProcessedMention
from backend.twitter_client import TwitterClient
from tools import create_composite_image, download_x_profile_picture, select_local_image
from utils import build_character_instructions

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TwitterBot(TwitterClient):
    def __init__(self):
        super().__init__()
        self.poll_interval = 90  # 90 seconds

        # Initialize database models
        self.processed_mentions = ProcessedMention()
        self.bot_state = BotState()

        # Load last mention ID from database
        self.last_mention_id = self.bot_state.get_last_mention_id()
        if self.last_mention_id:
            logger.info(f"Loaded last mention ID from database: {self.last_mention_id}")
        else:
            logger.info("No previous mention ID found in database")

        # Initialize image generation agent
        self._setup_image_agent()

    def _setup_image_agent(self):
        """Initialize the OpenAI agent for image generation."""
        try:
            local_memes = build_character_instructions()

            instructions = (
                "You are a helpful image generator agent.\n"
                + f"- {local_memes}.\n"
                + "Tool Use Requirements:\n"
                + "- use the download_x_profile_picture tool only "
                + "when the prompt contains X (Twitter) username such as @elonmusk.\n"
                + "- use select_local_image tool when you decide a local meme image is needed."
            )

            self.image_agent = Agent(
                name="Image generator",
                instructions=instructions,
                tools=[
                    select_local_image,
                    download_x_profile_picture,
                    create_composite_image,
                ],
            )
            logger.info("Image generation agent initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize image agent: {e}")
            self.image_agent = None

    def start_polling(self):
        """Start the main polling loop that checks for mentions every 90 seconds."""
        logger.info(
            f"Starting Twitter bot with {self.poll_interval}-second polling interval..."
        )

        while True:
            try:
                self.check_and_process_mentions()
                logger.info(f"Waiting {self.poll_interval} seconds until next check...")
                time.sleep(self.poll_interval)

            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                time.sleep(30)  # Wait 30 seconds before retrying on error

    def check_and_process_mentions(self):
        """Check for new mentions and process them."""
        try:
            # Use inherited method from TwitterClient
            mentions_list = self.get_mentions(since_id=self.last_mention_id, limit=10)

            if not mentions_list:
                logger.info("No new mentions found")
                return

            logger.info(f"Found {len(mentions_list)} new mentions")

            # Process mentions (newest first due to cursor order)
            for mention in reversed(mentions_list):
                # Skip if already processed
                if self.processed_mentions.is_processed(mention.id):
                    logger.info(f"Skipping already processed mention {mention.id}")
                    continue

                self.process_mention(mention)

            # Update the last processed mention ID to the newest mention
            if mentions_list:
                self.last_mention_id = mentions_list[0].id
                # Persist to database
                if self.last_mention_id:
                    self.bot_state.set_last_mention_id(self.last_mention_id)
                logger.info(
                    f"Saved last mention ID to database: {self.last_mention_id}"
                )

        except Exception as e:
            logger.error(f"Error checking mentions: {e}")

    def process_mention(self, mention):
        """Process a single mention by creating async task for image generation."""
        try:
            # Get user info from author_id
            user = self.client.get_user(id=mention.author_id)
            username = user.data.username
            tweet_text = mention.text

            logger.info(f"Processing mention from @{username}: {tweet_text}")

            # Mark as processing immediately to avoid duplicate processing
            self.processed_mentions.mark_as_processed(
                mention_id=mention.id,
                username=username,
                tweet_text=tweet_text,
                image_path="processing",  # Placeholder status
            )

            # Create async task for image generation
            asyncio.create_task(self._generate_and_reply_async(mention))

        except Exception as e:
            logger.error(f"Error processing mention {mention.id}: {e}")

    async def _generate_and_reply_async(self, mention):
        """Background async function to generate image and reply."""
        try:
            # Get user info again for the async context
            user = self.client.get_user(id=mention.author_id)
            username = user.data.username

            # Generate image using async agent
            image_path = await self.generate_response_image_async(mention)

            if image_path and os.path.exists(image_path):
                # Reply with image
                self.reply_with_image(mention.id, username, image_path)
                logger.info(f"Successfully replied to @{username}")

                # Update database with final image path
                self._update_processed_mention(mention.id, image_path)

                # Update bot statistics
                self.bot_state.increment_processed_count()

            else:
                logger.error(f"Failed to generate image for mention {mention.id}")
                # Update status to indicate failure
                self._update_processed_mention(mention.id, None)

        except Exception as e:
            logger.error(f"Async processing failed for mention {mention.id}: {e}")
            # Mark as failed
            self._update_processed_mention(mention.id, None)

    def _update_processed_mention(self, mention_id: str, image_path: str | None):
        """Update an already processed mention with final image path."""
        try:
            # Update the existing record with final image path
            self.processed_mentions.collection.update_one(
                {"mention_id": mention_id},
                {
                    "$set": {
                        "image_path": image_path,
                        "status": "completed" if image_path else "failed",
                    }
                },
            )
        except Exception as e:
            logger.error(f"Error updating processed mention {mention_id}: {e}")

    async def generate_response_image_async(self, mention) -> str | None:
        """Generate an AI image based on the mention content using OpenAI agent."""
        try:
            if not self.image_agent:
                logger.error("Image agent not initialized")
                return None

            # Extract username from mention
            user = self.client.get_user(id=mention.author_id)
            username = user.data.username

            # Create prompt from mention
            prompt = f"generate an image of @{username} {mention.text}"
            logger.info(f"Generating image with prompt: {prompt}")

            # Generate image using agent
            with trace("Twitter mention image generation"):
                result = await Runner.run(self.image_agent, prompt)

            # Extract image path from result
            if hasattr(result, "final_output") and result.final_output:
                logger.info(f"Image generation completed: {result.final_output}")
                return self._extract_image_path_from_result(result)
            else:
                logger.error("No output from image generation agent")
                return None

        except Exception as e:
            logger.error(f"Error generating response image: {e}")
            return None

    def _extract_image_path_from_result(self, result) -> str | None:
        """Extract the generated image path from agent result."""
        try:
            # This will depend on how your agent returns the image path
            # For now, assuming the final_output contains the path
            if hasattr(result, "final_output"):
                output = result.final_output
                # You may need to parse this based on your agent's output format
                if (
                    output
                    and isinstance(output, str)
                    and output.endswith((".png", ".jpg", ".jpeg"))
                ):
                    return output
                logger.warning(f"Could not extract image path from result: {output}")
            return None
        except Exception as e:
            logger.error(f"Error extracting image path: {e}")
            return None


if __name__ == "__main__":
    bot = TwitterBot()
    bot.start_polling()
