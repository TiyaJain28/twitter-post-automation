"""
media_manager.py
================================================================================
Manages authentic Demoly videos (.mp4) and images (.png, .jpg) in assets/.
- Scans assets/videos and assets/images
- Catalogs metadata in data/media_catalog.json
- Automatically analyzes media using Gemini multimodal capabilities
- Resolves public URLs for Buffer media publishing
================================================================================
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Any

from src.config import (
    ASSETS_DIR,
    VIDEOS_DIR,
    IMAGES_DIR,
    MEDIA_CATALOG_PATH,
    MEDIA_BASE_URL,
)
from src.gemini_client import GeminiClient

VIDEO_EXTS = {".mp4", ".webm", ".mov"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp"}


def load_media_catalog() -> List[Dict[str, Any]]:
    """Loads the registered media catalog from data/media_catalog.json."""
    if not MEDIA_CATALOG_PATH.exists():
        return []
    try:
        with open(MEDIA_CATALOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Warning] Failed to load media catalog: {e}")
        return []


def save_media_catalog(catalog: List[Dict[str, Any]]) -> None:
    """Saves the media catalog to data/media_catalog.json."""
    MEDIA_CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MEDIA_CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)


def _upload_catbox(path: Path) -> Optional[str]:
    """Uploads a local image or media file to catbox.moe CDN."""
    import requests
    try:
        with open(path, "rb") as f:
            res = requests.post(
                "https://catbox.moe/user/api.php",
                data={"reqtype": "fileupload"},
                files={"fileToUpload": (path.name, f)},
                timeout=60,
            )
        if res.status_code == 200 and res.text.strip().startswith("http"):
            return res.text.strip()
    except Exception as e:
        print(f"[Media Uploader] Catbox upload error: {e}")
    return None


def _upload_to_cdn(local_path: Path, is_video: bool = False) -> Optional[str]:
    """
    Uploads a local file to a public CDN that Buffer can ingest.
    Uses catbox.moe for fast public hosting.
    """
    print(f"[Media Uploader] Uploading {local_path.name} to CDN...")
    url = _upload_catbox(local_path)
    if url:
        print(f"[Media Uploader] Uploaded successfully: {url}")
        return url
    print("[Media Uploader] CDN upload failed.")
    return None


# Simple in-process URL cache to avoid re-uploading the same file in one run
_url_cache: dict = {}



def resolve_media_url(filename: str) -> Optional[str]:
    """
    Resolves the public HTTP(S) URL for a media file.
    If MEDIA_BASE_URL is set (e.g. 'https://raw.githubusercontent.com/owner/repo/main'):
      - For videos: {MEDIA_BASE_URL}/assets/videos/{filename}
      - For images: {MEDIA_BASE_URL}/assets/images/{filename}
    If filename is already an http(s) URL, returns it as-is.
    If running locally without MEDIA_BASE_URL, uploads to temporary public host so Buffer can ingest it.
    """
    if not filename:
        return None
    if filename.startswith("http://") or filename.startswith("https://"):
        return filename

    path_obj = Path(filename)
    ext = path_obj.suffix.lower()
    is_video = ext in VIDEO_EXTS

    if MEDIA_BASE_URL:
        import urllib.parse
        base = MEDIA_BASE_URL.rstrip("/")
        subfolder = "videos" if is_video else "images"
        safe_name = urllib.parse.quote(path_obj.name)
        return f"{base}/assets/{subfolder}/{safe_name}"

    # Check local filesystem
    local_path = None
    target_dir = VIDEOS_DIR if is_video else IMAGES_DIR
    potential_file = target_dir / path_obj.name
    if potential_file.exists():
        local_path = potential_file
    elif path_obj.exists():
        local_path = path_obj

    if local_path and local_path.exists():
        url = _upload_to_cdn(local_path, is_video=is_video)
        if url:
            return url

    # Return local relative path indicator if no public base URL is configured
    return f"file://assets/{'videos' if is_video else 'images'}/{path_obj.name}"


def analyze_media_file_with_gemini(file_path: Path, media_type: str) -> Dict[str, Any]:
    """
    Calls Gemini multimodal vision to inspect the actual video or image bytes
    and generate accurate tags, UI summary, and capability mappings.
    """
    clean_name = file_path.stem.replace("_", " ").replace("-", " ")
    prompt = f"""
You are cataloging an authentic Demoly product asset for social media publishing on X.
Asset Name: {file_path.name}
Asset Type: {media_type}

Inspect this visual asset and identify the exact Demoly UI elements, screens, or features shown (e.g. landing page, dashboard, recording controls, DOM search, masking, client handover):
Provide a valid JSON response with this exact schema:
{{
  "summary": "1-sentence description of the exact UI features, dashboard elements, or workflow shown in this {media_type}",
  "capabilities": ["Specific Feature 1", "Specific Feature 2"],
  "recommended_hook_angle": "Natural hook suggestion to introduce this visual proof on X"
}}
Return ONLY valid JSON.
"""
    try:
        from google.genai import types
        client = GeminiClient()
        raw_client = client._get_client()

        ext = file_path.suffix.lower()
        mime_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".mp4": "video/mp4",
            ".webm": "video/webm",
        }
        mime = mime_map.get(ext, "image/png")

        with open(file_path, "rb") as f:
            media_bytes = f.read()

        part = types.Part.from_bytes(data=media_bytes, mime_type=mime)
        res = raw_client.models.generate_content(
            model=client.model_name,
            contents=[part, prompt]
        )
        raw_text = res.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()

        data = json.loads(raw_text)
        return {
            "summary": data.get("summary", f"Demoly interface showing {clean_name}"),
            "capabilities": data.get("capabilities", ["Demoly Web Feature"]),
            "recommended_hook_angle": data.get("recommended_hook_angle", f"Here is how this works in Demoly:"),
        }
    except Exception as e:
        return {
            "summary": f"Demoly {media_type} interface for {clean_name}.",
            "capabilities": ["Product Feature"],
            "recommended_hook_angle": f"Watch how this works in Demoly:",
        }


def scan_and_index_assets() -> int:
    """
    Scans assets/videos and assets/images for new media files
    and indexes them into data/media_catalog.json.
    """
    catalog = load_media_catalog()
    existing_files = {entry.get("filename") for entry in catalog if "filename" in entry}
    added_count = 0

    # Ensure directories exist
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Scan Videos
    for v_file in VIDEOS_DIR.iterdir():
        if v_file.is_file() and v_file.suffix.lower() in VIDEO_EXTS:
            if v_file.name not in existing_files:
                print(f"[Media Indexer] Found new video: {v_file.name}. Analyzing with Gemini...")
                analysis = analyze_media_file_with_gemini(v_file, media_type="video")
                catalog.append({
                    "id": f"vid_{len(catalog) + 1}",
                    "filename": v_file.name,
                    "type": "video",
                    "file_size_kb": round(v_file.stat().st_size / 1024, 1),
                    "summary": analysis["summary"],
                    "capabilities": analysis["capabilities"],
                    "recommended_hook_angle": analysis["recommended_hook_angle"],
                })
                existing_files.add(v_file.name)
                added_count += 1

    # 2. Scan Images
    for i_file in IMAGES_DIR.iterdir():
        if i_file.is_file() and i_file.suffix.lower() in IMAGE_EXTS and not i_file.name.startswith("."):
            if i_file.name not in existing_files:
                print(f"[Media Indexer] Found new image: {i_file.name}. Analyzing with Gemini...")
                analysis = analyze_media_file_with_gemini(i_file, media_type="image")
                catalog.append({
                    "id": f"img_{len(catalog) + 1}",
                    "filename": i_file.name,
                    "type": "image",
                    "file_size_kb": round(i_file.stat().st_size / 1024, 1),
                    "summary": analysis["summary"],
                    "capabilities": analysis["capabilities"],
                    "recommended_hook_angle": analysis["recommended_hook_angle"],
                })
                existing_files.add(i_file.name)
                added_count += 1

    if added_count > 0:
        save_media_catalog(catalog)
        print(f"[Media Indexer] Successfully indexed {added_count} new media asset(s) to {MEDIA_CATALOG_PATH.name}.")
    else:
        print(f"[Media Indexer] No new media assets found. Catalog is up to date ({len(catalog)} total assets).")

    return added_count


def format_media_catalog_for_prompt() -> str:
    """
    Formats the registered media catalog into concise context for Gemini's prompt.
    Returns a string describing available videos and images.
    """
    catalog = load_media_catalog()
    if not catalog:
        return "None available yet. (Generate standard text-only post or thread)."

    lines = ["Available authentic product media you can attach:"]
    for item in catalog:
        m_type = item.get("type", "media").upper()
        fname = item.get("filename", "")
        summary = item.get("summary", "")
        caps = ", ".join(item.get("capabilities", []))
        lines.append(f"- [{m_type}] Filename: \"{fname}\" | Shows: {summary} | Capabilities: {caps}")

    lines.append("\nRULE: If you select a media file above, set 'media_filename' to its exact filename and write your tweet copy to introduce or highlight what is shown on screen.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Demoly Media Manager")
    parser.add_argument("--scan", action="store_true", help="Scan assets/ for new videos/images and index them")
    parser.add_argument("--list", action="store_true", help="List all indexed media assets")
    args = parser.parse_args()

    if args.scan:
        scan_and_index_assets()
    elif args.list:
        catalog = load_media_catalog()
        print(f"\nRegistered Media Assets ({len(catalog)} total):")
        for item in catalog:
            print(f"- [{item.get('type', '').upper()}] {item.get('filename')}: {item.get('summary')}")
        print()
    else:
        scan_and_index_assets()


if __name__ == "__main__":
    main()
