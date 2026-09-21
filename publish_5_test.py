"""
publish_5_test.py
================================================================================
Test script: Publishes 5 post types to X (Twitter) via Buffer immediately.

Posts published:
  1. Tweet          — text-only single tweet
  2. Thread         — multi-tweet text thread
  3. Image post     — single tweet with catalog asset image
  4. Video post     — single tweet with catalog asset video
  5. AI Image post  — single tweet with Gemini/Pollinations generated image

Run with:
    python publish_5_test.py
================================================================================
"""

import sys
import time

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.content_generator import generate_post
from src.image_generator import generate_image_for_post
from src.media_manager import load_media_catalog, resolve_media_url
from src.buffer_client import BufferClient
from src.gemini_client import GeneratedPostModel


def banner(title: str):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def publish_post(client: BufferClient, content: GeneratedPostModel, label: str):
    """Publishes a single or thread post immediately and prints result."""
    print(f"\n[{label}] Generating content...")
    print(f"  Type: {content.type.upper()}")
    for i, p in enumerate(content.posts, 1):
        print(f"  Post #{i} ({len(p)} chars): {p[:100]}...")
    if content.media_url:
        print(f"  Media URL: {content.media_url}")

    print(f"[{label}] Publishing to X via Buffer (shareNow)...")

    if content.type == "single":
        result = client.publish_single_post(
            text=content.posts[0],
            mode="shareNow",
            media_url=content.media_url,
        )
    else:
        result = client.publish_thread(
            posts=content.posts,
            mode="shareNow",
            media_url=content.media_url,
        )

    print(f"[{label}] PUBLISHED - Buffer ID: {result.get('id', 'N/A')} | Status: {result.get('status', 'N/A')}")
    return result


def main():
    client = BufferClient()
    catalog = load_media_catalog()
    results = []

    # ------------------------------------------------------------------
    # POST 1: Plain Tweet (text-only, single)
    # ------------------------------------------------------------------
    banner("POST 1/5: Plain Tweet (text-only)")
    try:
        content = generate_post(
            content_type_preference="single",
            allow_media=False,
            planned_focus_topic="Why web agencies waste 40% of handover time on back-and-forth client questions",
            planned_rationale="Sharp insight tweet to grab attention",
        )
        result = publish_post(client, content, "Tweet")
        results.append(("Tweet", result.get("id"), "OK"))
    except Exception as e:
        print(f"[Tweet] FAILED: {e}")
        results.append(("Tweet", None, f"FAILED: {e}"))
    time.sleep(3)

    # ------------------------------------------------------------------
    # POST 2: Thread (text-only, multi-tweet)
    # ------------------------------------------------------------------
    banner("POST 2/5: Thread (text-only)")
    try:
        content = generate_post(
            content_type_preference="thread",
            allow_media=False,
            planned_focus_topic="5 signs your client handover process is broken (and how to fix it with AI)",
            planned_rationale="Deep-dive thread with actionable framework",
        )
        result = publish_post(client, content, "Thread")
        results.append(("Thread", result.get("id"), "OK"))
    except Exception as e:
        print(f"[Thread] FAILED: {e}")
        results.append(("Thread", None, f"FAILED: {e}"))
    time.sleep(3)

    # ------------------------------------------------------------------
    # POST 3: Post with catalog IMAGE asset (img*.png from assets/images/)
    # ------------------------------------------------------------------
    banner("POST 3/5: Post with Catalog Image Asset")
    try:
        from src.config import IMAGES_DIR
        img_files = sorted(IMAGES_DIR.glob("img*.png"))
        if not img_files:
            raise FileNotFoundError("No img*.png files found in assets/images/")

        img_path = img_files[0]
        print(f"[Image Post] Using asset: {img_path.name}")
        img_url = resolve_media_url(img_path.name)
        print(f"[Image Post] Resolved URL: {img_url}")

        if not img_url or img_url.startswith("file://"):
            raise ValueError(f"Could not get a public URL for {img_path.name}")

        content = generate_post(
            content_type_preference="single",
            allow_media=True,
            preferred_media_filename=img_path.name,
            planned_focus_topic="Stop explaining client handovers twice — let AI answer their questions from the recording",
            planned_rationale="Showcasing catalog image asset",
        )
        content.media_filename = img_path.name
        content.media_url = img_url
        result = publish_post(client, content, "Image Post")
        results.append(("Image Post", result.get("id"), "OK"))
    except Exception as e:
        print(f"[Image Post] FAILED: {e}")
        results.append(("Image Post", None, f"FAILED: {e}"))
    time.sleep(3)

    # ------------------------------------------------------------------
    # POST 4: Post with catalog VIDEO asset
    # ------------------------------------------------------------------
    banner("POST 4/5: Post with Catalog Video Asset")
    try:
        from src.config import VIDEOS_DIR
        mp4_files = sorted(VIDEOS_DIR.glob("*.mp4"))
        if not mp4_files:
            raise FileNotFoundError("No .mp4 files found in assets/videos/")

        video_path = mp4_files[0]
        print(f"[Video Post] Using asset: {video_path.name}")
        video_url = resolve_media_url(video_path.name)
        print(f"[Video Post] Resolved URL: {video_url}")

        if not video_url or video_url.startswith("file://"):
            raise ValueError(f"Could not get a public URL for {video_path.name}")

        content = generate_post(
            content_type_preference="single",
            allow_media=True,
            preferred_media_filename=video_path.name,
            planned_focus_topic="How Demoly's browser screen recorder saves agencies hours every week — watch the intro",
            planned_rationale="Tutorial video demonstration post",
        )
        content.media_filename = video_path.name
        content.media_url = video_url
        result = publish_post(client, content, "Video Post")
        results.append(("Video Post", result.get("id"), "OK"))
    except Exception as e:
        print(f"[Video Post] FAILED: {e}")
        results.append(("Video Post", None, f"FAILED: {e}"))
    time.sleep(3)

    # ------------------------------------------------------------------
    # POST 5: Post with AI-Generated Image (Pollinations.ai)
    # ------------------------------------------------------------------
    banner("POST 5/5: Post with AI-Generated Image")
    try:
        print("[AI Image] Generating image via Pollinations.ai (free)...")
        ai_image_url = generate_image_for_post(
            focus_topic="AI is changing how web agencies hand off projects to clients",
            trend_connection="#AIAgents #BuildInPublic",
        )
        if not ai_image_url:
            raise ValueError("AI image generation returned no URL")

        print(f"[AI Image] Generated: {ai_image_url}")
        content = generate_post(
            content_type_preference="single",
            allow_media=True,
            planned_focus_topic="AI is reshaping how agencies deliver projects to clients — from back-and-forth emails to instant interactive walkthroughs",
            planned_trend_connection="#AIAgents #BuildInPublic",
            planned_rationale="Trend-first AI image post",
        )
        content.media_filename = None
        content.media_url = ai_image_url
        result = publish_post(client, content, "AI Image Post")
        results.append(("AI Image Post", result.get("id"), "OK"))
    except Exception as e:
        print(f"[AI Image Post] FAILED: {e}")
        results.append(("AI Image Post", None, f"FAILED: {e}"))

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    banner("ALL 5 POSTS - FINAL SUMMARY")
    for label, bid, status in results:
        icon = "[OK]" if status == "OK" else "[!!]"
        print(f"  {icon} {label}: {bid or status}")
    print("\nCheck your X (Twitter) profile now!")
    print("=" * 60)


if __name__ == "__main__":
    main()
