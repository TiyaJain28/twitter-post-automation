"""
config.py
================================================================================
Central configuration and environment loader for Demoly.dev X Automation.
Safely reads .env without ever logging or exposing private API keys.
================================================================================
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Root directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file if it exists
load_dotenv(dotenv_path=BASE_DIR / ".env")


def get_env_bool(name: str, default: bool = False) -> bool:
    """Safely parse boolean environment variable."""
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in ("true", "1", "yes", "on")


# Load API credentials from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
BUFFER_ACCESS_TOKEN = os.getenv("BUFFER_ACCESS_TOKEN", "").strip()
BUFFER_CHANNEL_ID = os.getenv("BUFFER_CHANNEL_ID", "").strip()

# Safety Flags:
# DRY_RUN: Defaults to True for safe testing.
DRY_RUN = get_env_bool("DRY_RUN", default=True)

# LIVE_MODE: Defaults to False. Must be explicitly set to 'true' to publish.
LIVE_MODE = get_env_bool("LIVE_MODE", default=False)

# File Paths
DATA_DIR = BASE_DIR / "data"
PROMPTS_DIR = BASE_DIR / "prompts"
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
VIDEOS_DIR = ASSETS_DIR / "videos"
GENERATED_IMAGES_DIR = ASSETS_DIR / "generated"  # AI-generated images (Gemini Imagen)
MEDIA_CATALOG_PATH = DATA_DIR / "media_catalog.json"
MEDIA_BASE_URL = os.getenv("MEDIA_BASE_URL", "").strip()

COMPETITOR_CSV_PATH = DATA_DIR / "competitor_posts.csv"
PUBLISHED_CSV_PATH = DATA_DIR / "published_posts.csv"
STYLE_GUIDE_PATH = BASE_DIR / "style-guide.md"
DEMOLY_FAQ_PATH = DATA_DIR / "demoly_faq.md"
TOPICS_BANK_PATH = DATA_DIR / "topics_bank.json"
ANALYSIS_PROMPT_PATH = PROMPTS_DIR / "analysis_prompt.txt"
GENERATION_PROMPT_PATH = PROMPTS_DIR / "generation_prompt.txt"


def mask_secret(secret: str) -> str:
    """Masks a secret string for safe display (e.g. 'AIzaSy...****')."""
    if not secret:
        return "(not set)"
    if len(secret) <= 8:
        return "********"
    return f"{secret[:4]}...{secret[-4:]}"


def validate_gemini_config() -> None:
    """Validates that the Gemini API key is present."""
    if not GEMINI_API_KEY:
        raise ValueError(
            "\n[CONFIG ERROR] GEMINI_API_KEY is missing!\n"
            "Please add your Gemini API key to the .env file:\n"
            "   GEMINI_API_KEY=your_actual_key_here\n"
            "You can get a free key at: https://aistudio.google.com/app/apikey"
        )


def validate_buffer_config() -> None:
    """Validates that Buffer credentials are set before live publishing."""
    if not BUFFER_ACCESS_TOKEN:
        raise ValueError(
            "\n[CONFIG ERROR] BUFFER_ACCESS_TOKEN is missing!\n"
            "Please add your Buffer token to the .env file:\n"
            "   BUFFER_ACCESS_TOKEN=your_token_here\n"
            "You can generate one at: https://buffer.com/developers/api"
        )
    if not BUFFER_CHANNEL_ID:
        raise ValueError(
            "\n[CONFIG ERROR] BUFFER_CHANNEL_ID is missing!\n"
            "Please discover your channel ID by running:\n"
            "   python -m src.buffer_client --list-channels\n"
            "Then set BUFFER_CHANNEL_ID in your .env file."
        )


def print_system_status() -> None:
    """Displays current system configuration status without revealing secrets."""
    print("\n" + "=" * 50)
    print("      DEMOLY.DEV X AUTOMATION - CONFIG STATUS")
    print("=" * 50)
    print(f"Gemini API Key:       {'[CONFIGURED]' if GEMINI_API_KEY else '[MISSING]'}")
    print(f"Buffer Access Token:  {'[CONFIGURED]' if BUFFER_ACCESS_TOKEN else '[MISSING]'}")
    print(f"Buffer Channel ID:    {BUFFER_CHANNEL_ID if BUFFER_CHANNEL_ID else '[NOT SET]'}")
    print(f"DRY RUN Mode:         {DRY_RUN} (Safe: No live publishing)")
    print(f"LIVE Mode:            {LIVE_MODE} (Live publishing {'ALLOWED' if LIVE_MODE else 'BLOCKED'})")
    print("=" * 50 + "\n")
