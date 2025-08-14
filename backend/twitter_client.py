import logging
import os

import tweepy
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class TwitterClient:
    """Shared Twitter API client with authentication and common utilities."""

    def __init__(self):
        self.api = self._setup_twitter_api()
        self.client = self._setup_twitter_client_v2()

    def _setup_twitter_api(self) -> tweepy.API:
        """Setup Twitter API v1.1 client for media uploads."""
        api_key = os.getenv("TWITTER_API_KEY")
        api_secret = os.getenv("TWITTER_API_SECRET")
        access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        access_token_secret = os.getenv("TWITTER_ACCESS_SECRET")

        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)

        api = tweepy.API(auth, wait_on_rate_limit=True)

        try:
            api.verify_credentials()
            logger.info("Twitter API v1.1 authentication successful")
        except Exception as e:
            logger.warning(f"Twitter API v1.1 authentication failed: {e}")

        return api

    def _setup_twitter_client_v2(self) -> tweepy.Client:
        """Setup Twitter API v2 client with full authentication."""
        api_key = os.getenv("TWITTER_API_KEY")
        api_secret = os.getenv("TWITTER_API_SECRET")
        access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        access_token_secret = os.getenv("TWITTER_ACCESS_SECRET")
        bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

        client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
        )

        try:
            # Test the connection
            me = client.get_me()
            logger.info(
                f"Twitter API v2 authentication successful for @{me.data.username}"
            )
        except Exception as e:
            logger.warning(f"Twitter API v2 authentication failed: {e}")

        return client

    def get_mentions(
        self, since_id: str | None = None, limit: int = 100
    ) -> list:  # type: ignore[type-arg]
        """Get recent mentions using Twitter API v2."""
        try:
            # Use v2 API to get mentions
            mentions = self.client.get_users_mentions(
                id=self.client.get_me().data.id,
                since_id=since_id,
                max_results=max(5, min(limit, 100)),  # v2 API requires 5-100
                tweet_fields=["author_id", "created_at", "text"],
            )

            if mentions.data:
                return list(mentions.data)[:limit]
            else:
                return []

        except Exception as e:
            logger.error(f"Error fetching mentions: {e}")
            return []

    def reply_with_image(
        self,
        mention_id: int,
        username: str,
        image_path: str,
        custom_text: str | None = None,
    ) -> None:
        """Reply to a mention with an image using v2 API."""
        try:
            # Upload the image using v1.1 API (only way to upload media)
            media = self.api.media_upload(image_path)

            # Create reply text
            if custom_text:
                reply_text = custom_text
            else:
                reply_text = "Here's your space adventure! 🚀👨‍🚀"

            # Post the reply using v2 API
            self.client.create_tweet(
                text=reply_text,
                in_reply_to_tweet_id=mention_id,
                media_ids=[media.media_id],
            )

            logger.info(f"Posted reply with image to @{username}")

        except Exception as e:
            logger.error(f"Error posting reply with image: {e}")
            raise

    def upload_media(self, image_path: str):
        """Upload media to Twitter and return media object."""
        try:
            return self.api.media_upload(image_path)
        except Exception as e:
            logger.error(f"Error uploading media: {e}")
            raise
