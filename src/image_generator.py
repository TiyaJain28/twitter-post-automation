"""
image_generator.py
================================================================================
AI Image & Graphic Generation for Demoly.dev X (Twitter) Automation.

100% Free, Keyless, Self-Contained Visual Generation:

  1. MEME PROMOTION GENERATOR (For Trending Topics & Dev Culture)
     - Automatically triggered when a post references a trending topic or dev pain.
     - Gemini crafts a punchy setup (pain point) and punchline (Demoly solution).
     - Renders standard viral meme formats (Drake, etc.) with demoly.dev branding.

  2. WORKFLOW COMPARISON INFOGRAPHIC (For Technical & Product Posts)
     - Renders a high-contrast dark-mode Before vs After matrix.
     - "Without Demoly" (friction points) vs "With Demoly.dev" (solutions).
     - Never duplicates the tweet text.

All generated assets are saved to assets/generated/ and uploaded to CDN for Buffer ingest.
================================================================================
"""

import os
import re
import json
import time
import textwrap
from pathlib import Path
from typing import Optional, List, Dict, Any

from src.config import GENERATED_IMAGES_DIR

# Ensure generated images and templates directories exist
GENERATED_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR = Path("assets/templates")
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# CDN Upload (uploads generated file to catbox.moe for Buffer ingest)
# ---------------------------------------------------------------------------

def _upload_to_cdn(file_path: Path) -> Optional[str]:
    """Uploads a local image file to catbox.moe CDN and returns the public URL."""
    try:
        import requests
        print(f"[Image Generator] Uploading to CDN: {file_path.name}")
        with open(file_path, "rb") as f:
            res = requests.post(
                "https://catbox.moe/user/api.php",
                data={"reqtype": "fileupload"},
                files={"fileToUpload": f},
                timeout=40,
            )
        if res.status_code == 200 and res.text.strip().startswith("http"):
            url = res.text.strip()
            print(f"[Image Generator] CDN upload successful: {url}")
            return url
        else:
            print(f"[Image Generator Warning] CDN upload unexpected response: {res.text[:200]}")
    except Exception as e:
        print(f"[Image Generator Warning] CDN upload failed: {e}")
    return None


# ---------------------------------------------------------------------------
# Provider 1: Trending Meme Generator (Drake & Viral Templates)
# ---------------------------------------------------------------------------

def generate_drake_meme(top_text: str, bottom_text: str, slug: str) -> Optional[str]:
    """
    Renders a standard Drake Hotline Bling meme with custom captions and demoly.dev branding.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont

        drake_path = TEMPLATES_DIR / "drake.jpg"
        if not drake_path.exists():
            import requests
            r = requests.get("https://i.imgflip.com/30b1gx.jpg", timeout=20)
            drake_path.write_bytes(r.content)

        img = Image.open(drake_path).convert("RGB")
        W, H = img.size
        draw = ImageDraw.Draw(img)

        font_path = "C:\\Windows\\Fonts\\segoeuib.ttf" if os.path.exists("C:\\Windows\\Fonts\\segoeuib.ttf") else "arialbd.ttf"
        try:
            font = ImageFont.truetype(font_path, 28)
            badge_font = ImageFont.truetype(font_path, 18)
        except Exception:
            font = badge_font = ImageFont.load_default()

        # Top rejection text (what developers hate)
        wrapped_top = textwrap.fill(top_text, width=22)
        draw.text((W // 2 + 25, 80), wrapped_top, font=font, fill="#111827")

        # Bottom approval text (Demoly solution)
        wrapped_bottom = textwrap.fill(bottom_text, width=22)
        draw.text((W // 2 + 25, H // 2 + 80), wrapped_bottom, font=font, fill="#111827")

        # Demoly branding badge at bottom-right
        draw.rectangle([W - 160, H - 36, W - 8, H - 8], fill="#7C3AED")
        draw.text((W - 146, H - 32), "demoly.dev", font=badge_font, fill="#FFFFFF")

        timestamp = int(time.time())
        clean_slug = re.sub(r"[^a-z0-9]+", "_", slug.lower())[:35].strip("_")
        filename = f"{timestamp}_meme_{clean_slug}.jpg"
        save_path = GENERATED_IMAGES_DIR / filename
        img.save(save_path)
        print(f"[Image Generator] Generated Drake meme: {save_path.name}")

        return _upload_to_cdn(save_path) or str(save_path)
    except Exception as e:
        print(f"[Image Generator Warning] Failed to render Drake meme: {e}")
        return None


def generate_meme_for_trend(post_text: str, focus_topic: str) -> Optional[str]:
    """
    Uses Gemini to craft a relatable meme punchline linking the trending topic to Demoly.
    """
    try:
        from src.gemini_client import GeminiClient
        gemini = GeminiClient()
        prompt = f"""You are a social media strategist creating a viral tech meme for Demoly (an AI browser screen recorder & client handover platform).
Topic: "{focus_topic}"
Tweet: "{post_text}"

Generate JSON for a Drake meme:
- "top": The frustrating traditional way or annoying developer pain point (rejection text under 50 chars).
- "bottom": The Demoly solution (approval text under 50 chars).

JSON schema:
{{
  "top": "rejection text",
  "bottom": "approval text"
}}
Return ONLY valid JSON."""
        raw = gemini.generate_raw_text(prompt)
        cleaned = re.sub(r"^```json\s*", "", raw, flags=re.MULTILINE)
        cleaned = re.sub(r"^```\s*$", "", cleaned, flags=re.MULTILINE).strip()
        data = json.loads(cleaned)
        top = data.get("top", "Hosting a 45-min Zoom call to explain UI updates")
        bottom = data.get("bottom", "Sending a 15-sec Demoly DOM walkthrough")
        return generate_drake_meme(top, bottom, focus_topic)
    except Exception as e:
        print(f"[Image Generator Warning] Failed to generate meme copy: {e}")
        return None


# ---------------------------------------------------------------------------
# Provider 2: Workflow Comparison Infographic (Before vs After Matrix)
# ---------------------------------------------------------------------------

def _get_comparison_data_from_gemini(post_text: str, focus_topic: str) -> Dict[str, Any]:
    """
    Uses Gemini to generate structured Before vs After comparison points.
    Guarantees the infographic does NOT duplicate the tweet sentences.
    """
    try:
        from src.gemini_client import GeminiClient
        gemini = GeminiClient()
        prompt = f"""You are an expert tech infographic designer for Demoly (an interactive browser screen recording & AI client handover tool for web agencies).
Based on this tweet and topic:
Tweet: "{post_text}"
Topic: "{focus_topic}"

Generate a JSON object for a Before vs After comparison infographic.
CRITICAL RULE: Do NOT repeat the tweet sentences verbatim. Extract 3 specific friction points for the left column, and 3 specific Demoly solutions for the right column.

Return ONLY valid JSON matching this exact structure:
{{
  "headline": "Punchy title under 40 chars",
  "left_title": "Without Demoly",
  "left_points": [
    "Friction point 1 under 45 chars",
    "Friction point 2 under 45 chars",
    "Friction point 3 under 45 chars"
  ],
  "right_title": "With Demoly.dev",
  "right_points": [
    "Solution benefit 1 under 45 chars",
    "Solution benefit 2 under 45 chars",
    "Solution benefit 3 under 45 chars"
  ]
}}"""
        raw = gemini.generate_raw_text(prompt)
        cleaned = re.sub(r"^```json\s*", "", raw, flags=re.MULTILINE)
        cleaned = re.sub(r"^```\s*$", "", cleaned, flags=re.MULTILINE).strip()
        data = json.loads(cleaned)
        if "headline" in data and "left_points" in data and "right_points" in data:
            return data
    except Exception as e:
        print(f"[Image Generator Warning] Gemini comparison generation fallback: {e}")

    # Solid default if LLM JSON fails
    return {
        "headline": "The Client Handover Bottleneck",
        "left_title": "Without Demoly",
        "left_points": [
            "30-min calls explaining basic buttons",
            "Clients forget UI steps after 48h",
            "5+ back-and-forth bug support tickets"
        ],
        "right_title": "With Demoly.dev",
        "right_points": [
            "1-click self-serve interactive replay",
            "Inspect DOM state and live clicks",
            "Zero status calls, 80% fewer tickets"
        ]
    }


def generate_comparison_infographic_card(post_text: str, focus_topic: str) -> Optional[str]:
    """
    Generates a high-resolution (1200x675) dark-mode comparison matrix.
    Adds genuine visual value without repeating the tweet text.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont

        data = _get_comparison_data_from_gemini(post_text, focus_topic)
        headline = data.get("headline", "Workflow Comparison")
        left_title = data.get("left_title", "Without Demoly")
        left_points = data.get("left_points", [])
        right_title = data.get("right_title", "With Demoly.dev")
        right_points = data.get("right_points", [])

        W, H = 1200, 675
        img = Image.new("RGB", (W, H), color="#0A0E1A")
        draw = ImageDraw.Draw(img)

        # Typography setup
        font_path_b = "C:\\Windows\\Fonts\\segoeuib.ttf" if os.path.exists("C:\\Windows\\Fonts\\segoeuib.ttf") else "arialbd.ttf"
        font_path_r = "C:\\Windows\\Fonts\\segoeui.ttf" if os.path.exists("C:\\Windows\\Fonts\\segoeui.ttf") else "arial.ttf"

        try:
            font_badge = ImageFont.truetype(font_path_b, 18)
            font_h1 = ImageFont.truetype(font_path_b, 36)
            font_col_h = ImageFont.truetype(font_path_b, 26)
            font_item = ImageFont.truetype(font_path_r, 22)
            font_symbol = ImageFont.truetype(font_path_b, 24)
            font_footer = ImageFont.truetype(font_path_b, 18)
        except Exception:
            font_badge = font_h1 = font_col_h = font_item = font_symbol = font_footer = ImageFont.load_default()

        # Violet ambient glow in background
        for r in range(120, 0, -6):
            alpha = int(14 * (r / 120))
            draw.ellipse([W - 350 - r, -80 - r, W + 150 + r, 300 + r], outline=(124, 58, 237, alpha))

        # Main Card container
        draw.rounded_rectangle([50, 40, W - 50, H - 40], radius=24, fill="#111827", outline="#1F2937", width=2)

        # Top Badge & Headline
        draw.rounded_rectangle([90, 75, 290, 115], radius=8, fill="#7C3AED")
        draw.text((110, 83), "WORKFLOW COMPARISON", font=font_badge, fill="#FFFFFF")
        draw.text((90, 135), headline, font=font_h1, fill="#F9FAFB")

        # Two Columns: Before vs After
        col_w = 480
        y_top = 210
        box_h = 320

        # Left Column (The Pain / Traditional)
        draw.rounded_rectangle([90, y_top, 90 + col_w, y_top + box_h], radius=16, fill="#1F1622", outline="#5B2136", width=2)
        draw.text((120, y_top + 25), left_title, font=font_col_h, fill="#F87171")

        y = y_top + 80
        for item in left_points[:4]:
            draw.text((120, y), "x", font=font_symbol, fill="#EF4444")
            draw.text((150, y + 2), item, font=font_item, fill="#D1D5DB")
            y += 56

        # Right Column (The Demoly Solution)
        x_right = W - 90 - col_w
        draw.rounded_rectangle([x_right, y_top, x_right + col_w, y_top + box_h], radius=16, fill="#181F38", outline="#4338CA", width=2)
        draw.text((x_right + 30, y_top + 25), right_title, font=font_col_h, fill="#A78BFA")

        y = y_top + 80
        for item in right_points[:4]:
            draw.text((x_right + 30, y), "+", font=font_symbol, fill="#10B981")
            draw.text((x_right + 60, y + 2), item, font=font_item, fill="#E0E7FF")
            y += 56

        # Footer
        draw.line([(90, H - 90), (W - 90, H - 90)], fill="#2A344A", width=1)
        draw.text((90, H - 75), "demoly.dev", font=font_footer, fill="#8B5CF6")
        draw.text((220, H - 75), "|  Interactive Browser Screen Recording for Modern Web Agencies", font=font_item, fill="#6B7280")

        # Save locally
        timestamp = int(time.time())
        slug = re.sub(r"[^a-z0-9]+", "_", focus_topic.lower())[:35].strip("_")
        filename = f"{timestamp}_matrix_{slug}.png"
        save_path = GENERATED_IMAGES_DIR / filename
        img.save(save_path)
        print(f"[Image Generator] Generated comparison infographic: {save_path.name}")

        # Upload to CDN
        return _upload_to_cdn(save_path) or str(save_path)

    except Exception as e:
        print(f"[Image Generator Warning] Failed to generate comparison infographic: {e}")
        return None


# ---------------------------------------------------------------------------
# Format Selector & Main Entry Point
# ---------------------------------------------------------------------------

def _is_trending_or_meme_topic(focus_topic: str, trend_connection: Optional[str], post_text: str) -> bool:
    """
    Evaluates whether the post is based on a trending topic, dev culture humor,
    or viral take that is best served with a meme.
    """
    if trend_connection:
        return True

    text_lower = f"{focus_topic} {post_text}".lower()
    meme_keywords = ["vibe coding", "pov:", "friday deployment", "meme", "drake"]
    return any(k in text_lower for k in meme_keywords)


def generate_image_for_post(
    focus_topic: str,
    trend_connection: Optional[str] = None,
    post_text: Optional[str] = None,
    brand_style: str = "",
) -> Optional[str]:
    """
    Generates a graphic tailored to the post without duplicating the tweet text:
      - Trending Topics & Dev Culture -> Viral Meme with Demoly promotion
      - Product & Technical Topics    -> Workflow Comparison Infographic
    """
    print(f"\n[Image Generator] Generating image for topic: '{focus_topic[:80]}'")
    effective_text = post_text or focus_topic

    if _is_trending_or_meme_topic(focus_topic, trend_connection, effective_text):
        print("[Image Generator] Trending/culture topic detected -> Generating Meme...")
        meme_result = generate_meme_for_trend(effective_text, focus_topic)
        if meme_result:
            return meme_result

    print("[Image Generator] Product/technical topic detected -> Generating Workflow Comparison...")
    return generate_comparison_infographic_card(effective_text, focus_topic)
