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

        # Select credentials based on environment
        environment = os.getenv("ENVIRONMENT", "dev").lower()
        if environment == "production":
            access_token = os.getenv("TWITTER_ACCESS_TOKEN")
            access_token_secret = os.getenv("TWITTER_ACCESS_SECRET")
            logger.info("Using production Twitter credentials")
        else:
            access_token = os.getenv("DEV_TWITTER_ACCESS_TOKEN")
            access_token_secret = os.getenv("DEV_TWITTER_ACCESS_SECRET")
            logger.info("Using development Twitter credentials")

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
        bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

        # Select credentials based on environment
        environment = os.getenv("ENVIRONMENT", "dev").lower()
        if environment == "production":
            access_token = os.getenv("TWITTER_ACCESS_TOKEN")
            access_token_secret = os.getenv("TWITTER_ACCESS_SECRET")
        else:
            access_token = os.getenv("DEV_TWITTER_ACCESS_TOKEN")
            access_token_secret = os.getenv("DEV_TWITTER_ACCESS_SECRET")

        client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            wait_on_rate_limit=True,
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

    def get_me(self):
        if not hasattr(self, "_me"):
            self._me = self.client.get_me()
        return self._me

    def get_mentions(
        self, since_id: str | None = None, limit: int = 100
    ) -> list:  # type: ignore[type-arg]
        """Get recent mentions using Twitter API v2."""
        try:
            # Use v2 API to get mentions
            me_id = self.get_me().data.id
            mentions = self.client.get_users_mentions(
                id=me_id,
                since_id=since_id,
                max_results=max(5, min(limit, 100)),  # v2 API requires 5-100
                tweet_fields=[
                    "author_id",
                    "created_at",
                    "text",
                    "in_reply_to_user_id",
                    "referenced_tweets",
                ],
            )

            if mentions.data:
                # Filter out replies - only keep main tweets (where in_reply_to_user_id is None)
                # An edge case is that when the tweet starts with a tag, the tweet will be considered
                # a reply even if it's a standalone tweet, e.g. "@memery_labs, create an image of ..."
                # in this case, mention.in_reply_to_user_id will be the same as me_id
                main_tweet_mentions = [
                    mention
                    for mention in mentions.data
                    # defensive measure to filter out self-tagging
                    if mention.author_id != me_id
                    and (
                        # only allow standalone tweet
                        not hasattr(mention, "in_reply_to_user_id")
                        or mention.in_reply_to_user_id is None
                        # including standalone tweet starting with the tag
                        or (
                            mention.referenced_tweets is None
                            and mention.in_reply_to_user_id == me_id
                        )
                    )
                ]
                return main_tweet_mentions[:limit]
            else:
                return []

        except Exception as e:
            logger.error(f"Error fetching mentions: {e}")
            return []

    def reply_with_media(
        self,
        mention_id: int,
        username: str,
        media_path: str,
        custom_text: str | None = None,
    ) -> None:
        """Reply to a mention with an media using v2 API."""
        try:
            # Upload the media using v1.1 API (only way to upload media)
            media = self.api.media_upload(media_path)

            # Create reply text (empty if no custom text specified)
            reply_text = custom_text if custom_text else ""

            # Post the reply using v2 API
            self.client.create_tweet(
                text=reply_text,
                in_reply_to_tweet_id=mention_id,
                media_ids=[media.media_id],
            )

            logger.info(f"Posted reply with media to @{username}")

        except Exception as e:
            logger.error(f"Error posting reply with media: {e}")
            raise

    def upload_media(self, media_path: str):
        """Upload media to Twitter and return media object."""
        try:
            return self.api.media_upload(media_path)
        except Exception as e:
            logger.error(f"Error uploading media: {e}")
            raise
