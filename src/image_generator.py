"""
image_generator.py
================================================================================
AI Image Generation for Demoly.dev X (Twitter) Automation.

Uses a multi-provider chain — tries free services first, paid as last resort:

  PROVIDER 1 — Pollinations.ai (100% FREE, no API key needed)
    - Simple HTTP GET: https://image.pollinations.ai/prompt/{prompt}
    - Uses Flux model, supports 1280x720 landscape (perfect for X/Twitter)
    - Returns a direct public image URL — no upload needed!

  PROVIDER 2 — Hugging Face Inference API (FREE tier, free API key)
    - Uses SDXL or similar model via HF Inference API
    - Set HF_API_KEY in .env for this to work
    - Generated image is uploaded to catbox.moe CDN

  PROVIDER 3 — Gemini Imagen (PAID, existing Gemini key)
    - Requires a paid Google AI plan
    - Falls back to this only if both above providers fail

Generated images are saved to assets/generated/ for audit and re-use.
================================================================================
"""

import re
import time
import urllib.parse
from pathlib import Path
from typing import Optional
import os

from src.config import GEMINI_API_KEY, GENERATED_IMAGES_DIR, validate_gemini_config

# Optional: free Hugging Face API key (set in .env as HF_API_KEY)
HF_API_KEY = os.getenv("HF_API_KEY", "").strip()

# Ensure generated images directory exists
GENERATED_IMAGES_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Prompt Builder
# ---------------------------------------------------------------------------

def _build_image_prompt(focus_topic: str, trend_connection: Optional[str], brand_style: str = "") -> str:
    """
    Constructs a detailed image generation prompt for on-brand Demoly visuals.
    """
    trend_note = (
        f", subtly referencing the trending topic: {trend_connection}"
        if trend_connection
        else ""
    )
    style_note = brand_style or (
        "clean minimal tech SaaS aesthetic, dark background, purple violet accent gradients, "
        "modern UI mockup style, professional, no clutter, premium and tech-forward"
    )
    prompt = (
        f"professional social media image for Demoly SaaS browser screen recorder and AI client handover tool"
        f"{trend_note}, topic: {focus_topic}, "
        f"style: {style_note}, "
        f"no text overlays, no watermarks, 16:9 landscape"
    )
    return prompt


# ---------------------------------------------------------------------------
# CDN Upload (for providers that return bytes, not a URL)
# ---------------------------------------------------------------------------

def _upload_to_cdn(file_path: Path) -> Optional[str]:
    """
    Uploads a local file to catbox.moe CDN and returns the public URL.
    """
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


def _save_and_upload(image_bytes: bytes, focus_topic: str) -> Optional[str]:
    """Saves bytes to assets/generated/, uploads to CDN, returns public URL."""
    slug = re.sub(r"[^a-z0-9]+", "_", focus_topic.lower())[:40].strip("_")
    timestamp = int(time.time())
    filename = f"{timestamp}_{slug}.png"
    save_path = GENERATED_IMAGES_DIR / filename
    save_path.write_bytes(image_bytes)
    print(f"[Image Generator] Saved: {save_path}")
    return _upload_to_cdn(save_path) or str(save_path)


# ---------------------------------------------------------------------------
# Provider 1: Pollinations.ai — FREE, no key needed
# ---------------------------------------------------------------------------

def _generate_via_pollinations(prompt: str) -> Optional[str]:
    """
    Generates an image using Pollinations.ai (100% free, no API key).
    Returns the direct public image URL (no upload needed).
    Saves a local copy to assets/generated/ for audit.
    Retries up to 3 times on server errors.
    """
    import requests

    encoded_prompt = urllib.parse.quote(prompt)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?model=flux&width=1280&height=720&seed={int(time.time()) % 9999}&nologo=true"
    )
    print(f"[Image Generator] [Provider: Pollinations.ai] Generating image...")

    for attempt in range(1, 4):
        try:
            res = requests.get(url, timeout=90, stream=True)
            if res.status_code == 200 and "image" in res.headers.get("Content-Type", ""):
                image_bytes = res.content
                # Save locally for audit
                slug = re.sub(r"[^a-z0-9]+", "_", prompt[:40].lower()).strip("_")
                filename = f"{int(time.time())}_pollinations_{slug}.png"
                save_path = GENERATED_IMAGES_DIR / filename
                save_path.write_bytes(image_bytes)
                print(f"[Image Generator] Saved local copy: {save_path.name}")

                # Upload saved file to CDN so Buffer gets a stable URL
                cdn_url = _upload_to_cdn(save_path)
                if cdn_url:
                    return cdn_url

                # Fallback: use the Pollinations URL directly
                print(f"[Image Generator] Using Pollinations direct URL as fallback.")
                return url
            else:
                print(f"[Image Generator] Pollinations attempt {attempt}/3 returned status {res.status_code}. Retrying in 8s...")
                if attempt < 3:
                    time.sleep(8)
        except Exception as e:
            print(f"[Image Generator] Pollinations attempt {attempt}/3 failed: {e}. Retrying in 8s...")
            if attempt < 3:
                time.sleep(8)

    print(f"[Image Generator] Pollinations failed after 3 attempts.")
    return None


# ---------------------------------------------------------------------------
# Provider 2: Hugging Face Inference API — FREE tier, requires free key
# ---------------------------------------------------------------------------

def _generate_via_huggingface(prompt: str, focus_topic: str) -> Optional[str]:
    """
    Generates an image using Hugging Face Inference API (free tier).
    Requires HF_API_KEY in .env (get one free at huggingface.co).
    """
    if not HF_API_KEY:
        print("[Image Generator] Hugging Face: HF_API_KEY not set, skipping.")
        return None

    import requests

    # SDXL is high quality and available on free HF inference API
    HF_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
    api_url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {
        "inputs": prompt,
        "parameters": {"width": 1280, "height": 720},
    }

    print(f"[Image Generator] [Provider: Hugging Face / {HF_MODEL}] Generating image...")
    try:
        res = requests.post(api_url, headers=headers, json=payload, timeout=120)
        if res.status_code == 200 and res.content:
            return _save_and_upload(res.content, focus_topic)
        else:
            print(f"[Image Generator] HuggingFace returned {res.status_code}: {res.text[:200]}")
    except Exception as e:
        print(f"[Image Generator] HuggingFace failed: {e}")
    return None


# ---------------------------------------------------------------------------
# Provider 3: Gemini Imagen — PAID (existing key, last resort)
# ---------------------------------------------------------------------------

def _generate_via_gemini(prompt: str, focus_topic: str) -> Optional[str]:
    """
    Generates an image using Gemini Imagen models (requires paid API plan).
    Used as last-resort fallback only.
    """
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=GEMINI_API_KEY)

        IMAGE_MODELS = [
            "models/gemini-3.1-flash-image",
            "models/gemini-3.1-flash-lite-image",
            "models/gemini-2.5-flash-image",
        ]

        for img_model in IMAGE_MODELS:
            try:
                print(f"[Image Generator] [Provider: Gemini] Trying {img_model}...")
                response = client.models.generate_content(
                    model=img_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=["TEXT", "IMAGE"],
                    ),
                )
                for part in response.candidates[0].content.parts:
                    if part.inline_data is not None:
                        return _save_and_upload(part.inline_data.data, focus_topic)
            except Exception as model_err:
                print(f"[Image Generator] Gemini {img_model} failed: {model_err}")
                continue
    except Exception as e:
        print(f"[Image Generator] Gemini provider failed: {e}")
    return None


# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------

def generate_image_for_post(
    focus_topic: str,
    trend_connection: Optional[str] = None,
    brand_style: str = "",
) -> Optional[str]:
    """
    Generates a social media image for the given post topic.

    Tries providers in order (cheapest/freest first):
      1. Pollinations.ai  — 100% free, no key
      2. Hugging Face     — free tier, needs HF_API_KEY in .env
      3. Gemini Imagen    — paid, uses existing GEMINI_API_KEY

    Returns:
        Public URL of the generated image, or None if all providers fail.
    """
    prompt = _build_image_prompt(focus_topic, trend_connection, brand_style)
    print(f"\n[Image Generator] Generating AI image for: '{focus_topic[:80]}'")

    # 1. Try Pollinations (free, no key)
    result = _generate_via_pollinations(prompt)
    if result:
        print(f"[Image Generator] [OK] Image ready via Pollinations.ai: {result}")
        return result

    # 2. Try Hugging Face (free tier)
    result = _generate_via_huggingface(prompt, focus_topic)
    if result:
        print(f"[Image Generator] [OK] Image ready via Hugging Face: {result}")
        return result

    # 3. Try Gemini (paid fallback)
    result = _generate_via_gemini(prompt, focus_topic)
    if result:
        print(f"[Image Generator] [OK] Image ready via Gemini: {result}")
        return result

    print("[Image Generator] [FAIL] All image generation providers failed.")
    return None

