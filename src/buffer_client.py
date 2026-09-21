"""
buffer_client.py
================================================================================
Buffer Publishing Layer using the official Buffer GraphQL API (https://api.buffer.com).
Supports:
1. Channel discovery (--list-channels)
2. Single X post creation (queued or share now)
3. X Twitter thread creation using native GraphQL metadata.twitter.thread
================================================================================
"""

import sys
import requests
from typing import List, Dict, Optional, Any

from src.config import (
    BUFFER_ACCESS_TOKEN,
    BUFFER_CHANNEL_ID,
    validate_buffer_config,
)

BUFFER_GRAPHQL_ENDPOINT = "https://api.buffer.com"


class BufferClient:
    """Client wrapper for Buffer's official GraphQL API."""

    def __init__(
        self,
        access_token: Optional[str] = None,
        channel_id: Optional[str] = None,
    ):
        self.access_token = access_token or BUFFER_ACCESS_TOKEN
        self.channel_id = channel_id or BUFFER_CHANNEL_ID

    @property
    def headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "User-Agent": "DemolyXAutomation/1.0",
        }

    def _execute_graphql(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Executes a GraphQL query/mutation against api.buffer.com with error handling."""
        if not self.access_token:
            raise ValueError(
                "[BUFFER ERROR] Missing BUFFER_ACCESS_TOKEN. "
                "Please configure your token in .env or GitHub Secrets."
            )

        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        try:
            response = requests.post(
                BUFFER_GRAPHQL_ENDPOINT,
                headers=self.headers,
                json=payload,
                timeout=30,
            )
        except requests.exceptions.RequestException as net_err:
            raise RuntimeError(f"[BUFFER NETWORK ERROR] Failed to connect to api.buffer.com: {net_err}")

        if response.status_code == 401:
            raise PermissionError(
                "[BUFFER AUTH ERROR] 401 Unauthorized. Your BUFFER_ACCESS_TOKEN is invalid or expired. "
                "Please generate a new personal token at https://buffer.com/developers/api"
            )

        if response.status_code != 200:
            raise RuntimeError(
                f"[BUFFER HTTP ERROR] Server returned HTTP status {response.status_code}: {response.text}"
            )

        data = response.json()
        if "errors" in data and data["errors"]:
            err_messages = "; ".join([e.get("message", "Unknown GraphQL error") for e in data["errors"]])
            raise RuntimeError(f"[BUFFER GRAPHQL ERROR] {err_messages}")

        return data

    def list_channels(self) -> List[Dict[str, Any]]:
        """
        Fetches all organizations and connected social channels.
        Useful for retrieving the Twitter/X channel ID.
        """
        # Step 1: Fetch organization IDs from account
        org_query = """
        query GetOrganizations {
          account {
            organizations {
              id
              name
            }
          }
        }
        """
        org_result = self._execute_graphql(org_query)
        organizations = org_result.get("data", {}).get("account", {}).get("organizations", [])

        if not organizations:
            return []

        # Step 2: Fetch channels for each organization
        channels_query = """
        query GetChannels($input: ChannelsInput!) {
          channels(input: $input) {
            id
            name
            displayName
            service
          }
        }
        """

        all_channels = []
        for org in organizations:
            org_id = org.get("id")
            org_name = org.get("name")
            try:
                ch_result = self._execute_graphql(channels_query, {"input": {"organizationId": org_id}})
                channels = ch_result.get("data", {}).get("channels", [])
                for ch in channels:
                    all_channels.append({
                        "id": ch.get("id"),
                        "name": ch.get("name") or ch.get("displayName"),
                        "service": ch.get("service"),
                        "organization_id": org_id,
                        "organization_name": org_name,
                    })
            except Exception as ch_err:
                print(f"[Buffer Warning] Could not fetch channels for organization '{org_name}': {ch_err}")

        return all_channels


    def _build_assets_payload(self, media_url: Optional[str]) -> Optional[List[Dict[str, Any]]]:
        """Builds the Buffer assets payload for image or video URL."""
        if not media_url:
            return None
        if not (media_url.startswith("http://") or media_url.startswith("https://")):
            print(f"[Buffer Warning] Media URL '{media_url}' is not a public HTTP(S) URL. Skipping attachment for Buffer.")
            return None

        is_video = any(media_url.lower().endswith(ext) for ext in [".mp4", ".webm", ".mov"])
        if is_video:
            return [{"video": {"url": media_url}}]
        return [{"image": {"url": media_url}}]

    def publish_single_post(
        self,
        text: str,
        mode: str = "addToQueue",
        due_at: Optional[str] = None,
        media_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Creates a single post in Buffer for the configured channel.
        Modes: 'addToQueue' (default), 'shareNow', or 'customScheduled' (when due_at is provided).
        """
        validate_buffer_config()

        mutation = """
        mutation CreatePost($input: CreatePostInput!) {
          createPost(input: $input) {
            ... on PostActionSuccess {
              post {
                id
                status
                dueAt
              }
            }
            ... on MutationError {
              message
            }
          }
        }
        """

        input_data = {
            "channelId": self.channel_id,
            "text": text,
            "schedulingType": "automatic",
            "mode": mode,
        }
        if due_at:
            input_data["dueAt"] = due_at
            input_data["mode"] = "customScheduled"

        assets = self._build_assets_payload(media_url)
        if assets:
            input_data["assets"] = assets

        result = self._execute_graphql(mutation, {"input": input_data})
        payload = result.get("data", {}).get("createPost", {})

        if "message" in payload:
            raise RuntimeError(f"[BUFFER POST ERROR] {payload['message']}")

        post = payload.get("post", {})
        return {
            "id": post.get("id", "UNKNOWN_ID"),
            "status": post.get("status", "QUEUED"),
            "due_at": post.get("dueAt"),
        }

    def publish_thread(
        self,
        posts: List[str],
        mode: str = "addToQueue",
        due_at: Optional[str] = None,
        media_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Creates a Twitter thread in Buffer using metadata.twitter.thread.
        """
        validate_buffer_config()

        if not posts:
            raise ValueError("[BUFFER THREAD ERROR] Cannot publish empty thread.")

        mutation = """
        mutation CreateThreadPost($input: CreatePostInput!) {
          createPost(input: $input) {
            ... on PostActionSuccess {
              post {
                id
                status
                dueAt
              }
            }
            ... on MutationError {
              message
            }
          }
        }
        """

        # Format thread entries
        thread_entries = [{"text": p} for p in posts]

        input_data = {
            "channelId": self.channel_id,
            "text": posts[0],  # Root post must match top-level text
            "schedulingType": "automatic",
            "mode": mode,
            "metadata": {
                "twitter": {
                    "thread": thread_entries
                }
            }
        }
        if due_at:
            input_data["dueAt"] = due_at
            input_data["mode"] = "customScheduled"

        assets = self._build_assets_payload(media_url)
        if assets:
            input_data["assets"] = assets
            if thread_entries:
                thread_entries[0]["assets"] = assets

        result = self._execute_graphql(mutation, {"input": input_data})
        payload = result.get("data", {}).get("createPost", {})

        if "message" in payload:
            raise RuntimeError(f"[BUFFER THREAD ERROR] {payload['message']}")

        post = payload.get("post", {})
        return {
            "id": post.get("id", "UNKNOWN_ID"),
            "status": post.get("status", "QUEUED"),
            "due_at": post.get("dueAt"),
        }



def print_available_channels() -> None:
    """Helper CLI function to discover and display connected Buffer channels."""
    print("\n--- Connecting to Buffer GraphQL API to find your channels ---")
    client = BufferClient()
    try:
        channels = client.list_channels()
        if not channels:
            print("[INFO] No social channels found on this Buffer account.")
            print("Please link your Demoly.dev Twitter/X account at https://publish.buffer.com first.")
            return

        print(f"\nFound {len(channels)} connected channel(s):\n")
        print(f"{'CHANNEL ID':<30} | {'SERVICE':<10} | {'ACCOUNT NAME'}")
        print("-" * 65)

        twitter_channels = []
        for ch in channels:
            svc = ch['service']
            name = ch['name']
            cid = ch['id']
            print(f"{cid:<30} | {svc:<10} | {name}")
            if svc and "twitter" in svc.lower():
                twitter_channels.append(ch)

        print("-" * 65)
        if twitter_channels:
            print("\n[RECOMMENDATION] Copy your Twitter Channel ID above and add to your .env:")
            print(f"   BUFFER_CHANNEL_ID={twitter_channels[0]['id']}")
        else:
            print("\n[NOTE] No Twitter/X channel detected. Please connect your X account in Buffer dashboard.")

    except Exception as err:
        print(f"\n[ERROR] Could not fetch channels: {err}")


if __name__ == "__main__":
    if "--list-channels" in sys.argv:
        print_available_channels()
    else:
        print("Buffer Client Module.")
        print("Run with '--list-channels' to list your Buffer channel IDs:")
        print("  python -m src.buffer_client --list-channels")
