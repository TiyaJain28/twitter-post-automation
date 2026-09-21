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


from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import json

# Load API credentials from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
BUFFER_ACCESS_TOKEN = os.getenv("BUFFER_ACCESS_TOKEN", "").strip()
BUFFER_CHANNEL_ID = os.getenv("BUFFER_CHANNEL_ID", "").strip()
BUFFER_CHANNEL_IDS_ENV = os.getenv("BUFFER_CHANNEL_IDS", "").strip()
ACCOUNTS_JSON_ENV = os.getenv("ACCOUNTS_JSON", "").strip()

# Safety Flags:
# DRY_RUN: Defaults to True for safe testing.
DRY_RUN = get_env_bool("DRY_RUN", default=True)

# LIVE_MODE: Defaults to False. Must be explicitly set to 'true' to publish.
LIVE_MODE = get_env_bool("LIVE_MODE", default=False)

# File Paths
CONFIG_DIR = BASE_DIR / "config"
ACCOUNTS_CONFIG_PATH = CONFIG_DIR / "accounts.json"
DATA_DIR = BASE_DIR / "data"
PROMPTS_DIR = BASE_DIR / "prompts"
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
VIDEOS_DIR = ASSETS_DIR / "videos"
GENERATED_IMAGES_DIR = ASSETS_DIR / "generated"  # AI-generated images (Gemini Imagen)
MEDIA_CATALOG_PATH = DATA_DIR / "media_catalog.json"
MEDIA_BASE_URL = os.getenv("MEDIA_BASE_URL", "").strip()


@dataclass
class AccountConfig:
    """Represents a connected Twitter/X profile with distinct persona & voice."""
    id: str               # Buffer channel ID
    name: str             # Display name / handle
    persona: str = ""     # Unique persona & voice for Gemini
    target_audience: str = "" # Specific audience for this account


# Default personas when multiple accounts are configured without custom profiles
DEFAULT_ACCOUNT_PERSONAS = [
    {
        "name": "Founder / Visionary",
        "persona": "Contrarian SaaS Founder & Bootstrapper. Focuses on founder pain points, shipping velocity, building agency leverage, SaaS economics, and unbundling legacy tools.",
        "target_audience": "Founders, indie hackers, agency owners, early-stage CTOs",
    },
    {
        "name": "Tech / Engineer",
        "persona": "Senior Full-Stack Engineer & AI Systems Architect. Focuses on browser internals, DOM state indexing vs lossy video transcripts, deterministic AI agents, and developer tooling efficiency.",
        "target_audience": "Software engineers, frontend/fullstack developers, tech leads",
    },
    {
        "name": "Agency Growth / Operations",
        "persona": "Agency Operations Strategist & Client Experience Lead. Focuses on client communication bottlenecks, unpaid scope creep in handover videos, and scaling client delivery without hiring more support.",
        "target_audience": "Digital agencies, dev shops, product managers, customer success leads",
    },
]


def get_configured_accounts() -> List[AccountConfig]:
    """
    Returns the list of all configured Twitter/X accounts to publish to.
    Resolution priority:
    1. config/accounts.json file (if present)
    2. ACCOUNTS_JSON environment variable (JSON string in GitHub secrets)
    3. BUFFER_CHANNEL_IDS (comma-separated list in env / GitHub secrets)
    4. BUFFER_CHANNEL_ID (single channel fallback)
    """
    # 1. Check config/accounts.json
    if ACCOUNTS_CONFIG_PATH.exists():
        try:
            with open(ACCOUNTS_CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list) and data:
                return [
                    AccountConfig(
                        id=str(item.get("id") or item.get("channel_id", "")).strip(),
                        name=str(item.get("name", f"Account #{idx+1}")).strip(),
                        persona=str(item.get("persona", "")).strip(),
                        target_audience=str(item.get("target_audience", "")).strip(),
                    )
                    for idx, item in enumerate(data)
                    if item.get("id") or item.get("channel_id")
                ]
        except Exception as e:
            print(f"[Warning] Failed to parse {ACCOUNTS_CONFIG_PATH}: {e}")

    # 2. Check ACCOUNTS_JSON env var
    if ACCOUNTS_JSON_ENV:
        try:
            data = json.loads(ACCOUNTS_JSON_ENV)
            if isinstance(data, list) and data:
                return [
                    AccountConfig(
                        id=str(item.get("id") or item.get("channel_id", "")).strip(),
                        name=str(item.get("name", f"Account #{idx+1}")).strip(),
                        persona=str(item.get("persona", "")).strip(),
                        target_audience=str(item.get("target_audience", "")).strip(),
                    )
                    for idx, item in enumerate(data)
                    if item.get("id") or item.get("channel_id")
                ]
        except Exception as e:
            print(f"[Warning] Failed to parse ACCOUNTS_JSON env var: {e}")

    # 3. Check BUFFER_CHANNEL_IDS (comma-separated)
    raw_ids = [cid.strip() for cid in BUFFER_CHANNEL_IDS_ENV.split(",") if cid.strip()]
    if not raw_ids and BUFFER_CHANNEL_ID:
        raw_ids = [BUFFER_CHANNEL_ID]

    accounts: List[AccountConfig] = []
    for idx, cid in enumerate(raw_ids):
        persona_template = DEFAULT_ACCOUNT_PERSONAS[idx] if idx < len(DEFAULT_ACCOUNT_PERSONAS) else {
            "name": f"Account #{idx+1}",
            "persona": "Tech industry builder & practitioner with direct, authentic observations.",
            "target_audience": "Tech builders, engineers, and digital practitioners",
        }
        accounts.append(
            AccountConfig(
                id=cid,
                name=persona_template["name"],
                persona=persona_template["persona"],
                target_audience=persona_template["target_audience"],
            )
        )

    return accounts

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
    """Validates that Buffer credentials and at least one channel are set before live publishing."""
    if not BUFFER_ACCESS_TOKEN:
        raise ValueError(
            "\n[CONFIG ERROR] BUFFER_ACCESS_TOKEN is missing!\n"
            "Please add your Buffer token to the .env file:\n"
            "   BUFFER_ACCESS_TOKEN=your_token_here\n"
            "You can generate one at: https://buffer.com/developers/api"
        )
    accounts = get_configured_accounts()
    if not accounts:
        raise ValueError(
            "\n[CONFIG ERROR] No Twitter/X Channel ID found!\n"
            "Please discover your channel ID by running:\n"
            "   python -m src.buffer_client --list-channels\n"
            "Then set BUFFER_CHANNEL_ID (or BUFFER_CHANNEL_IDS) in your .env file or GitHub Secrets."
        )


def print_system_status() -> None:
    """Displays current system configuration status without revealing secrets."""
    accounts = get_configured_accounts()
    print("\n" + "=" * 50)
    print("      DEMOLY.DEV X AUTOMATION - CONFIG STATUS")
    print("=" * 50)
    print(f"Gemini API Key:       {'[CONFIGURED]' if GEMINI_API_KEY else '[MISSING]'}")
    print(f"Buffer Access Token:  {'[CONFIGURED]' if BUFFER_ACCESS_TOKEN else '[MISSING]'}")
    print(f"Configured Accounts:  {len(accounts)} account(s)")
    for idx, acc in enumerate(accounts, 1):
        print(f"   [{idx}] {acc.name} (Channel ID: {acc.id})")
        if acc.persona:
            print(f"       Persona: {acc.persona[:60]}...")
    print(f"DRY RUN Mode:         {DRY_RUN} (Safe: No live publishing)")
    print(f"LIVE Mode:            {LIVE_MODE} (Live publishing {'ALLOWED' if LIVE_MODE else 'BLOCKED'})")
    print("=" * 50 + "\n")
