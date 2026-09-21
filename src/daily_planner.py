"""
daily_planner.py
================================================================================
Intelligent Daily Cadence Planner for Demoly.dev X (Twitter) Automation.

Orchestrates 3 distinct posts per day:
1. A Single Tweet (text-only)
2. A Thread (multi-tweet deep dive, text-only)
3. A Post with Photo/Video (authentic demo media attached)

Strategy:
- First evaluates real-time Twitter trending hashtags and tech discussions.
- Determines which format is best suited to trend-jack or address the top trend.
- Dynamically selects the most suitable topics/sources (Trend, FAQ, Topic Bank,
  or hybrid) for that day across the 3 formats without rigid formula constraints.
================================================================================
"""

import json
from typing import Optional, List
from pydantic import BaseModel, Field

from src.config import (
    TOPICS_BANK_PATH,
    DEMOLY_FAQ_PATH,
    PUBLISHED_CSV_PATH,
)
from src.gemini_client import GeminiClient
from src.trend_fetcher import (
    get_realtime_trending_context,
    get_realtime_trending_hashtags,
)
from src.media_manager import load_media_catalog, format_media_catalog_for_prompt
from src.content_generator import (
    load_style_guide,
    load_recent_published_posts,
    load_topic_inspiration,
)


class PostPlanItem(BaseModel):
    """Execution plan for a single post in the daily trio."""
    format: str = Field(description="Must be 'single' (text-only tweet), 'thread' (text-only thread), or 'media' (tweet/thread with photo/video)")
    post_type: str = Field(description="Content structure: 'single' or 'thread'")
    focus_topic: str = Field(description="The primary angle, problem statement, or concept for this post")
    source_rationale: str = Field(description="Strategic explanation of why this topic and source were chosen for today")
    trend_connection: Optional[str] = Field(default=None, description="Specific trending topic or hashtag to reference/trend-jack, if relevant")
    preferred_media: Optional[str] = Field(default=None, description="Filename from available media catalog if format=='media' and generate_image is False, else null")
    generate_image: bool = Field(default=False, description="If True, Gemini will generate a custom AI image for this post instead of using a catalog asset. Set True when the post is trend-based or when no catalog asset closely matches the topic.")


class DailyCadencePlan(BaseModel):
    """Overall strategic plan for today's 3-post cadence."""
    trend_analysis: str = Field(description="Evaluation of today's live trends and why formats/topics were allocated this way")
    items: List[PostPlanItem] = Field(description="Exactly 3 post items: 1 single tweet, 1 thread, 1 media post")


PLANNER_SYSTEM_PROMPT = """
You are the Head of Growth and Technical Social Strategist for Demoly (https://demoly.dev).
Demoly is an AI-powered browser screen recorder, client handover platform, and visual bug reporting tool built specifically for tech agencies, web development studios, and QA teams.
Demoly records the browser DOM (Document Object Model), enabling AI visual search on silent videos, element-level privacy masking, public interactive AI links, and MCP server integrations for Cursor/Antigravity/Claude Code.

Your task is to craft today's 3-POST CONTENT PLAN for Demoly's official X (Twitter) account:
1. One Single Tweet (strictly text-only, punchy insight or question)
2. One Thread (strictly text-only, multi-tweet deep dive or framework)
3. One Post with Photo/Video (showcases media with matching copy)

PLANNING RULES & STRATEGY:
1. TREND-FIRST EVALUATION:
   - First, examine the real-time tech trends and Twitter trending hashtags fetched live today.
   - Determine which format (Single Tweet, Thread, or Media Post) is best suited to address today's most prominent trend:
     * If the trend is a broad technical discussion or debate (e.g. AI agent shifts, AOSP architecture, B2B tool fatigue) -> A Thread is often ideal.
     * If the trend is a sharp take, contrarian observation, or quick viral debate -> A Single Tweet is often ideal.
     * If the trend relates to frontend testing, visual bugs, or UI workflows -> A Media Post demonstrating Demoly's solution is ideal.

2. DYNAMIC SOURCE SELECTION (NO RIGID FORMULAS):
   - You are NOT locked to an arbitrary 1-trend, 1-faq, 1-topic bank rule.
   - Assess what is most compelling, timely, and valuable for Demoly's agency audience today:
     * You may draw from Live Trends, Demoly FAQ architectural capabilities, Topic Bank agency friction points, or a blend.
     * Ensure all 3 posts explore DIFFERENT angles so the feed feels vibrant, diverse, and high-value.

3. GUARANTEED FORMAT TRIO:
   Across the 3 items in "items":
   - Exactly ONE item MUST have format="single" and post_type="single" with preferred_media=null and generate_image=false.
   - Exactly ONE item MUST have format="thread" and post_type="thread" with preferred_media=null and generate_image=false.
   - Exactly ONE item MUST have format="media" and post_type="single".

4. MEDIA DECISION FOR THE MEDIA POST (generate_image vs catalog asset):
   For the format="media" item, you MUST choose ONE of the following options:

   OPTION A — Use a Catalog Asset (generate_image=false):
   - Set generate_image=false and preferred_media=<exact filename from AVAILABLE MEDIA>.
   - Use this when a catalog asset closely matches the post topic (e.g. a post about AI search → use an AI search screenshot).
   - The catalog asset should reinforce the post copy with visual proof.

   OPTION B — Generate AI Image (generate_image=true):
   - Set generate_image=true and preferred_media=null.
   - Use this when:
     * The media post is strongly trend-based (i.e. the trending topic is the main hook).
     * No catalog asset closely matches the topic angle.
     * The post is drawing from Topic Bank themes that aren't covered by catalog screenshots.
   - Gemini will generate a custom branded image for the post automatically.

   Decision guideline: Prefer AI-generated images for trend-first posts. Prefer catalog assets for Demoly feature demo posts.

5. DEDUPLICATION:
   - Review RECENTLY PUBLISHED POSTS. Do not reuse recent angles or hooks.

OUTPUT FORMAT:
Return strictly valid JSON matching the DailyCadencePlan schema.
"""


def plan_daily_cadence(gemini_client: Optional[GeminiClient] = None) -> DailyCadencePlan:
    """
    Analyzes live trends, available assets, and recent posts to construct
    an optimized 3-post daily cadence plan.
    """
    print("\n[Daily Planner] Analyzing live trends, assets, and topic bank...")
    realtime_trends = get_realtime_trending_context()
    trending_hashtags = get_realtime_trending_hashtags()
    recent_posts = load_recent_published_posts(limit=8)
    topic_inspiration = load_topic_inspiration(limit=8)
    available_media = format_media_catalog_for_prompt()

    user_prompt = f"""
LIVE REAL-TIME TECH TRENDS TODAY:
{realtime_trends}

LIVE TWITTER TRENDING HASHTAGS TODAY:
{trending_hashtags}

AVAILABLE AUTHENTIC PRODUCT MEDIA ASSETS:
{available_media}

RECENTLY PUBLISHED POSTS (DO NOT REPEAT):
{recent_posts}

TOPIC BANK CANDIDATES FOR INSPIRATION:
{topic_inspiration}

Create today's 3-post strategy plan now according to the planning rules.
"""

    client = gemini_client or GeminiClient()

    # Use Gemini structured outputs with DailyCadencePlan
    response = client._get_client().models.generate_content(
        model=client.model_name,
        contents=[
            {"role": "user", "parts": [{"text": PLANNER_SYSTEM_PROMPT + "\n\n" + user_prompt}]}
        ],
        config={
            "response_mime_type": "application/json",
            "response_schema": DailyCadencePlan,
            "temperature": 0.5,
        },
    )

    raw_text = response.text
    parsed_json = json.loads(raw_text)
    plan = DailyCadencePlan(**parsed_json)

    # Sanity verification on format trio:
    formats = [item.format for item in plan.items]
    if "single" not in formats or "thread" not in formats or "media" not in formats:
        # Normalize if needed
        print("[Daily Planner] Note: Re-normalizing formats to guarantee Single, Thread, and Media trio.")
        plan.items[0].format = "single"
        plan.items[0].post_type = "single"
        plan.items[0].preferred_media = None
        plan.items[0].generate_image = False

        plan.items[1].format = "thread"
        plan.items[1].post_type = "thread"
        plan.items[1].preferred_media = None
        plan.items[1].generate_image = False

        plan.items[2].format = "media"
        catalog = load_media_catalog()
        if catalog and not plan.items[2].preferred_media and not plan.items[2].generate_image:
            plan.items[2].preferred_media = catalog[0].get("filename")

    # Ensure media item has either preferred_media or generate_image=True
    for item in plan.items:
        if item.format == "media" and not item.preferred_media and not item.generate_image:
            # Default: pick first catalog asset if no decision was made
            catalog = load_media_catalog()
            if catalog:
                item.preferred_media = catalog[0].get("filename")
            else:
                item.generate_image = True  # No catalog? Generate one.

    print(f"[Daily Planner] Successfully planned 3 posts.")
    print(f"[Daily Planner Strategy]: {plan.trend_analysis}")
    for idx, it in enumerate(plan.items, 1):
        if it.format == "media":
            media_mode = "AI-GENERATED" if it.generate_image else f"CATALOG: {it.preferred_media or 'None'}"
        else:
            media_mode = "text-only"
        print(f"  Post #{idx} [{it.format.upper()}]: {it.focus_topic[:70]}... | Image: {media_mode}")

    return plan


if __name__ == "__main__":
    print("\n--- Testing Daily Planner ---")
    daily_plan = plan_daily_cadence()
    print("\nGenerated Plan Details:")
    print(json.dumps(daily_plan.model_dump(), indent=2))
