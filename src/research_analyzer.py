"""
research_analyzer.py
================================================================================
Validates competitor research data and coordinates with Gemini to generate
and update the official Demoly.dev X Content Style Guide (style-guide.md).
================================================================================
"""

import csv
from pathlib import Path
from typing import List, Dict

from src.config import (
    COMPETITOR_CSV_PATH,
    STYLE_GUIDE_PATH,
    ANALYSIS_PROMPT_PATH,
)
from src.gemini_client import GeminiClient

REQUIRED_COLUMNS = [
    "Account",
    "Account Type",
    "Post",
    "Likes",
    "Reposts",
    "Replies",
    "Views",
    "Date",
    "URL",
    "Post Type",
]


def validate_competitor_csv(file_path: Path) -> List[Dict[str, str]]:
    """
    Validates that the competitor research CSV file exists, is non-empty,
    and contains all expected column headers.
    Returns the parsed rows as a list of dictionaries.
    """
    if not file_path.exists():
        raise FileNotFoundError(
            f"\n[RESEARCH ERROR] Competitor data file not found at:\n  {file_path}\n"
            f"Please ensure competitor_posts.csv is present in the data/ directory."
        )

    with open(file_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError(f"[RESEARCH ERROR] File {file_path.name} is empty or has no header row.")

        # Check for missing columns (case-insensitive strip)
        actual_cols = {col.strip() for col in reader.fieldnames if col}
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in actual_cols]

        if missing_cols:
            raise ValueError(
                f"\n[RESEARCH ERROR] CSV is missing required columns:\n"
                f"  Missing: {', '.join(missing_cols)}\n"
                f"  Expected: {', '.join(REQUIRED_COLUMNS)}\n"
                f"  Found: {', '.join(actual_cols)}"
            )

        rows = [row for row in reader if any(row.values())]

    if not rows:
        raise ValueError(f"[RESEARCH ERROR] {file_path.name} contains headers but no data rows.")

    print(f"[Research] Successfully validated {len(rows)} competitor posts from {file_path.name}.")
    return rows


def format_research_summary(rows: List[Dict[str, str]]) -> str:
    """Formats raw CSV rows into a clean text block for Gemini analysis."""
    lines = []
    for idx, r in enumerate(rows, 1):
        lines.append(
            f"Post #{idx} by {r.get('Account', 'Unknown')} ({r.get('Account Type', 'Competitor')} - {r.get('Post Type', 'General')}):\n"
            f"Content: \"{r.get('Post', '').strip()}\"\n"
            f"Engagement: Likes={r.get('Likes', 0)}, Reposts={r.get('Reposts', 0)}, "
            f"Replies={r.get('Replies', 0)}, Views={r.get('Views', 'N/A')}\n"
            f"Date: {r.get('Date', 'N/A')} | URL: {r.get('URL', 'N/A')}\n"
        )
    return "\n".join(lines)


def run_research_analysis() -> Path:
    """
    Orchestrates the research analysis process:
    1. Validates competitor_posts.csv
    2. Builds analysis prompt
    3. Calls Gemini
    4. Writes style-guide.md
    """
    print("\n--- Starting Competitor Research Analysis ---")
    rows = validate_competitor_csv(COMPETITOR_CSV_PATH)
    data_summary = format_research_summary(rows)

    if not ANALYSIS_PROMPT_PATH.exists():
        raise FileNotFoundError(f"Analysis prompt template not found at {ANALYSIS_PROMPT_PATH}")

    prompt_template = ANALYSIS_PROMPT_PATH.read_text(encoding="utf-8")
    full_prompt = prompt_template.replace("{data_summary}", data_summary)

    # Call Gemini
    client = GeminiClient()
    new_style_guide = client.analyze_research(full_prompt)

    # Save to style-guide.md
    STYLE_GUIDE_PATH.write_text(new_style_guide, encoding="utf-8")
    print(f"[Research] Style guide updated successfully -> {STYLE_GUIDE_PATH}")
    print("--- Research Analysis Complete ---\n")
    return STYLE_GUIDE_PATH


if __name__ == "__main__":
    try:
        run_research_analysis()
    except Exception as err:
        print(f"\n[ERROR] {err}")
