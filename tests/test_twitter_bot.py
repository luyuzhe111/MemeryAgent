import logging
import os

from backend.twitter_client import TwitterClient

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TestBot(TwitterClient):
    """Test bot for immediate testing without polling delays."""

    def __init__(self):
        super().__init__()
        self.test_media_dir = os.path.join(os.path.dirname(__file__), "test_media")

    def test_reply_to_recent_mentions(
        self, limit: int = 1, fname: str = "moon_astronauts.png"
    ):
        """Test by replying to recent mentions with the astronaut image/video."""
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
                media_path = os.path.join(self.test_media_dir, fname)

                if os.path.exists(media_path):
                    self.reply_with_media(mention_id, "user", media_path)
                    logger.info(f"✅ Successfully replied to mention {mention_id}")
                else:
                    logger.error(f"❌ Astronaut media not found at {media_path}")

            logger.info("Test completed!")

        except Exception as e:
            logger.error(f"Error in test: {e}")

    def test_media_upload(self, fname):
        """Test uploading the astronaut image without posting a tweet."""
        try:
            media_path = os.path.join(self.test_media_dir, fname)

            if not os.path.exists(media_path):
                logger.error(f"media not found at {media_path}")
                return

            logger.info("Testing media upload...")
            media = self.upload_media(media_path)
            logger.info(f"✅ media upload successful! Media ID: {media.media_id}")

        except Exception as e:
            logger.error(f"❌ media upload failed: {e}")


def main():
    """Main function to run tests."""
    print("🤖 Twitter Bot Test Script")
    print("=" * 40)

    try:
        bot = TestBot()

        for fname in ["moon_astronauts.png", "hosico_bonk_scooter_night_video.mp4"]:
            # Test 1: Image upload
            print(f"\n1. Testing media ({fname}) upload...")
            bot.test_media_upload(fname)

            # Test 2: Reply to recent mentions
            print("\n2. Testing replies to recent mentions...")
            confirm = input(
                "This will reply to your recent mentions with the astronaut image. Continue? (y/N): "
            )

            if confirm.lower() == "y":
                bot.test_reply_to_recent_mentions(
                    limit=1, fname=fname
                )  # Start with just 1 mention
            else:
                print("Skipped mention replies test.")

            print("\n✅ Test completed!")

    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"\n❌ Test failed: {e}")


if __name__ == "__main__":
    main()
