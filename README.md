# Demoly.dev Automated X/Twitter Content System

An automated, beginner-friendly, zero-to-low-cost system that generates high-impact X (Twitter) content for **Demoly.dev** using **Google Gemini AI**, extracts strategic insights from competitor research, and schedules/publishes posts via **Buffer GraphQL API**.

---

## 📖 Table of Contents
1. [What This Project Does](#1-what-this-project-does)
2. [How the Architecture Works](#2-how-the-architecture-works)
3. [How Gemini Works in This System](#3-how-gemini-works-in-this-system)
4. [How Buffer Works in This System](#4-how-buffer-works-in-this-system)
5. [How Python Connects Everything](#5-how-python-connects-everything)
6. [Folder Structure](#6-folder-structure)
7. [Step-by-Step Local Setup (Windows & VS Code)](#7-step-by-step-local-setup-windows--vs-code)
8. [How to Get Your Gemini API Key (Free)](#8-how-to-get-your-gemini-api-key-free)
9. [How to Configure Buffer & Connect Twitter/X](#9-how-to-configure-buffer--connect-twitterx)
10. [Where to Put API Keys (.env)](#10-where-to-put-api-keys-env)
11. [How to Discover Your Twitter Channel ID](#11-how-to-discover-your-twitter-channel-id)
12. [Testing Safe Mode (DRY_RUN)](#12-testing-safe-mode-dry_run)
13. [How LIVE_MODE Works](#13-how-live_mode-works)
14. [How to Analyze Competitor Posts](#14-how-to-analyze-competitor-posts)
15. [How to Push to GitHub](#15-how-to-push-to-github)
16. [How to Add GitHub Secrets](#16-how-to-add-github-secrets)
17. [How to Manually Run on GitHub Actions](#17-how-to-manually-run-on-github-actions)
18. [How to Enable Daily Automation (Cron)](#18-how-to-enable-daily-automation-cron)
19. [Troubleshooting Common Errors](#19-troubleshooting-common-errors)

---

## 1. What This Project Does
- Reads competitor post performance data from `data/competitor_posts.csv`.
- Uses **Google Gemini** to analyze what resonates with developers and compiles a living `style-guide.md`.
- Generates **original**, developer-focused single posts or multi-post threads adhering strictly to the Demoly.dev brand voice.
- **Validates** every post to guarantee it is under X's 280-character limit, avoids corporate hype, and has zero fake statistics.
- Sends approved posts directly into your **Buffer queue** via Buffer's official GraphQL API.
- Safeguards your accounts with **Default Dry Run** mode so nothing is posted until you are ready.
- Automates execution daily using **GitHub Actions**.

---

## 2. How the Architecture Works

```text
[Competitor & Client CSV]
           │
           ▼
[Gemini Research Analyzer] ──► [style-guide.md]
                                      │
                                      ▼
                           [Gemini Content Generator]
                                      │
                                      ▼
                        [Python Validation Layer]
                           (Under 280 chars? Original?)
                                      │
              ┌───────────────────────┴───────────────────────┐
              ▼                                               ▼
     [DRY_RUN Mode: Safe]                            [LIVE_MODE: Active]
     - Prints to terminal                            - Calls Buffer GraphQL API
     - Appends to published_posts.csv                - Adds to Demoly.dev X queue
     - 0 API calls to Buffer                         - Appends to published_posts.csv
```

---

## 3. How Gemini Works in This System
We use the official **Google GenAI SDK** (`google-genai`) with model `gemini-2.5-flash`:
1. **Analysis Mode**: Gemini reviews the collected likes, reposts, and formats from competitor data and summarizes structural patterns (hooks, CTA, length).
2. **Generation Mode**: Gemini receives `style-guide.md` and outputs **Structured JSON** conforming to a strict schema (`type`: `"single" | "thread"`, `posts`: `[...]`). This eliminates messy formatting errors.

---

## 4. How Buffer Works in This System
Buffer is a social media management platform that connects directly to your X/Twitter account.
- **Why Buffer?** Direct X API access has steep pricing tiers and strict restrictions. Buffer has a free tier that allows scheduling posts safely.
- **Official GraphQL API**: We interact with Buffer's modern endpoint (`https://api.buffer.com`).
- **Threads**: For multi-tweet threads, our client packages all tweets into the `metadata.twitter.thread` field so Buffer publishes them in sequence as replies.

---

## 5. How Python Connects Everything
Python serves as the automated pipeline coordinator:
1. Loads environment keys safely using `python-dotenv` (never prints secrets).
2. Prompts Gemini and validates the JSON response with `pydantic`.
3. Verifies post lengths and character safety.
4. If in `DRY_RUN` mode, previews the post in the console.
5. If in `LIVE_MODE`, sends an authenticated GraphQL mutation to Buffer.
6. Records a permanent audit row in `data/published_posts.csv`.

---

## 6. Folder Structure

```text
demoly-x-automation/
│
├── src/
│   ├── __init__.py               # Python package marker
│   ├── config.py                 # Safe environment loader & safety checks
│   ├── gemini_client.py          # Google Gemini SDK caller with structured output
│   ├── research_analyzer.py      # Competitor CSV parser & style guide generator
│   ├── content_generator.py      # Prompt builder & post validator
│   ├── buffer_client.py          # Buffer GraphQL API client & channel discovery
│   └── main.py                   # Main CLI entry point & audit logger
│
├── data/
│   ├── competitor_posts.csv      # Input: Public competitor posts for pattern research
│   └── published_posts.csv       # Output: Permanent audit log of generated/published posts
│
├── prompts/
│   ├── analysis_prompt.txt       # Instructions for Gemini research analysis
│   └── generation_prompt.txt     # Instructions for Gemini post generation
│
├── style-guide.md                # Living Demoly.dev voice, hooks, and content rules
├── requirements.txt              # Required Python libraries
├── .env.example                  # Template for API keys (safe to commit)
├── .gitignore                    # Prevents secrets and cache from reaching Git
├── README.md                     # You are here!
│
└── .github/
    └── workflows/
        └── daily-post.yml        # GitHub Actions automated workflow
```

---

## 7. Step-by-Step Local Setup (Windows & VS Code)

### Step 1: Open VS Code Terminal
In VS Code, press `` Ctrl + ` `` (Backtick) or click **Terminal ➔ New Terminal**.

### Step 2: Create and Activate a Python Virtual Environment
Type this in VS Code Terminal:
```powershell
python -m venv venv
.\venv\Scripts\activate
```
*(You will see `(venv)` appear on the left side of your terminal prompt.)*

### Step 3: Install Required Dependencies
Type this in VS Code Terminal:
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 8. How to Get Your Gemini API Key (Free)
1. Go to **[Google AI Studio](https://aistudio.google.com/app/apikey)**.
2. Sign in with your Google account.
3. Click **Create API Key**.
4. Copy your API key (it begins with `AIzaSy...`).

---

## 9. How to Configure Buffer & Connect Twitter/X
1. Create a free account at **[Buffer.com](https://buffer.com)** if you don't have one.
2. Connect your **Demoly.dev Twitter/X account** in Buffer under **Channels**.
3. Go to the Buffer Developer Portal: **[https://buffer.com/developers/api](https://buffer.com/developers/api)**.
4. Generate a **Personal Access Token** and copy it.

---

## 10. Where to Put API Keys (.env)

### Step 1: Create your `.env` file
Type this in VS Code Terminal:
```powershell
copy .env.example .env
```

### Step 2: Open `.env` and fill in your keys
Open the newly created `.env` file in VS Code. It will look like this:
```ini
GEMINI_API_KEY=AIzaSyYourRealGeminiKeyHere
BUFFER_ACCESS_TOKEN=your_real_buffer_token_here
BUFFER_CHANNEL_ID=
DRY_RUN=true
LIVE_MODE=false
```
> [!CAUTION]
> Never share or commit your `.env` file. It is listed in `.gitignore` to protect you.

---

## 11. How to Discover Your Twitter Channel ID
Buffer needs to know *which* social channel to post to. We built an automated helper for this!

Type this in VS Code Terminal:
```powershell
python -m src.buffer_client --list-channels
```
**Example output:**
```text
Found 1 connected channel(s):

CHANNEL ID                     | SERVICE    | ACCOUNT NAME
-----------------------------------------------------------------
6543210abcdef1234567890a       | twitter    | @DemolyDev
-----------------------------------------------------------------

[RECOMMENDATION] Copy your Twitter Channel ID above and add to your .env:
   BUFFER_CHANNEL_ID=6543210abcdef1234567890a
```
Copy that ID and paste it into your `.env` file:
```ini
BUFFER_CHANNEL_ID=6543210abcdef1234567890a
```

---

## 12. Testing Safe Mode (DRY_RUN)
By default, **DRY_RUN is enabled**. Running the script will:
- Read `style-guide.md`
- Prompt Gemini to generate content
- Verify character limits
- Print the formatted post/thread in your terminal
- Log the draft to `data/published_posts.csv`
- **Make 0 publishing calls to Buffer**

Type this in VS Code Terminal:
```powershell
python -m src.main
```

You can also test specific formats:
```powershell
# Force a single post
python -m src.main --type single

# Force a multi-post thread
python -m src.main --type thread

# Check configuration status
python -m src.main --status
```

---

## 13. How LIVE_MODE Works
Only when you have verified the dry runs and are ready to actually publish or queue posts to X:

### Step 1: Update `.env`
Change the flags in your `.env` file:
```ini
DRY_RUN=false
LIVE_MODE=true
```

### Step 2: Run with live flag
Type this in VS Code Terminal:
```powershell
python -m src.main --live
```
The post will be added to your Buffer publishing queue and logged as `QUEUED` in `data/published_posts.csv`.

---

## 14. How to Analyze Competitor Posts
You can add new competitor/client tweets to `data/competitor_posts.csv`.

Whenever you update the CSV and want Gemini to refresh your style guide:
Type this in VS Code Terminal:
```powershell
python -m src.main --analyze
```
This re-analyzes the data and updates `style-guide.md` automatically.

---

## 15. How to Push to GitHub

Type these in VS Code Terminal:
```powershell
# 1. Initialize Git (if not already done)
git init

# 2. Add files (your .env is automatically ignored)
git add .

# 3. Commit your files
git commit -m "feat: initial demoly-x-automation setup"

# 4. Set main branch
git branch -M main

# 5. Link to your GitHub repo (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/demoly-x-automation.git

# 6. Push to GitHub
git push -u origin main
```

---

## 16. How to Add GitHub Secrets
GitHub Actions cannot read your local `.env` file. You must add your keys as **Encrypted Secrets**:

1. Open your repository in your browser on GitHub.
2. Click this on GitHub: **Settings** (top tab of your repo).
3. In the left sidebar, click **Secrets and variables ➔ Actions**.
4. Click the green button: **New repository secret**.
5. Add each of these secrets:
   - Name: `GEMINI_API_KEY` | Value: *(Paste your Gemini key)*
   - Name: `BUFFER_ACCESS_TOKEN` | Value: *(Paste your Buffer token)*
   - Name: `BUFFER_CHANNEL_ID` | Value: *(Paste your Buffer Channel ID)*
   - Name: `LIVE_MODE` | Value: `false` *(Set to `true` only when you want automated live publishing!)*
   - Name: `DRY_RUN` | Value: `true` *(Keep `true` while testing)*

---

## 17. How to Manually Run on GitHub Actions
You can test the GitHub Actions workflow at any time without waiting for a scheduled hour:

1. Click this on GitHub: **Actions** tab at the top.
2. In the left sidebar, click **Demoly.dev Daily X Content**.
3. Click the **Run workflow** dropdown on the right.
4. Select your content type (e.g. `random`, `single`, or `thread`).
5. Click the green **Run workflow** button.
6. Click into the running job to watch Python generate content in the live execution logs!

---

## 18. How to Enable Daily Automation (Cron)
Once you are confident with the results:

1. Open `.github/workflows/daily-post.yml` in VS Code.
2. Find lines 17-19 and **uncomment** the schedule:
   ```yaml
   schedule:
     - cron: '0 13 * * *'
   ```
   *(This runs automatically every day at 13:00 UTC / 6:30 PM IST / 9:00 AM EDT).*
3. Update GitHub Secret `LIVE_MODE` to `true` and `DRY_RUN` to `false`.
4. Commit and push:
   ```powershell
   git add .github/workflows/daily-post.yml
   git commit -m "enable daily scheduled publishing"
   git push
   ```

---

## 19. Troubleshooting Common Errors

### Error: `GEMINI_API_KEY is missing!`
- **Cause**: The `.env` file doesn't exist or `GEMINI_API_KEY` is blank.
- **Fix**: Run `copy .env.example .env` and paste your key from Google AI Studio.

### Error: `The 'google-genai' package is not installed`
- **Cause**: Dependencies haven't been installed in your active virtual environment.
- **Fix**: Run `pip install -r requirements.txt`.

### Error: `401 Unauthorized` from Buffer
- **Cause**: Your `BUFFER_ACCESS_TOKEN` has expired or was copied incorrectly.
- **Fix**: Re-generate a Personal Access Token at [buffer.com/developers/api](https://buffer.com/developers/api).

### Error: `CSV is missing required columns`
- **Cause**: `data/competitor_posts.csv` is missing one of the 10 required headers.
- **Fix**: Ensure your CSV header includes:
  `Account,Account Type,Post,Likes,Reposts,Replies,Views,Date,URL,Post Type`

### Post exceeds 280 characters
- **Behavior**: The built-in validator in `content_generator.py` automatically detects posts longer than 280 characters, logs a warning, and truncates cleanly at a word boundary before sending to Buffer.
