# Demoly Visual Assets

Place your authentic Demoly product media in these subdirectories:

- `assets/videos/`: Screen recording demo clips (`.mp4`, H.264 recommended, 15–45 seconds).
- `assets/images/`: High-resolution UI screenshots, feature graphics, or comparison cards (`.png`, `.jpg`, `.svg`).

## Automated Indexing
After placing any new video or image here, run:
```bash
python -m src.media_manager --scan
```
Gemini will automatically analyze each clip/screenshot, summarize what happens on screen, and index it into `data/media_catalog.json` so daily tweets and threads can automatically feature your real product media!
