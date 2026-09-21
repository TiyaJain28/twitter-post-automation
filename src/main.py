"""
main.py
================================================================================
Main entry point for Demoly.dev X Automation.
Coordinates:
1. Research Analysis (--analyze)
2. Safe Content Generation
3. Safe Dry-Run Display (Default)
4. Live Buffer Publishing (Only when LIVE_MODE=true)
5. Audit Logging to data/published_posts.csv
================================================================================
"""

import sys
import csv
import time
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, List

# Ensure UTF-8 output encoding for emojis on Windows PowerShell/CMD
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


from src.config import (
    DRY_RUN,
    LIVE_MODE,
    PUBLISHED_CSV_PATH,
    AccountConfig,
    get_configured_accounts,
    print_system_status,
)
from src.content_generator import generate_post, generate_planned_post
from src.daily_planner import plan_daily_cadence, DailyCadencePlan
from src.trend_fetcher import (
    get_realtime_trending_context,
    get_realtime_trending_hashtags,
)
from src.research_analyzer import run_research_analysis
from src.buffer_client import BufferClient, print_available_channels
from src.gemini_client import GeneratedPostModel
from src.media_manager import scan_and_index_assets


def log_published_post(
    content: GeneratedPostModel,
    buffer_id: str,
    status: str,
    csv_path: Optional[Path] = None,
    account_name: Optional[str] = None,
) -> None:
    """
    Appends the post details to data/published_posts.csv.
    Schema: Timestamp,Account,Post Type,Content,Buffer ID,Status,Media
    """
    target_path = csv_path or PUBLISHED_CSV_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)

    file_exists = target_path.exists()
    has_account_header = False
    if file_exists:
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                first_line = f.readline()
                if "Account" in first_line:
                    has_account_header = True
        except Exception:
            pass

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    post_type = content.type
    media_info = content.media_filename or "none"
    combined_content = " || ".join(content.posts)
    acct = account_name or "Default"

    with open(target_path, mode="a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Account", "Post Type", "Content", "Buffer ID", "Status", "Media"])
            writer.writerow([timestamp, acct, post_type, combined_content, buffer_id, status, media_info])
        elif has_account_header:
            writer.writerow([timestamp, acct, post_type, combined_content, buffer_id, status, media_info])
        else:
            # Append Account as an extra trailing column if existing CSV had old format
            writer.writerow([timestamp, post_type, combined_content, buffer_id, status, media_info, acct])

    print(f"[Audit Log] Recorded to {target_path.name} (Account: {acct}, Status: {status})")


def run_pipeline(
    force_dry_run: bool = False,
    force_live: bool = False,
    post_type: Optional[str] = None,
    in_minutes: Optional[int] = None,
    share_now: bool = False,
    media_file: Optional[str] = None,
    no_media: bool = False,
) -> None:
    """
    Runs the full Demoly.dev content generation and publishing pipeline.
    """
    # Determine execution mode
    # Default is DRY RUN. LIVE mode is active if explicitly requested or configured via env.
    if force_dry_run:
        is_live = False
    elif force_live:
        is_live = True
    else:
        is_live = LIVE_MODE and not DRY_RUN

    print("\n" + "=" * 60)
    if is_live:
        print(" [WARNING] RUNNING IN LIVE PUBLISHING MODE")
        if in_minutes:
            print(f" [SCHEDULE] Scheduled to publish in {in_minutes} minutes")
        elif share_now:
            print(" [SCHEDULE] Configured to share immediately (shareNow)")
        else:
            print(" [SCHEDULE] Adding to Buffer queue (automatic schedule)")
    else:
        print(" [SAFE] RUNNING IN DRY RUN MODE (NO POSTING WILL OCCUR)")
    print("=" * 60)

    # 1. Generate original content with Gemini
    print("\n[Step 1/3] Generating content via Gemini...")
    content: GeneratedPostModel = generate_post(
        content_type_preference=post_type,
        preferred_media_filename=media_file,
        allow_media=False if no_media else None,
    )

    # 2. Display formatted content to user
    print("\n" + "=" * 50)
    print(f" GENERATED CONTENT ({content.type.upper()})")
    print("=" * 50)
    for idx, post in enumerate(content.posts, 1):
        print(f"\n[Post #{idx}] ({len(post)} / 280 chars):")
        print(f"\"{post}\"")
    if content.media_filename:
        print(f"\n[Attached Media]: {content.media_filename}")
        if content.media_url:
            print(f"[Media URL]:      {content.media_url}")
    print("\n" + "=" * 50)

    # 3. Handle Publishing vs Dry Run
    if not is_live:
        # DRY RUN SAFETY PATH
        print("\n================================")
        print("DRY RUN RESULT")
        print("================================")
        print("Mode: DRY_RUN=true")
        print("Status: Content successfully generated & validated.")
        print("No content was sent to Buffer or published to X.")
        print("================================\n")

        log_published_post(
            content=content,
            buffer_id="DRY_RUN_NO_ID",
            status="DRY_RUN",
        )
        return

    # LIVE PUBLISHING PATH
    print("\n[Step 2/3] Publishing to Buffer...")
    buffer_client = BufferClient()

    # Determine publishing mode & custom schedule
    mode = "addToQueue"
    due_at = None
    if share_now:
        mode = "shareNow"
    elif in_minutes is not None and in_minutes > 0:
        mode = "customScheduled"
        target_time = datetime.now(timezone.utc) + timedelta(minutes=in_minutes)
        due_at = target_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    if content.type == "single":
        result = buffer_client.publish_single_post(
            text=content.posts[0],
            mode=mode,
            due_at=due_at,
            media_url=content.media_url,
        )
    else:
        result = buffer_client.publish_thread(
            posts=content.posts,
            mode=mode,
            due_at=due_at,
            media_url=content.media_url,
        )

    buffer_id = result.get("id", "UNKNOWN")
    publish_status = result.get("status", "QUEUED")
    post_due_at = result.get("due_at")

    print("\n" + "=" * 50)
    print(" LIVE PUBLISH SUCCESSFUL")
    print("=" * 50)
    print(f"Buffer Post ID: {buffer_id}")
    print(f"Buffer Status:  {publish_status}")
    if post_due_at:
        print(f"Scheduled For:  {post_due_at} (UTC)")
    if content.media_filename:
        print(f"Attached Media: {content.media_filename}")
    print("Your content has been added to Buffer for Demoly.dev X.")
    print("=" * 50 + "\n")

    # Step 3: Record in Audit Log
    status_entry = f"sent ({post_due_at})" if post_due_at else publish_status
    log_published_post(content=content, buffer_id=buffer_id, status=status_entry)


def get_optimal_engagement_slots(now_utc: Optional[datetime] = None) -> List[datetime]:
    """
    Returns 3 peak global engagement slots optimized for BOTH Indian (IST)
    and International (US / Europe) audiences:

      Slot 1 (Single Tweet): 10:00 AM IST (04:30 UTC)
              -> India morning start + Asia-Pacific workday peak.
      Slot 2 (Thread):       6:30 PM IST (13:00 UTC / 9:00 AM US-EST / 2:00 PM CET)
              -> The Global Sweet Spot: India evening commute + US East Coast start + Europe afternoon.
      Slot 3 (Media Post):   10:30 PM IST (17:00 UTC / 1:00 PM US-EST / 10:00 AM US-PST)
              -> US West Coast (Silicon Valley) morning + US East Coast afternoon + late India.
    """
    if now_utc is None:
        now_utc = datetime.now(timezone.utc)

    target_slots_utc = [(4, 30), (13, 0), (17, 0)]
    scheduled = []

    for h, m in target_slots_utc:
        candidate = now_utc.replace(hour=h, minute=m, second=0, microsecond=0)
        if candidate <= now_utc + timedelta(minutes=5):
            candidate += timedelta(days=1)
        scheduled.append(candidate)

    return scheduled


def run_daily_batch(
    force_dry_run: bool = False,
    force_live: bool = False,
    spaced: bool = False,
    share_now: bool = False,
) -> None:
    """
    Executes the full 3-post daily cadence across all configured Twitter/X accounts:
    1. Single Tweet (text-only)
    2. Thread (multi-tweet, text-only)
    3. Media Post (with authentic video or image attached)

    Supports multi-account publishing with strictly unique, persona-tailored content
    and cross-account topic deduplication.
    """
    if force_dry_run:
        is_live = False
    elif force_live:
        is_live = True
    else:
        is_live = LIVE_MODE and not DRY_RUN

    accounts = get_configured_accounts()
    if not accounts:
        accounts = [AccountConfig(id="", name="Default", persona="", target_audience="")]

    print("\n" + "=" * 65)
    print(" DEMOLY.DEV DAILY 3-POST CADENCE ENGINE (MULTI-ACCOUNT)")
    print(f" Mode: {'[LIVE PUBLISHING]' if is_live else '[SAFE DRY RUN - PREVIEW ONLY]'}")
    print(f" Accounts to Process: {len(accounts)} account(s)")
    for idx, acc in enumerate(accounts, 1):
        print(f"   [{idx}] {acc.name} (Channel: {acc.id or '[Default]'})")
    if is_live:
        if share_now:
            print(" Schedule: Publishing all posts IMMEDIATELY (shareNow)")
        elif spaced:
            print(" Schedule: Spacing 3 posts per account at peak Global + Indian windows:")
            print("           * Slot 1: 10:00 AM IST (04:30 UTC) -> Single Tweet")
            print("           * Slot 2:  6:30 PM IST (13:00 UTC / 9:00 AM EST) -> Thread")
            print("           * Slot 3: 10:30 PM IST (17:00 UTC / 10:00 AM PST) -> Media Post")
        else:
            print(" Schedule: Adding posts to Buffer posting queue")
    print("=" * 65)

    # Pre-fetch live trends & hashtags once to share across all accounts
    realtime_trends = get_realtime_trending_context()
    trending_hashtags = get_realtime_trending_hashtags()

    # Shared list of used topics across accounts in this batch to guarantee ZERO overlap
    all_used_topics: List[str] = []

    for a_idx, account in enumerate(accounts, 1):
        print("\n" + "#" * 65)
        print(f" >>> [ACCOUNT {a_idx}/{len(accounts)}] {account.name.upper()} <<<")
        if account.persona:
            print(f" Voice/Persona: {account.persona}")
        if account.target_audience:
            print(f" Target Audience: {account.target_audience}")
        print("#" * 65)

        # 1. Plan today's 3 posts with cross-account topic deduplication
        plan: DailyCadencePlan = plan_daily_cadence(
            account=account if len(accounts) > 1 or account.persona else None,
            batch_excluded_topics=all_used_topics if all_used_topics else None,
        )

        # Register topics so no other account in this run will repeat them
        for it in plan.items:
            all_used_topics.append(it.focus_topic)

        print("\n" + "-" * 60)
        print(f" STRATEGIC CADENCE PLAN FOR {account.name.upper()}:")
        print(f" {plan.trend_analysis}")
        print("-" * 60)

        # 2. Generate 3 unique posts tailored for this account
        generated_posts = []
        for idx, item in enumerate(plan.items, 1):
            print(f"\n[{idx}/3] Generating Post #{idx} [{item.format.upper()}] for {account.name}...")
            print(f"      Focus Topic: {item.focus_topic}")
            if item.trend_connection:
                print(f"      Trend/Hashtag Context: {item.trend_connection}")
            if item.preferred_media:
                print(f"      Target Media Asset: {item.preferred_media}")

            content: GeneratedPostModel = generate_planned_post(
                plan_item=item,
                cached_trends=realtime_trends,
                cached_hashtags=trending_hashtags,
                account=account,
            )
            generated_posts.append((item, content))

        # 3. Preview generated posts
        print("\n" + "=" * 65)
        print(f" ALL 3 POSTS GENERATED FOR {account.name.upper()}")
        print("=" * 65)
        for idx, (item, content) in enumerate(generated_posts, 1):
            print(f"\n--- [{account.name}] POST #{idx}: {item.format.upper()} ({content.type.upper()}) ---")
            print(f"Topic: {item.focus_topic}")
            print(f"Source Rationale: {item.source_rationale}")
            if content.media_filename:
                print(f"Attached Media: {content.media_filename}")
                if content.media_url:
                    print(f"Media URL:      {content.media_url}")

            for p_idx, post_text in enumerate(content.posts, 1):
                print(f"\n[Tweet {p_idx}/{len(content.posts)}] ({len(post_text)} / 280 chars):")
                print(f"\"{post_text}\"")
        print("\n" + "=" * 65)

        # 4. Publish or Log
        if not is_live:
            print(f"\n[{account.name}] DRY RUN: 3 posts successfully previewed (not sent to Buffer).")
            for item, content in generated_posts:
                log_published_post(
                    content=content,
                    buffer_id="DRY_RUN_NO_ID",
                    status="DRY_RUN",
                    account_name=account.name,
                )
            continue

        # Live Mode
        print(f"\nPublishing 3 posts to Buffer for {account.name} (Channel: {account.id})...")
        buffer_client = BufferClient(channel_id=account.id)
        optimal_slots = get_optimal_engagement_slots() if spaced else []

        for idx, (item, content) in enumerate(generated_posts):
            due_at = None
            if share_now:
                mode = "shareNow"
            elif spaced:
                target_time = optimal_slots[idx] if idx < len(optimal_slots) else (datetime.now(timezone.utc) + timedelta(hours=(idx + 1) * 4))
                due_at = target_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
                mode = "customScheduled"
                ist_time = target_time + timedelta(hours=5, minutes=30)
                print(f"      [Schedule Slot #{idx+1}] Target: {due_at} UTC ({ist_time.strftime('%I:%M %p')} IST)")
            else:
                mode = "addToQueue"

            print(f"\nPublishing Post #{idx+1} ({content.type}) for {account.name} via mode '{mode}'...")
            if content.type == "single":
                result = buffer_client.publish_single_post(
                    text=content.posts[0],
                    mode=mode,
                    due_at=due_at,
                    media_url=content.media_url,
                    channel_id=account.id,
                )
            else:
                result = buffer_client.publish_thread(
                    posts=content.posts,
                    mode=mode,
                    due_at=due_at,
                    media_url=content.media_url,
                    channel_id=account.id,
                )

            buffer_id = result.get("id", "UNKNOWN")
            publish_status = result.get("status", "QUEUED")
            post_due_at = result.get("due_at")
            status_entry = f"sent ({post_due_at})" if post_due_at else publish_status

            log_published_post(
                content=content,
                buffer_id=buffer_id,
                status=status_entry,
                account_name=account.name,
            )
            print(f" Post #{idx+1} ({account.name}) sent to Buffer (ID: {buffer_id}, Status: {status_entry})")
            if idx < len(generated_posts) - 1:
                time.sleep(3)

    print("\n" + "=" * 65)
    print(" ALL CONFIGURED ACCOUNTS COMPLETED SUCCESSFULLY")
    print("=" * 65 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Demoly.dev Automated X/Twitter Content System"
    )
    parser.add_argument(
        "--daily-batch",
        action="store_true",
        help="Execute the full 3-post daily cadence across all configured accounts with trend-first dynamic planning",
    )
    parser.add_argument(
        "--spaced",
        action="store_true",
        help="Space daily-batch posts across peak engagement slots instead of default Buffer queue",
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Run competitor CSV analysis and update style-guide.md",
    )
    parser.add_argument(
        "--list-channels",
        action="store_true",
        help="Fetch and display all connected Buffer social channels and Channel IDs",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Force DRY_RUN mode (never publishes, only previews)",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Run in LIVE_MODE (requires LIVE_MODE=true in .env to publish)",
    )
    parser.add_argument(
        "--type",
        choices=["single", "thread"],
        default=None,
        help="Force content type ('single' or 'thread')",
    )
    parser.add_argument(
        "--in-minutes",
        type=int,
        default=None,
        help="Schedule post to be published N minutes from now (e.g. --in-minutes 10)",
    )
    parser.add_argument(
        "--share-now",
        action="store_true",
        help="Publish immediately to X (shareNow) instead of buffering into queue",
    )
    parser.add_argument(
        "--media",
        type=str,
        default=None,
        help="Force attachment of a specific media file from assets/ (e.g. --media silent_search.mp4)",
    )
    parser.add_argument(
        "--no-media",
        action="store_true",
        help="Force post to be text-only (no image or video attached)",
    )
    parser.add_argument(
        "--scan-media",
        action="store_true",
        help="Scan assets/ for new videos/images and index them with Gemini",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Display current system configuration and safety status",
    )

    args = parser.parse_args()

    if args.status:
        print_system_status()
        return

    if args.list_channels:
        print_available_channels()
        return

    try:
        if args.scan_media:
            scan_and_index_assets()
            return

        if args.analyze:
            run_research_analysis()
            return

        if args.daily_batch:
            run_daily_batch(
                force_dry_run=args.dry_run,
                force_live=args.live,
                spaced=args.spaced,
                share_now=args.share_now,
            )
            return

        run_pipeline(
            force_dry_run=args.dry_run,
            force_live=args.live,
            post_type=args.type,
            in_minutes=args.in_minutes,
            share_now=args.share_now,
            media_file=args.media,
            no_media=args.no_media,
        )

    except KeyboardInterrupt:
        print("\n[INFO] Execution cancelled by user.")
        sys.exit(0)
    except Exception as err:
        print(f"\n{err}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

