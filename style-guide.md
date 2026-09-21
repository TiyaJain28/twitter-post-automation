# Demoly X Content Style Guide & Authority Manual

## 1. Product Identity & Core Truths (Reference: demoly_faq.md)
**Demoly** (https://demoly.dev) is an AI-powered browser screen recorder, client handover platform, and visual bug reporting tool built for **tech agencies, web development studios, and QA teams**.

### The Technical Breakthrough: DOM Capture vs. Pixel Video
- **Traditional Screen Recorders (Loom, native OS, Google Drive)**: Record raw 30–60 fps pixel video streams and run basic speech-to-text audio transcription. If a creator didn't speak on camera, the recording is a black box.
- **Demoly's Innovation**: Captures the browser **DOM (Document Object Model)** hierarchy, layout state transitions, and user events (clicks, form inputs, route changes).
- **Why It Matters**:
  1. **Visual AI Search on Silent Videos**: Clients can search for buttons, forms, and settings even if the creator never spoke a single word (FAQ Q6, Q20, Q75).
  2. **80%–85% Timestamp Accuracy**: Demoly pairs DOM tree indexing with targeted visual frame snapshots on demand, jumping clients directly to the exact second (FAQ Q72, Q79).
  3. **Element-Level Dynamic Masking**: Redactions attach to DOM elements, staying masked across dynamic scrolling and page changes (FAQ Q57, Q58).
  4. **Non-Destructive Storage**: Edits and trims are saved as a metadata overlay layer; the raw underlying recording is permanently preserved and reversible by admins (FAQ Q54, Q59).
  5. **Zero-Friction Link Sharing**: Viewers can watch, comment, and query the embedded AI assistant on public links **without creating a Demoly account** (FAQ Q63).
  6. **Unlimited Everything**: Unlimited recording duration, unlimited file sizes, unlimited recordings per workspace on all plans (FAQ Q43, Q101).

---

## 2. Audience & Psychology
- **Primary ICP**: Agency Founders, Technical Directors, Product Managers (PMs), and Lead QA Engineers at web dev studios and software agencies.
- **Secondary ICP**: SaaS product teams (interactive onboarding/docs), DevRel / developer educators (searchable coding tutorials), internal HR/Ops teams (portal walkthroughs) (FAQ Q24-Q26).
- **Their Mindset**: They are busy professionals losing billable hours to repeat support calls and vague bug reports. They respect candor, technical precision, and tangible operational relief. They despise generic marketing buzzwords ("revolutionize", "synergy", "paradigm shift").

---

## 3. Daily 3-Post Cadence & Trend-First Dynamic Source Selection

Every day, the system executes a **3-Post Daily Cadence**:
1. **A Single Tweet** (text-only punchy takeaway, contrarian hook, or debate question)
2. **A Thread** (text-only multi-tweet architectural deep dive or framework)
3. **A Post with Photo/Video** (authentic demo media attached with targeted intro copy)

### The Trend-First Decision Engine
Instead of following a rigid day-of-the-week schedule or locking sources to rigid formulas, the daily planner runs a **Trend-First Assessment**:
1. **Live Trend Analysis**: First evaluates real-time Twitter trending hashtags and tech discussions (Hacker News, Dev.to).
2. **Format Matching**: Determines which format (Single Tweet, Thread, or Media Post) is best suited to capitalize on today's top trend.
3. **Dynamic Source Selection**: Evaluates what topics and sources make the highest strategic impact for that specific day:
   - **Real-Time Trends**: Timely trend-jacking and community discussions.
   - **Topic Bank ([data/topics_bank.json](file:///c:/Users/HP/OneDrive/Desktop/twitter/data/topics_bank.json))**: Curated agency friction points and workflows.
   - **Demoly FAQ ([data/demoly_faq.md](file:///c:/Users/HP/OneDrive/Desktop/twitter/data/demoly_faq.md))**: Architectural proof (DOM capture, element masking, public zero-login links, MCP server).
   - **Authentic Media Catalog ([data/media_catalog.json](file:///c:/Users/HP/OneDrive/Desktop/twitter/data/media_catalog.json))**: Real product screenshots and demo videos.
4. **Deduplication Guarantee**: Programmatically inspects [data/published_posts.csv](file:///c:/Users/HP/OneDrive/Desktop/twitter/data/published_posts.csv) so all 3 posts explore completely fresh angles without repeating recent topics.

---

## 4. Strict Thread Architecture Rules (Mandatory)

1. **STRICT ZERO THREAD LABELS & NO "BREAKDOWN 👇"**: NEVER write "Thread", "A thread:", "Thread 🧵", "Breakdown", "Breakdown 👇", or use pointing-down emojis (👇). Let the first post stand naturally on its own and flow organically into the narrative without generic clickbait phrasing.
2. **Dynamic Thread Length (Topic-Dependent, typically 3 to 7 Posts)**:
   Threads are NOT locked to 5 posts. The post count must naturally adapt to the topic's depth and scope:
   - **Focused Contrast / Quick Workflow Shift (3–4 posts)**: Hook -> Friction/Root cause -> Demoly mechanism & proof -> Discussion question.
   - **Deep Technical / Handover Framework / Architecture (5–7 posts)**: Hook -> Detailed status-quo friction -> Root cause / legacy limitations -> Demoly DOM mechanism -> Practical workflow transformation -> Before vs. After outcome -> Engaging CTA.
   - **Rule of Substance**: Never insert filler tweets just to meet an arbitrary length. Every post in the thread must deliver a sharp, standalone insight. Always end with an interactive question or high-engagement CTA.
3. **Natural Post Length**: No artificial word or character limits. Let each post flow naturally and completely according to the depth of the idea, without premature truncation or filler.
4. **Visual Spacing & Clean Line Breaks**: Never write a dense, continuous wall of text on a single line. Use clean double line breaks (`\n\n`) between hooks, problem statements, and key takeaways. Place list items on separate lines so posts have breathing room on mobile feeds.
5. **Factual Integrity**: Draw strictly from the 109 Q&As in `data/demoly_faq.md`. Never invent fake percentage stats or fake customer logos.
6. **Trending Twitter Hashtags (1–3 Relevant Tags)**:
   - Always incorporate 1 to 3 relevant trending hashtags from Twitter/X.
   - **Single Post**: Place 1–3 hashtags at the very bottom after a clean double line break (`\n\n#AI #buildinpublic`).
   - **Thread**: Place 1–3 hashtags ONLY at the end of the final concluding tweet. Intermediate tweets remain clean.
   - **Strict Character Limits**: Every tweet with hashtags must remain strictly under 280 characters.
   - **No Spam**: Never exceed 3 hashtags per post.

---

## 5. Viral & Trending Tech Angles to Weave In

- **"Vibe Coding" Reality Check (Cursor, Claude 3.7, Karpathy)**: Writing code with AI is now lightning fast; client handovers and bug verification are where agencies stall.
- **Model Context Protocol (MCP)**: AI agents (Claude Code, Cursor) need structured DOM states and timestamps to debug frontend bugs autonomously.
- **Death of Discovery Calls & "Book a Demo" Forms**: Clients and buyers want self-serve interactive queries over 30-minute meetings.
- **Subscription Fatigue & $20/Seat Backlash**: Calling out expensive per-seat screen recorders that don't even search visual screens.

---

## 6. High-Converting Hook Formats (Swipe File)

- **The Anti-Meeting Hook**: *"Today, we're killing the 'can we quickly jump on a call?' message. No more 30-minute meetings explaining a feature you already recorded."*
- **The Tool Contrast**: *"Loom searches your words. Demoly searches your screen. If you never spoke on camera, Loom can't find the button. Here is why that matters:"*
- **The Founder Frustration**: *"We delivered 45 walkthrough videos for an enterprise client. Within a week, we lost 15 hours to repeat calls asking questions already in the recordings. That is why we built Demoly."*
- **The Hidden Cost**: *"Tech agencies lose 2 to 4 hours per team member every week answering questions already explained in client handover videos. Here is why:"*
- **The Contrarian Reality**: *"Everyone is talking about 'vibe coding' a SaaS in 2 hours. But nobody mentions: you can't vibe-explain a web app to a non-technical client."*
- **The Architecture Truth**: *"A screen recorder that refuses to record your desktop OS is not broken—it's by design. Here is the engineering decision behind Demoly:"*

---

## 7. Interactive Engagement Patterns (Driving Replies & Bookmarks)

- **The "Pick Your Nightmare" Dilemma**:
  *"Pick the worst agency scenario:  
  A) Client asking for a 30-min call on Monday to ask where the billing tab is  
  B) QA filing a ticket saying 'it doesn't work' with a blurry screenshot  
  C) Uploading a 100MB video to Google Drive that fails to stream  
  D) Paying $20/seat for Loom and clients still requesting calls"*
- **The "Unpopular Opinion" Hot Take**:
  *"Unpopular opinion: If a developer needs more than 60 seconds to reproduce a staging bug, the QA workflow is fundamentally broken."*
- **The "Honest Question" Metric**:
  *"Be honest: how many billable hours did your agency lose this week to meetings that could have been an interactive 2-minute recording?"*
