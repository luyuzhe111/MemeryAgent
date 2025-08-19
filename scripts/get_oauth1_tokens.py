#!/usr/bin/env python3
"""
OAuth 1.0a script to get access tokens for test account.
"""
import os

import tweepy
from dotenv import load_dotenv

load_dotenv()


def get_oauth1_tokens():
    # Your main app's credentials (memery_labs app)
    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")

    if not api_key or not api_secret:
        print("Error: TWITTER_API_KEY and TWITTER_API_SECRET must be set in .env")
        return

    # Step 1: Get request token and authorization URL
    auth = tweepy.OAuthHandler(api_key, api_secret)

    try:
        # Get the authorization URL
        redirect_url = auth.get_authorization_url()

        print("\n" + "=" * 80)
        print("STEP 1: Open this URL in your browser")
        print("Make sure you're logged into your TEST ACCOUNT")
        print("=" * 80)
        print(redirect_url)
        print("=" * 80)

        # Step 2: Get PIN from user
        verifier = input("\nAfter authorizing, enter the PIN/verifier code: ").strip()

        # Step 3: Get access tokens
        auth.get_access_token(verifier)

        print("\n" + "=" * 60)
        print("SUCCESS! Add these to your .env file:")
        print("=" * 60)
        print(f"DEV_TWITTER_ACCESS_TOKEN={auth.access_token}")
        print(f"DEV_TWITTER_ACCESS_SECRET={auth.access_token_secret}")
        print("=" * 60)

        # Step 4: Verify it works
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=auth.access_token,
            access_token_secret=auth.access_token_secret,
        )

        me = client.get_me()
        print(f"\n✅ Verified! This will authenticate as: @{me.data.username}")
        print("These tokens never expire - much simpler than OAuth 2.0!")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    get_oauth1_tokens()
