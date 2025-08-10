import logging
import os

from twitter_client import TwitterClient

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TestBot(TwitterClient):
    """Test bot for immediate testing without polling delays."""

    def __init__(self):
        super().__init__()
        self.test_image_dir = os.path.join(os.path.dirname(__file__), "test_images")

    def test_reply_to_recent_mentions(self, limit: int = 1):
        """Test by replying to recent mentions with the astronaut image."""
        try:
            logger.info(f"Fetching up to {limit} recent mentions for testing...")

            mentions_list = self.get_mentions(limit=limit)

            if not mentions_list:
                logger.info("No recent mentions found to test with")
                return

            logger.info(f"Found {len(mentions_list)} recent mentions")

            # Process each mention
            for i, mention in enumerate(mentions_list, 1):
                # v2 API response format is different
                tweet_text = mention.text
                mention_id = mention.id

                logger.info(
                    f"[{i}/{len(mentions_list)}] Processing mention {mention_id}: {tweet_text}"
                )

                # Use the astronaut image from test_image_dir
                image_path = os.path.join(self.test_image_dir, "moon_astronauts.png")

                if os.path.exists(image_path):
                    self.reply_with_image(mention_id, "user", image_path)
                    logger.info(f"✅ Successfully replied to mention {mention_id}")
                else:
                    logger.error(f"❌ Astronaut image not found at {image_path}")

            logger.info("Test completed!")

        except Exception as e:
            logger.error(f"Error in test: {e}")

    def test_image_upload(self):
        """Test uploading the astronaut image without posting a tweet."""
        try:
            image_path = os.path.join(self.test_image_dir, "moon_astronauts.png")

            if not os.path.exists(image_path):
                logger.error(f"Astronaut image not found at {image_path}")
                return

            logger.info("Testing image upload...")
            media = self.upload_media(image_path)
            logger.info(f"✅ Image upload successful! Media ID: {media.media_id}")

        except Exception as e:
            logger.error(f"❌ Image upload failed: {e}")


def main():
    """Main function to run tests."""
    print("🤖 Twitter Bot Test Script")
    print("=" * 40)

    try:
        bot = TestBot()

        # Test 1: Image upload
        print("\n1. Testing image upload...")
        bot.test_image_upload()

        # Test 2: Reply to recent mentions
        print("\n2. Testing replies to recent mentions...")
        confirm = input(
            "This will reply to your recent mentions with the astronaut image. Continue? (y/N): "
        )

        if confirm.lower() == "y":
            bot.test_reply_to_recent_mentions(limit=1)  # Start with just 1 mention
        else:
            print("Skipped mention replies test.")

        print("\n✅ Test completed!")

    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"\n❌ Test failed: {e}")


if __name__ == "__main__":
    main()
