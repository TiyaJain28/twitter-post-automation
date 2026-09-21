"""
content_generator.py
================================================================================
Generates original Demoly.dev X posts or threads based on the style-guide.md
using Gemini structured JSON outputs.
================================================================================
"""

import random
import re
from typing import Optional, Any
from pathlib import Path

import csv
import json
from src.config import (
    STYLE_GUIDE_PATH,
    GENERATION_PROMPT_PATH,
    DEMOLY_FAQ_PATH,
    PUBLISHED_CSV_PATH,
    TOPICS_BANK_PATH,
)
from src.gemini_client import GeminiClient, GeneratedPostModel
from src.trend_fetcher import (
    get_realtime_trending_context,
    get_realtime_trending_hashtags,
)
from src.media_manager import format_media_catalog_for_prompt, resolve_media_url
from src.image_generator import generate_image_for_post

# Maximum character limit on X (standard)
X_CHAR_LIMIT = 280


def load_style_guide(path: Optional[Path] = None) -> str:
    """Reads the style-guide.md file."""
    target_path = path or STYLE_GUIDE_PATH
    if not target_path.exists():
        raise FileNotFoundError(
            f"\n[STYLE GUIDE MISSING] Could not find style guide at: {target_path}\n"
            f"Please run the research analyzer first or ensure style-guide.md is present."
        )
    content = target_path.read_text(encoding="utf-8").strip()
    if not content:
        raise ValueError("[STYLE GUIDE EMPTY] style-guide.md exists but is empty.")
    return content


def load_knowledge_base(path: Optional[Path] = None) -> str:
    """Reads the Demoly FAQ & Knowledge Base file (data/demoly_faq.md)."""
    target_path = path or DEMOLY_FAQ_PATH
    if not target_path.exists():
        return ""
    return target_path.read_text(encoding="utf-8").strip()


def load_recent_published_posts(limit: int = 8) -> str:
    """Reads the last N posts from published_posts.csv to prevent repetition."""
    if not PUBLISHED_CSV_PATH.exists():
        return "None yet (this is the first post)."
    try:
        with open(PUBLISHED_CSV_PATH, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [r for r in reader if r.get("Content")]
        if not rows:
            return "None yet (this is the first post)."
        recent = rows[-limit:]
        formatted = []
        for idx, r in enumerate(recent, 1):
            text_snippet = r.get("Content", "").replace(" || ", " ")[:160]
            formatted.append(f"{idx}. [{r.get('Post Type', 'post')}] {text_snippet}...")
        return "\n".join(formatted)
    except Exception:
        return "None yet."


def load_topic_inspiration(limit: int = 5) -> str:
    """Randomly samples N topics from the 100-topic bank (data/topics_bank.json)."""
    if not TOPICS_BANK_PATH.exists():
        return ""
    try:
        with open(TOPICS_BANK_PATH, mode="r", encoding="utf-8") as f:
            topics = json.load(f)
        if not topics:
            return ""
        sample_size = min(limit, len(topics))
        chosen = random.sample(topics, sample_size)
        formatted = []
        for t in chosen:
            formatted.append(
                f"- [Topic #{t.get('id', '?')} | {t.get('pillar', 'General')}]: {t.get('topic', '')}\n"
                f"  Angle: {t.get('angle', '')}\n"
                f"  Hook Idea: \"{t.get('hook_seed', '')}\""
            )
        return "\n".join(formatted)
    except Exception:
        return ""


def split_long_post(text: str, max_len: int = 280) -> list[str]:
    """Splits a post into multiple items strictly <= max_len without cutting mid-sentence or mid-word."""
    if len(text) <= max_len:
        return [text]

    paragraphs = text.split("\n\n")
    chunks = []
    current = ""
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if len(p) > max_len:
            sentences = re.split(r"(?<=[.!?])\s+", p)
            for s in sentences:
                s = s.strip()
                if not s:
                    continue
                if len(s) > max_len:
                    words = s.split(" ")
                    for w in words:
                        if not current:
                            current = w
                        elif len(current) + 1 + len(w) <= max_len:
                            current += " " + w
                        else:
                            chunks.append(current)
                            current = w
                else:
                    if not current:
                        current = s
                    elif len(current) + 1 + len(s) <= max_len:
                        current += " " + s
                    else:
                        chunks.append(current)
                        current = s
        else:
            if not current:
                current = p
            elif len(current) + 2 + len(p) <= max_len:
                current += "\n\n" + p
            else:
                chunks.append(current)
                current = p

    if current:
        chunks.append(current)

    return chunks


def validate_generated_content(content: GeneratedPostModel) -> GeneratedPostModel:
    """
    Validates structural rules on the generated content.
    Ensures every post adheres strictly to X's 280-char limit by automatically
    splitting longer paragraphs into multi-tweet sequences.
    """
    if not content.posts:
        raise ValueError("[GENERATION ERROR] Gemini returned an empty list of posts.")

    clean_posts = []
    for idx, post in enumerate(content.posts, 1):
        text = post.strip()
        if not text:
            continue

        # Sanitize: strip out any forbidden "Breakdown 👇", "Breakdown:", or pointing-down emojis
        text = re.sub(r"\s*(?:Breakdown|breakdown)?\s*[👇⬇]\s*$", "", text).strip()
        text = re.sub(r"\s+(?:Breakdown|breakdown)\s*[:\.]?\s*$", ".", text).strip()
        text = text.replace("👇", "").replace("🧵", "").strip()

        # For single posts or posts with media attached, prioritize keeping it as a single tweet <= 280 chars:
        if (content.type == "single" or content.media_filename) and len(text) > 280:
            # Check if trailing hashtags caused the overflow
            tags_match = re.search(r"\n\n(#[A-Za-z0-9_ ]+)$", text)
            if tags_match:
                base_text = text[:tags_match.start()].strip()
                tag_list = tags_match.group(1).split()
                fitted = False
                for t in tag_list:
                    if len(base_text) + len(t) + 2 <= 280:
                        text = f"{base_text}\n\n{t}"
                        fitted = True
                        break
                if not fitted and len(base_text) <= 280:
                    text = base_text

        # If post exceeds 280, safely split across tweets so Buffer / Twitter never rejects it
        if len(text) > 280:
            split_items = split_long_post(text, max_len=280)
            if content.type == "single" and len(split_items) > 1:
                content.type = "thread"
            clean_posts.extend(split_items)
        else:
            clean_posts.append(text)

    # Ensure at least 1-2 trending hashtags exist on the final tweet/post if none were generated
    has_hashtags = any("#" in p for p in clean_posts)
    if not has_hashtags and clean_posts:
        fallback_tags = "#buildinpublic #AI"
        last_post = clean_posts[-1]
        if len(last_post) + len(fallback_tags) + 2 <= 280:
            clean_posts[-1] = f"{last_post}\n\n{fallback_tags}"
        elif len(last_post) + 5 <= 280:
            clean_posts[-1] = f"{last_post}\n\n#AI"

    content.posts = clean_posts
    return content


def generate_post(
    content_type_preference: Optional[str] = None,
    gemini_client: Optional[GeminiClient] = None,
    preferred_media_filename: Optional[str] = None,
    allow_media: Optional[bool] = None,
    planned_focus_topic: Optional[str] = None,
    planned_trend_connection: Optional[str] = None,
    planned_rationale: Optional[str] = None,
    cached_trends: Optional[str] = None,
    cached_hashtags: Optional[str] = None,
) -> GeneratedPostModel:
    """
    Reads the style guide and generates either a single post or a thread.

    Parameters:
        content_type_preference: 'single', 'thread', or None (random choice)
        gemini_client: Optional GeminiClient instance
        preferred_media_filename: Optional filename of video or image to force attach
        allow_media: True to force media, False for text-only, None for balanced 25% cadence
        planned_focus_topic: Explicit topic angle planned for this post
        planned_trend_connection: Trending topic/hashtag connection
        planned_rationale: Strategic context for why this post was chosen
        cached_trends: Pre-fetched tech trends context to avoid duplicate network calls
        cached_hashtags: Pre-fetched trending hashtags to avoid duplicate network calls
    """
    style_guide = load_style_guide()
    knowledge_base = load_knowledge_base()
    recent_posts = load_recent_published_posts(limit=6)
    topic_inspiration = load_topic_inspiration(limit=5)
    realtime_trends = cached_trends or get_realtime_trending_context()
    trending_hashtags = cached_hashtags or get_realtime_trending_hashtags()

    # Determine whether this run should consider media:
    # If user passed --media: always True
    # If user passed --no-media: always False
    # If not specified: Healthy cadence -> 25% media, 75% text-only
    if preferred_media_filename:
        use_media = True
    elif allow_media is not None:
        use_media = allow_media
    else:
        use_media = random.random() < 0.25  # 1 in 4 posts

    if use_media:
        available_media = format_media_catalog_for_prompt()
    else:
        available_media = "None for this run. This post/thread is strictly TEXT-ONLY. You MUST set 'media_filename': null."

    if not GENERATION_PROMPT_PATH.exists():
        raise FileNotFoundError(f"Generation prompt template not found at {GENERATION_PROMPT_PATH}")

    prompt_template = GENERATION_PROMPT_PATH.read_text(encoding="utf-8")

    # Follow Style Guide: 80% threads, 20% single tweets
    if not content_type_preference:
        content_type_preference = random.choices(["thread", "single"], weights=[0.8, 0.2], k=1)[0]

    formatted_prompt = prompt_template.format(
        style_guide=style_guide,
        knowledge_base=knowledge_base,
        recent_posts=recent_posts,
        topic_inspiration=topic_inspiration,
        realtime_trends=realtime_trends,
        trending_hashtags=trending_hashtags,
        available_media=available_media,
        content_type_preference=content_type_preference,
    )

    # Inject planned strategic topic if specified by the daily planner
    if planned_focus_topic:
        formatted_prompt += f"\n\nTARGETED STRATEGIC OBJECTIVE FOR THIS RUN:\n- Primary Topic / Angle: {planned_focus_topic}"
        if planned_rationale:
            formatted_prompt += f"\n- Strategic Context: {planned_rationale}"
        if planned_trend_connection:
            formatted_prompt += f"\n- Live Trend / Hashtag Context to incorporate: {planned_trend_connection}"
        formatted_prompt += "\nFocus your post tightly around this angle while adhering to all Demoly voice and style rules."

    if preferred_media_filename:
        formatted_prompt += f"\n\nUSER OVERRIDE: You MUST use and reference the authentic media asset '{preferred_media_filename}' for this post. Set media_filename to '{preferred_media_filename}'."

    client = gemini_client or GeminiClient()
    raw_content = client.generate_content(formatted_prompt)

    # Validate output
    validated = validate_generated_content(raw_content)

    # Resolve media URL if media was selected
    if preferred_media_filename:
        validated.media_filename = preferred_media_filename

    if validated.media_filename:
        validated.media_url = resolve_media_url(validated.media_filename)

    return validated


def generate_planned_post(
    plan_item: Any,
    gemini_client: Optional[GeminiClient] = None,
    cached_trends: Optional[str] = None,
    cached_hashtags: Optional[str] = None,
) -> GeneratedPostModel:
    """
    Generates a single post or thread following a PostPlanItem from DailyCadencePlan.
    Supports both catalog-asset media posts and Gemini AI-generated image posts.
    """
    allow_media = True if plan_item.format == "media" else False

    # If generate_image=True, we don't pass preferred_media to the prompt
    # (no catalog asset), but we DO still flag allow_media=True so the prompt
    # is formatted as a media post. After generation, we attach the AI image URL.
    preferred_media_for_prompt = None if getattr(plan_item, "generate_image", False) else plan_item.preferred_media

    result = generate_post(
        content_type_preference=plan_item.post_type,
        gemini_client=gemini_client,
        preferred_media_filename=preferred_media_for_prompt,
        allow_media=allow_media,
        planned_focus_topic=plan_item.focus_topic,
        planned_trend_connection=plan_item.trend_connection,
        planned_rationale=plan_item.source_rationale,
        cached_trends=cached_trends,
        cached_hashtags=cached_hashtags,
    )

    # If this is an AI-generated image post, generate and attach the image now
    if getattr(plan_item, "generate_image", False) and plan_item.format == "media":
        print("[Content Generator] Requesting AI image generation from Gemini Imagen...")
        image_url = generate_image_for_post(
            focus_topic=plan_item.focus_topic,
            trend_connection=plan_item.trend_connection,
        )
        if image_url:
            result.media_filename = None  # No catalog filename — it's generated
            result.media_url = image_url
            print(f"[Content Generator] AI image attached: {image_url}")
        else:
            # Fallback: try to pick any catalog asset rather than posting blank
            print("[Content Generator] AI image generation failed. Falling back to catalog asset.")
            from src.media_manager import load_media_catalog
            catalog = load_media_catalog()
            if catalog:
                fallback_file = catalog[0].get("filename")
                result.media_filename = fallback_file
                result.media_url = resolve_media_url(fallback_file)
                print(f"[Content Generator] Fallback catalog asset: {fallback_file}")

    return result


if __name__ == "__main__":
    try:
        res = generate_post()
        print(f"\n[Generated Type]: {res.type}")
        for i, p in enumerate(res.posts, 1):
            print(f"\n--- Post {i} ({len(p)} chars) ---\n{p}")
    except Exception as err:
        print(f"\n[ERROR] {err}")
