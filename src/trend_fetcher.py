"""
trend_fetcher.py
================================================================================
Fetches real-time trending tech news, developer discussions, and industry
shifts dynamically on every run (both locally and in GitHub Actions).
Uses public, zero-auth, zero-rate-limit APIs (Hacker News & Dev.to).
================================================================================
"""

import requests
import re
from typing import List

HN_TOP_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"
DEVTO_TOP_URL = "https://dev.to/api/articles?per_page=6&top=1"
DEVTO_TECH_URL = "https://dev.to/api/articles?tag=tech&top=1"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Safe fallback trends if external network is unavailable
EVERGREEN_TRENDS = [
    "AI coding agents (Cursor, Claude Code, Antigravity) and Model Context Protocol (MCP)",
    "'Vibe coding' hype vs. the reality of testing, QA, and client handovers",
    "B2B SaaS subscription fatigue: cutting $20/seat tools and bloated meeting tools",
    "The backlash against 'book a demo' forms and 30-minute discovery calls",
    "Async engineering culture: replacing repetitive Google Meet calls with interactive links",
]

# Core high-performing tech/startup Twitter hashtags
EVERGREEN_TECH_HASHTAGS = [
    "#AI",
    "#buildinpublic",
    "#webdev",
    "#SaaS",
    "#coding",
    "#vibecoding",
    "#softwareengineering",
    "#devops",
    "#frontend",
    "#tech",
]


def fetch_hacker_news_trends(limit: int = 6) -> List[str]:
    """Fetches real-time top stories from Hacker News."""
    try:
        resp = requests.get(HN_TOP_URL, timeout=4)
        if resp.status_code != 200:
            return []
        story_ids = resp.json()[:limit * 2]

        headlines = []
        for sid in story_ids:
            try:
                item_resp = requests.get(HN_ITEM_URL.format(sid), timeout=3)
                if item_resp.status_code == 200:
                    data = item_resp.json()
                    title = data.get("title", "").strip()
                    score = data.get("score", 0)
                    if title:
                        headlines.append(f"{title} (HN Score: {score})")
                    if len(headlines) >= limit:
                        break
            except Exception:
                continue

        return headlines
    except Exception as e:
        print(f"[Trend Fetcher] Hacker News fetch notice: {e}")
        return []


def fetch_devto_trends(limit: int = 3) -> List[str]:
    """Fetches trending developer articles from Dev.to."""
    try:
        resp = requests.get(DEVTO_TOP_URL, timeout=4)
        if resp.status_code != 200:
            return []
        articles = resp.json()[:limit]
        return [f"{a.get('title', '')} (Dev.to - {a.get('readable_publish_date', 'today')})" for a in articles if a.get("title")]
    except Exception:
        return []


def fetch_twitter_trending_hashtags(limit: int = 15) -> List[str]:
    """
    Fetches real-time trending hashtags from Twitter/X and developer communities.
    Aggregates live Twitter trends (Trends24) and Dev.to trending topics,
    combined with core high-reach tech hashtags.
    """
    headers = {"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"}
    live_twitter_hashtags = []

    # 1. Fetch live Twitter trending hashtags from Trends24 (US & Global)
    for url in ["https://trends24.in/united-states/", "https://trends24.in/"]:
        try:
            r = requests.get(url, headers=headers, timeout=4)
            if r.status_code == 200:
                matches = re.findall(r'href="https://twitter\.com/search\?q=[^"]+"[^>]*>([^<]+)</a>', r.text)
                for item in matches:
                    item = item.strip()
                    # Filter for clean ASCII alphanumeric hashtags
                    if item.startswith("#") and re.match(r"^#[A-Za-z0-9_]{2,30}$", item):
                        if item not in live_twitter_hashtags:
                            live_twitter_hashtags.append(item)
            if len(live_twitter_hashtags) >= 10:
                break
        except Exception as e:
            print(f"[Trend Fetcher] Twitter trends notice: {e}")

    # 2. Fetch live developer trending tags from Dev.to
    devto_tags = []
    try:
        r_devto = requests.get(DEVTO_TECH_URL, headers=headers, timeout=4)
        if r_devto.status_code == 200:
            for a in r_devto.json()[:6]:
                for tag in a.get("tag_list", []):
                    ht = f"#{tag}"
                    if re.match(r"^#[A-Za-z0-9_]{2,30}$", ht) and ht not in devto_tags:
                        devto_tags.append(ht)
    except Exception as e:
        print(f"[Trend Fetcher] Dev.to tags notice: {e}")

    # 3. Combine: Tech dev tags + Core tech hashtags + Live Twitter hashtags
    combined = []
    for tag in devto_tags + EVERGREEN_TECH_HASHTAGS + live_twitter_hashtags:
        if tag.lower() not in [c.lower() for c in combined]:
            combined.append(tag)

    return combined[:limit]


def get_realtime_trending_context() -> str:
    """
    Collects real-time tech trends from multiple live sources.
    Returns a formatted string ready for injection into the generation prompt.
    """
    print("[Trends] Fetching real-time tech trends from live sources...")
    trends = []

    # 1. Hacker News
    hn = fetch_hacker_news_trends(limit=5)
    if hn:
        trends.extend(hn)

    # 2. Dev.to
    devto = fetch_devto_trends(limit=3)
    if devto:
        trends.extend(devto)

    # 3. Fallback if offline
    if not trends:
        print("[Trends] Using evergreen tech trends as fallback.")
        trends = EVERGREEN_TRENDS

    formatted = "\n".join([f"- {t}" for t in trends])
    print(f"[Trends] Successfully gathered {len(trends)} real-time trending topics.")
    return formatted


def get_realtime_trending_hashtags() -> str:
    """
    Collects real-time trending hashtags from Twitter/X and developer communities.
    Returns a clean formatted string for injection into the generation prompt.
    """
    print("[Trends] Fetching real-time trending hashtags from Twitter/X...")
    tags = fetch_twitter_trending_hashtags(limit=16)
    formatted = " ".join(tags)
    print(f"[Trends] Successfully gathered {len(tags)} trending hashtags: {formatted}")
    return formatted


if __name__ == "__main__":
    print("\n--- Real-Time Trending News Test ---")
    print(get_realtime_trending_context())
    print("\n--- Real-Time Trending Hashtags Test ---")
    print(get_realtime_trending_hashtags())
