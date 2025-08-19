#!/usr/bin/env python3
"""
OAuth 2.0 script to get access tokens for test account.
Run this script and follow the instructions.
"""
import base64
import hashlib
import os
import secrets
import urllib.parse

import requests
from dotenv import load_dotenv

load_dotenv()


def generate_pkce_pair():
    """Generate PKCE code verifier and challenge."""
    code_verifier = (
        base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("utf-8").rstrip("=")
    )
    code_challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode("utf-8")).digest())
        .decode("utf-8")
        .rstrip("=")
    )
    return code_verifier, code_challenge


def get_oauth2_tokens():
    client_id = os.getenv("TWITTER_CLIENT_ID")
    client_secret = os.getenv("TWITTER_CLIENT_SECRET")

    if not client_id:
        print("Error: TWITTER_CLIENT_ID must be set in .env")
        return

    # Generate PKCE pair
    code_verifier, code_challenge = generate_pkce_pair()

    # Step 1: Build authorization URL
    redirect_uri = (
        "http://localhost:8080/callback"  # You need to add this to your app settings
    )
    state = secrets.token_urlsafe(32)

    auth_params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": "tweet.read tweet.write users.read offline.access",
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }

    auth_url = "https://twitter.com/i/oauth2/authorize?" + urllib.parse.urlencode(
        auth_params
    )

    print("\n" + "=" * 80)
    print("STEP 1: Add this redirect URI to your Twitter app settings:")
    print("Go to your app -> App settings -> Authentication settings")
    print("Add this as a Callback URI:")
    print(f"{redirect_uri}")
    print("=" * 80)

    input("Press Enter after adding the callback URI...")

    print("\n" + "=" * 80)
    print("STEP 2: Open this URL in your browser")
    print("Make sure you're logged into your TEST ACCOUNT")
    print("=" * 80)
    print(auth_url)
    print("=" * 80)

    # Step 2: Get authorization code from user
    print(
        "\nAfter authorizing, you'll be redirected to localhost:8080/callback?code=..."
    )
    print("Copy the 'code' parameter from the URL")
    auth_code = input("Enter the authorization code: ").strip()

    # Step 3: Exchange code for tokens
    token_url = "https://api.twitter.com/2/oauth2/token"

    token_data = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "code": auth_code,
        "code_verifier": code_verifier,
    }

    # Add client secret if available (for confidential clients)
    if client_secret:
        auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        headers = {"Authorization": f"Basic {auth_header}"}
    else:
        headers = {}

    try:
        response = requests.post(token_url, data=token_data, headers=headers)
        response.raise_for_status()
        tokens = response.json()

        print("\n" + "=" * 50)
        print("SUCCESS! Add these to your .env file:")
        print("=" * 50)
        print(f"DEV_TWITTER_ACCESS_TOKEN={tokens['access_token']}")
        if "refresh_token" in tokens:
            print(f"DEV_TWITTER_REFRESH_TOKEN={tokens['refresh_token']}")
        print("=" * 50)

        # Note: OAuth 2.0 tokens work differently with tweepy
        print(
            "\nNOTE: You'll need to update your code to use OAuth 2.0 tokens properly"
        )

    except requests.exceptions.RequestException as e:
        print(f"Error getting tokens: {e}")
        if hasattr(e, "response") and e.response:
            print(f"Response: {e.response.text}")


if __name__ == "__main__":
    get_oauth2_tokens()
