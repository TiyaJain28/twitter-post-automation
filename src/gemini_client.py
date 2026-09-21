"""
gemini_client.py
================================================================================
Gemini client module using the official Google GenAI Python SDK.
Handles text analysis and structured JSON post/thread generation with error handling.
================================================================================
"""

import json
import re
from typing import Optional
import os
from pydantic import BaseModel, Field

from src.config import GEMINI_API_KEY, validate_gemini_config

CANDIDATE_MODELS = [
    os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.8-flash",
    "gemini-3.6-flash",
    "gemini-pro-latest",
]



class GeneratedPostModel(BaseModel):
    """Structured format for generated single post or thread."""
    type: str = Field(description="Must be 'single' or 'thread'")
    posts: list[str] = Field(description="List of posts. Single post has 1 item, thread has dynamic length (typically 3 to 7 items depending on topic depth).")
    media_filename: Optional[str] = Field(default=None, description="Optional filename of matching video or image from available media library (e.g. 'demo.mp4'), or None")
    media_url: Optional[str] = Field(default=None, description="Public URL of the media file, if resolved")


class GeminiClient:
    """Client for interacting with Google Gemini API."""

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or CANDIDATE_MODELS[0]
        self._client = None

    def _get_client(self):
        """Initializes and returns the official Google GenAI Client."""
        if self._client is not None:
            return self._client

        validate_gemini_config()

        try:
            from google import genai
            self._client = genai.Client(api_key=GEMINI_API_KEY)
            return self._client
        except ImportError:
            raise ImportError(
                "\n[DEPENDENCY ERROR] The 'google-genai' package is not installed.\n"
                "Please run:\n"
                "   pip install google-genai\n"
            )
        except Exception as e:
            raise RuntimeError(f"[GEMINI INIT ERROR] Could not initialize Gemini client: {e}")

    def analyze_research(self, prompt: str) -> str:
        """
        Sends competitor data and analysis prompt to Gemini to produce the style guide.
        Returns the raw markdown response.
        """
        client = self._get_client()
        last_err = None

        for model in CANDIDATE_MODELS:
            try:
                print(f"[Gemini] Analyzing competitor research using {model}...")
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )
                if not response.text:
                    raise ValueError("Gemini returned an empty response during research analysis.")
                return response.text.strip()
            except Exception as e:
                last_err = e
                print(f"[Gemini Warning] Model {model} encountered an issue ({e}). Trying fallback...")

        raise RuntimeError(f"[GEMINI API ERROR] Failed to analyze research across candidate models: {last_err}")

    def generate_content(self, prompt: str) -> GeneratedPostModel:
        """
        Generates original Demoly.dev content enforcing structured JSON output.
        Returns a validated GeneratedPostModel object.
        """
        client = self._get_client()
        last_err = None

        for model in CANDIDATE_MODELS:
            try:
                print(f"[Gemini] Generating original content using {model}...")
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": GeneratedPostModel,
                    },
                )

                # If the SDK automatically parses the schema:
                if hasattr(response, "parsed") and response.parsed is not None:
                    if isinstance(response.parsed, GeneratedPostModel):
                        return response.parsed

                # Fallback: parse raw text output
                raw_text = response.text.strip()
                cleaned_text = re.sub(r"^```json\s*", "", raw_text, flags=re.MULTILINE)
                cleaned_text = re.sub(r"^```\s*$", "", cleaned_text, flags=re.MULTILINE).strip()
                data = json.loads(cleaned_text)
                return GeneratedPostModel(**data)

            except Exception as e:
                last_err = e
                print(f"[Gemini Warning] Model {model} encountered an issue: {e}. Trying fallback...")

        raise RuntimeError(f"[GEMINI API ERROR] Content generation failed across models: {last_err}")

