"""Retry script for Post 4 (video) and Post 5 (AI image)."""
import sys
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.content_generator import generate_post
from src.image_generator import generate_image_for_post
from src.media_manager import resolve_media_url
from src.buffer_client import BufferClient
from src.config import VIDEOS_DIR

client = BufferClient()

# -------------------------------------------------------
# POST 4: Video via gofile.io
# -------------------------------------------------------
print("=" * 60)
print("  POST 4: Video Post (gofile.io CDN)")
print("=" * 60)
try:
    mp4_files = sorted(VIDEOS_DIR.glob("*.mp4"))
    if not mp4_files:
        raise FileNotFoundError("No .mp4 files in assets/videos/")
    mp4 = mp4_files[0]
    print(f"Using: {mp4.name}")

    video_url = resolve_media_url(mp4.name)
    print(f"Resolved URL: {video_url}")

    if not video_url or video_url.startswith("file://"):
        raise ValueError(f"Could not get a public URL for {mp4.name}")

    content = generate_post(
        content_type_preference="single",
        allow_media=True,
        preferred_media_filename=mp4.name,
        planned_focus_topic="How Demoly screen recorder works - intro tutorial for web agencies",
        planned_rationale="Tutorial video demonstration",
    )
    content.media_filename = mp4.name
    content.media_url = video_url

    print(f"Tweet ({len(content.posts[0])} chars): {content.posts[0][:120]}...")
    result = client.publish_single_post(
        text=content.posts[0],
        mode="shareNow",
        media_url=video_url,
    )
    print(f"[PUBLISHED] Buffer ID: {result.get('id')} | Status: {result.get('status')}")

except Exception as e:
    print(f"[FAILED] Video post: {e}")

time.sleep(5)

# -------------------------------------------------------
# POST 5: AI Image via Pollinations.ai
# -------------------------------------------------------
print()
print("=" * 60)
print("  POST 5: AI Image Post (Pollinations.ai)")
print("=" * 60)
try:
    print("Generating AI image...")
    ai_url = generate_image_for_post(
        focus_topic="AI is changing how web agencies deliver projects to clients",
        trend_connection="#AIAgents #BuildInPublic",
    )
    if not ai_url:
        raise ValueError("AI image generation returned no URL")

    print(f"AI Image URL: {ai_url}")

    content = generate_post(
        content_type_preference="single",
        allow_media=True,
        planned_focus_topic="AI is reshaping how agencies deliver projects to clients",
        planned_trend_connection="#AIAgents #BuildInPublic",
        planned_rationale="Trend-first AI image post",
    )
    content.media_filename = None
    content.media_url = ai_url

    print(f"Tweet ({len(content.posts[0])} chars): {content.posts[0][:120]}...")
    result = client.publish_single_post(
        text=content.posts[0],
        mode="shareNow",
        media_url=ai_url,
    )
    print(f"[PUBLISHED] Buffer ID: {result.get('id')} | Status: {result.get('status')}")

except Exception as e:
    print(f"[FAILED] AI image post: {e}")

print()
print("Done! Check your X profile.")
