# Demoly Knowledge Base & Product Reference (FAQ)
A comprehensive, categorized FAQ knowledge base compiled from founder interviews, product specifications, architectural details, and roadmap insights for **Demoly** (https://www.demoly.dev).
---
## Table of Contents
1. [Category 1: Company Origin, Problem & Founder Insights (11 Questions)](#category-1-company-origin-problem--founder-insights)
2. [Category 2: Product Definition, Core Value & Positioning (12 Questions)](#category-2-product-definition-core-value--positioning)
3. [Category 3: Target Personas, Use Cases & Workflows (8 Questions)](#category-3-target-personas-use-cases--workflows)
4. [Category 4: Recording Capabilities, Mechanics & Boundaries (19 Questions)](#category-4-recording-capabilities-mechanics--boundaries)
5. [Category 5: Editing, Non-Destructive Storage & Element-Level Masking (11 Questions)](#category-5-editing-non-destructive-storage--element-level-masking)
6. [Category 6: Publishing, Sharing, Access Control & Privacy (9 Questions)](#category-6-publishing-sharing-access-control--privacy)
7. [Category 7: AI Architecture, Visual Indexing & Search Engine (16 Questions)](#category-7-ai-architecture-visual-indexing--search-engine)
8. [Category 8: AI Capabilities, Multi-Video Search & Documentation Roadmap (11 Questions)](#category-8-ai-capabilities-multi-video-search--documentation-roadmap)
9. [Category 9: Bug Reporting, Developer Tooling & MCP Integration (4 Questions)](#category-9-bug-reporting-developer-tooling--mcp-integration)
10. [Category 10: Pricing, Plans & Workspace Administration (4 Questions)](#category-10-pricing-plans--workspace-administration)
11. [Category 11: Security, Data Handling & Failure Edge Cases (5 Questions)](#category-11-security-data-handling--failure-edge-cases)
---
## Category 1: Company Origin, Problem & Founder Insights
### Q1: What is the origin story of Demoly and what specific problem triggered its creation?
**A:** Demoly was created by the co-founders of **Creative Pie**, a tech agency that has delivered web applications and AI-native products for over 85 global clients. While delivering complex platforms (notably a large enterprise web application for a law firm requiring 35–60 handover walkthrough videos), a severe operational bottleneck occurred.
Clients and their staff would not watch 10-minute videos to find a single answer, nor did they know which video contained a specific feature. Consequently, clients repeatedly requested live Google Meet calls to ask questions about features already explained in the videos. Each call consumed 15–30 minutes, totaling **2 to 4 hours per team member each week** answering repetitive queries. This friction led the founders to conclude that handover recordings should not just be passive videos—they must actively answer client questions.

### Q2: How did the agency handle handovers and bug reports before building Demoly?
**A:** Previously, the workflow relied on two primary tools:
1. **Google Drive:** Team members used native OS screen recorders (e.g., Mac screen recorder) with voiceover, uploaded video files to Google Drive folders, and shared folder links.
2. **Loom:** The team paid $20/seat monthly to record and share links.
There was no standardized, visual-plus-technical workflow for QA bug reporting or client handoff support.

### Q3: What were the specific shortcomings of Loom for client handovers?
**A:**
1. **Transcript-Only Search:** Loom’s search only indexed transcribed audio. If a feature or UI element (such as a logout button or input field) was shown on screen but not explicitly spoken aloud, Loom could not find it.
2. **Cost & Limitations:** Loom charged $20/month per seat and imposed recording limits on free tiers without solving the core searchability issue.
3. **Passive Consumption:** Clients still had to review entire recordings or request meetings when search failed.

### Q4: What were the specific shortcomings of Google Drive?
**A:**
1. **File Streaming Limits:** Google Drive fails to stream video files exceeding ~100 MB directly in the browser; clients had to download entire video files locally before viewing.
2. **Lack of In-Video Search:** Google Drive has no visual search. Even with Gemini integrations (costing ~$29/month), AI processing is restricted to speech transcripts and cannot inspect visual screen content.
3. **Friction for Non-Technical Clients:** Non-technical clients found downloading and organizing multiple large video files cumbersome.

### Q5: Why wasn't written documentation alone sufficient to solve the problem?
**A:** Manual documentation is extremely time-consuming to create, requiring developers/PMs to capture screenshots, write sequential steps, and maintain documents as the UI changes. Furthermore, end users frequently prefer visual demonstrations over reading text. Recording a walkthrough is much faster; Demoly's strategy is to capture video instantly and let AI automatically generate documentation from the recording.

### Q6: What was the original technical concept of Demoly before the AI search was introduced?
**A:** The initial idea focused on recording the **browser Document Object Model (DOM)** rather than standard video pixel streams. Because web applications have many static frames, capturing DOM state changes rather than constant 30–60 fps video drastically reduces file size, decreases database storage costs, and eliminates large video uploads.

### Q7: When and how did the "Talk to the Video" AI search feature emerge?
**A:** The concept emerged directly from the continuous client demand for Google Meet walkthroughs. The founders realized that since all product answers already existed inside the recorded footage, clients should be able to query the video directly via conversational AI instead of scheduling calls with agency developers.

### Q8: What user behaviors and inefficiencies does Demoly eliminate?
**A:**
1. Eliminates client hunting across dozens of video links or downloading large video files.
2. Eliminates the need to watch an entire 10-minute video to find a 10-second instruction.
3. Eliminates repetitive, time-consuming support meetings and demo calls.
4. Eliminates vague, text-only bug reports by combining video proof with technical browser logs.

### Q9: What are the primary and secondary problems Demoly solves?
**A:**
- **Primary Problem:** Enables product teams to record handover walkthroughs once and allows clients to get instant, timestamped answers to their queries via AI search without human intervention.
- **Secondary Problem:** Streamlines internal bug reporting across QA, PMs, developers, and designers by recording visual browser interactions alongside deep technical diagnostic data.

### Q10: What problem does Demoly deliberately choose NOT to solve?
**A:** Demoly deliberately avoids being a generic, full-OS desktop screen recorder. It does not record desktop operating system windows, native software applications, or mobile phone screens. It focuses strictly on **browser-based web applications**, capturing DOM data, console logs, network calls, and web interactions.

### Q11: What is the fundamental insight behind Demoly that competitors miss?
**A:** Competitors treat screen recording as generic pixel capture or voice transcription across all industries. Tech agencies delivering web applications require more than passive video: they need deep web context (DOM states, API calls, console logs, auto-generated documentation) and conversational visual search so videos can answer questions autonomously even when speech is absent.

---
## Category 2: Product Definition, Core Value & Positioning
### Q12: What is Demoly in one sentence?
**A:** Demoly is an AI-powered walkthrough and bug reporting platform built for tech agencies to record browser-based product handovers that clients can interactively search and query using AI.

### Q13: Complete the value proposition: "Demoly allows you to..."
**A:**
- Demoly allows you to deliver comprehensive product handover videos without wasting hours re-explaining the same features in client meetings.
- Demoly allows your recorded walkthroughs to answer client questions autonomously, even when you did not speak during the recording.
- Demoly allows you to record unlimited videos without time, seat, or project limits.
- Demoly allows QA and PM teams to report web bugs with visual proof combined with console logs and network data without relying on fragmented tools.

### Q14: What category does Demoly belong to?
**A:** Demoly defines a unified category combining **Client Handoff**, **Visual & Technical Bug Reporting**, and **AI Product Documentation**.

### Q15: What tools does Demoly replace?
**A:**
1. **Loom** (and generic screen recorders) for web product demos and client handovers.
2. **Google Drive** for video storage, organization, and distribution.
3. **Manual support/demo meetings** previously needed to guide clients through web apps.
4. **Fragmented QA bug reporting tools** that capture only static screenshots or text descriptions without browser diagnostics.

### Q16: What tools does Demoly complement rather than replace?
**A:**
1. **AI Coding Assistants & Agents (Cursor, Claude Code, Antigravity):** Demoly exposes an MCP (Model Context Protocol) server so bug reports, console logs, and network traces can be fed directly to AI coding agents for autonomous debugging.
2. **Website & No-Code Platforms (Webflow, frontend frameworks):** Demoly will allow auto-generated product walkthrough docs to be embedded directly into client portals and knowledge bases.

### Q17: What would you never position Demoly as?
**A:** Demoly is never positioned as a generic desktop screen recorder.

### Q18: What is the simplest workflow Demoly enables?
**A:** Record a browser walkthrough of a web app, generate a shareable link, send it to a client, and let the client ask the video any question to jump to the exact timestamp and get an answer.

### Q19: What is the most powerful workflow Demoly enables?
**A:** An agency records 50+ silent or narrated walkthrough videos of a massive web application. Demoly indexes all DOM elements, actions, and speech across the workspace. A client can query anything (e.g., *"How do I configure role permissions?"*), and Demoly identifies the precise action, visual state, and timestamp across the entire video library, providing an instant step-by-step answer.

### Q20: What single feature immediately differentiates Demoly from Loom?
**A:** The **DOM-native AI Visual Search**: Loom only searches spoken words in transcripts, whereas Demoly inspects the actual DOM elements, visual UI states, and on-screen actions. Demoly can find features, forms, and buttons even if the creator never spoke a single word.

### Q21: What feature makes users say "I actually need this"?
**A:** The ability to record and share handovers quickly, mask sensitive PII/passwords across dynamic screens in one click, trim pauses directly in the browser, and let the video autonomously handle repetitive client inquiries.

### Q22: What feature is easiest for users to understand immediately?
**A:** One-click screen recording via the Chrome extension and instant link sharing with an embedded AI chat assistant.

### Q23: What aspect of Demoly is most difficult to explain to customers?
**A:** The distinction between traditional pixel screen recording and **DOM-based capture**. Customers often ask why Demoly cannot record desktop OS apps outside the browser, which requires explaining that Demoly's AI search and lightweight storage depend on inspecting browser DOM trees, web layouts, and network events.

---
## Category 3: Target Personas, Use Cases & Workflows
### Q24: Who is Demoly fundamentally built for?
**A:** Demoly is built specifically for **Tech Agencies, Web Development Studios, Product Teams, and QA Teams** delivering web applications.

### Q25: Who are the primary user personas within a tech agency?
**A:**
1. **Product Managers (PMs):** Review staging builds, report visual/functional bugs with context to devs/designers, and record structured handovers for clients.
2. **Quality Assurance (QA) Engineers:** Test web apps and record reproducible bug reports including console logs, network errors, and visual flows.
3. **Developers & Technical Leads:** Consume visual and technical bug reports to resolve issues rapidly, and record technical walkthroughs.
4. **Agency Founders & Account/Client Relationship Managers:** Deliver client project folders, monitor handover status, and reduce post-launch support overhead.

### Q26: Who are secondary and emerging personas that can get value from Demoly?
**A:**
1. **SaaS Companies:** Creating interactive, AI-searchable product documentation, changelogs, and user onboarding tutorials.
2. **HR & Operations Teams:** Recording internal employee onboarding, portal walkthroughs, and HR tool tutorials with AI-searchable answers.
3. **Educators & Technical Instructors:** Recording coding courses and browser-based software tutorials where students can query the video directly instead of repeatedly asking the instructor.

### Q27: Who records the video versus who watches/searches the video?
**A:**
- **Creators (Recorders):** Developers, PMs, QA engineers, founders, and account managers.
- **Consumers (Viewers/Searchers):** Clients and their operational teams, internal developers resolving bugs, or new employees undergoing onboarding.

### Q28: What is the exact step-by-step workflow for QA Bug Reporting in Demoly?
**A:**
1. The PM or QA engineer spots an issue, layout bug, or typo while testing a web application.
2. They click the Demoly Chrome extension to start recording the browser tab.
3. They demonstrate the bug, add a comment pinned to the exact timestamp explaining the expected vs. actual behavior.
4. They share the video link with the developer and UI designer.
5. The developer reviews the visual playback (and in upcoming updates, inspects attached console logs, network calls, and API responses).
6. The developer resolves the issue, replies or comments within the Demoly link, and marks the task complete.

### Q29: What is the exact step-by-step workflow for Client Project Handover?
**A:**
1. The agency finishes a web application and creates a dedicated project folder for the client inside Demoly.
2. The team records a series of walkthrough videos covering all product features, modules, and administrative settings.
3. Sensitive client data or credentials on screen are masked using Demoly’s one-click redaction tool.
4. The agency shares the folder link (or invites client emails with restricted viewer permissions).
5. When the client or their staff need to perform a task (e.g., *"How do I add a new team member?"* or *"How do I change my billing info?"*), they type the question into the Demoly AI search bar.
6. Demoly answers the question step-by-step and navigates the client directly to the exact video timestamp demonstrating that workflow.

### Q30: How does Demoly adapt to different agency team sizes?
**A:**
- **Small Agencies (1–5 members):** Founders and developers handle both recording and client handovers directly.
- **Mid-Tier Agencies (5–25 members):** PMs and QA engineers handle staging bug reports and handover video creation.
- **Large-Scale Agencies / Enterprises:** Dedicated client relationship managers, QA teams, and lead developers manage segregated client workspaces and role-based permissions.

### Q31: What feedback has Demoly received from its initial 10–15 early users?
**A:** Early agency users highlighted massive time savings in client handovers. Users also surfaced unexpected applications, such as educators requesting Demoly to host browser-based coding tutorials so students can query the videos directly via AI rather than emailing instructors.

---
## Category 4: Recording Capabilities, Mechanics & Boundaries
### Q32: What happens immediately after a user signs up for Demoly?
**A:** The user lands on the main dashboard, which displays a **Start Recording** button. Clicking this redirects them to the Chrome Web Store to install the Demoly browser extension. Once installed, recording can begin immediately.

### Q33: Is there an onboarding wizard before recording?
**A:** In the initial V1 release, there is only a direct sign-up (email/password or Google Single Sign-On). Interactive onboarding and product tour flows are scheduled after V1.

### Q34: Can a user record without installing the Chrome extension?
**A:** No. The Chrome extension is mandatory because it captures the browser DOM, tab audio, and web events.

### Q35: What browsers are officially supported today, and what is on the roadmap?
**A:**
- **Supported Today:** Google Chrome.
- **Roadmap:** Mozilla Firefox, Microsoft Edge, and Brave.

### Q36: What elements can Demoly record today?
**A:**
- Active browser tab
- Multiple browser tabs (within the same browser session)
- Entire browser window
- Microphone speech / voiceover
- Audio playing inside the browser tab (system/tab audio)
- Video media playing within the web tab
- Cursor movement and visual cursor navigation indicators
- Mouse clicks and user interactions (typing, scrolling, form inputs)

### Q37: How does Demoly handle multi-tab recording and tab switching?
**A:** Users can switch between tabs, open new tabs, or close tabs during a recording session. Demoly smoothly continues capturing the active browser tab within that window.

### Q38: Can a user switch between different browser applications (e.g., Chrome to Safari) during one recording?
**A:** No. Recording is bound to the active browser instance where the extension is running.

### Q39: What happens if the user refreshes the page or navigates to a new URL during recording?
**A:** Demoly continues recording smoothly across page reloads and URL navigations within the active tab.

### Q40: What happens if the web application crashes during recording?
**A:** Demoly continues capturing whatever state is rendered inside the browser tab.

### Q41: What happens if the internet connection drops during recording?
**A:**
- **Current Behavior:** The unsaved recording in progress may be lost if the network drops before upload completion.
- **Roadmap Behavior:** Demoly will cache chunks locally in browser storage (`localStorage`/`IndexedDB`). When connection restores, users will be shown a preview to review, resume, and upload.

### Q42: Is recording data stored locally first or streamed during recording?
**A:** Data is buffered locally in the browser runtime and streamed/uploaded progressively as the recording proceeds.

### Q43: Are there limits on recording duration, file size, or number of recordings?
**A:**
- **Duration Limit:** None (unlimited recording duration on all plans).
- **File Size Limit:** None (unlimited file size).
- **Video Count Limit:** Unlimited recordings per workspace across both Free and Pro plans.

### Q44: Can users pause, resume, or cancel a recording?
**A:**
- **Cancel Without Saving:** Supported today.
- **Pause & Resume:** Not available in V1; actively in development for upcoming UX updates.

### Q45: How do microphone permissions and audio inputs work?
**A:** Demoly requests microphone access through standard browser permissions. It automatically detects and uses the default system/browser microphone (including Bluetooth headsets/headphones). Changing audio input devices is managed via system/browser defaults; an in-app device picker is planned.

### Q46: Can users record silently without microphone audio?
**A:** Yes. Silent recordings are fully supported. Demoly's DOM visual indexing ensures the AI search functions with complete accuracy even when no voiceover is recorded.

### Q47: Can Demoly record system audio without microphone audio?
**A:** In upcoming audio updates, Demoly will support recording browser tab audio independently or simultaneously with the microphone. It will strictly capture browser-generated audio, not external operating system audio.

### Q48: How does Demoly handle embedded videos, iframes, and PDFs inside a webpage?
**A:**
- **Embedded Videos:** Captured and recorded.
- **Embedded Iframes & PDFs:** Currently face capture limitations due to cross-origin browser sandbox restrictions. Support for nested iframes and embedded documents is actively being addressed.

### Q49: Are browser pop-ups, password fields, and notifications recorded?
**A:** Everything rendered inside the browser tab viewport is captured. However, creators can use Demoly's **Masking/Redaction Tool** post-recording to obscure passwords, API keys, and sensitive PII with one click before publishing.

### Q50: Why is Demoly strictly browser-only rather than full desktop?
**A:** Demoly's core intelligence relies on DOM tree analysis, layout state transitions, network logs, and web runtime events. This depth of indexing is only possible within a browser architecture. Desktop-wide capture would dilute the product into a heavy, commoditized pixel-recorder without DOM intelligence.

---
## Category 5: Editing, Non-Destructive Storage & Element-Level Masking
### Q51: What video editing functionality is available today?
**A:**
1. **Trimming / Cutting:** Removing unwanted start, end, or middle sections (e.g., pauses, mistakes, load times).
2. **Element-Level Masking (Redaction):** Obscuring sensitive UI areas, PII, passwords, and API credentials.
3. **Timestamp Commenting:** Pinning text comments to specific timecodes.
4. **Cursor Highlight Animation:** Enabling visual cursor tracking indicators.

### Q52: When does trimming occur in the workflow?
**A:** Trimming is performed immediately after recording in the Demoly web editor before the final version is processed and published.

### Q53: Can users make multiple cuts and delete sections from the middle of a video?
**A:** Yes. Users can define multiple timestamp cut points, delete middle portions, and Demoly automatically stitches the remaining sections together seamlessly.

### Q54: Is editing destructive, or are original raw recordings preserved?
**A:** Editing is **completely non-destructive**. Demoly saves edits as a metadata overlay layer applied over the raw underlying recording data in the database. Workspace administrators can revert any edits and restore the original raw recording at any time.

### Q55: What happens when a user edits an already published video?
**A:** The edits save automatically, and the changes reflect instantly on the original shared URL. The creator does not need to generate or distribute a new link.

### Q56: Does editing trigger AI re-indexing?
**A:** Yes. When an edited video is saved, Demoly automatically re-processes and re-indexes both the transcript and the visual DOM data so that timestamps and AI search results align with the edited timeline.

### Q57: How does Demoly's element-level masking (redaction) work?
**A:** Redaction is performed in the post-recording editor. Rather than applying a dumb static blur box over pixel coordinates, Demoly attaches the mask to the **DOM object/element**.
If the page scrolls, navigates, or the element changes position on screen, the mask dynamically tracks and stays attached to that specific element throughout the video.

### Q58: Can a single mask obscure an element across multiple screens?
**A:** Yes. Masking a specific element or sensitive field once will keep that item obscured whenever and wherever it appears in the recording.

### Q59: Is redaction permanent or reversible?
**A:** Redaction is non-destructive and editable within the creator's workspace editor. If an admin unmasks an element and saves, it becomes visible again. However, viewers accessing the published video only see the redacted presentation layer and cannot inspect or recover the hidden content.

### Q60: Can redactions be applied to specific timestamps or elements?
**A:** Users can pause at any timestamp in the editor and select specific UI components, input fields, API keys, or page sections to redact.

### Q61: What is the fundamental difference between Trimming and Masking in Demoly?
**A:**
- **Trimming:** Removes temporal chunks (time ranges) from the video timeline (e.g., deleting silences or mistakes).
- **Masking:** Obscures spatial regions/DOM elements across the timeline while preserving the surrounding video flow.

---
## Category 6: Publishing, Sharing, Access Control & Privacy
### Q62: What publishing and sharing modes exist in Demoly?
**A:**
1. **Public Sharing:** Generates a public URL accessible to anyone with the link.
2. **Private Workspace Sharing:** Restricts video access exclusively to members of the workspace.
3. **Restricted Email Sharing:** Restricts access to specified email addresses who must log in to view.

### Q63: Can someone view and interact with a public Demoly video without an account?
**A:** Yes. Anyone opening a public Demoly link can watch the video, read comments, and fully utilize the conversational AI search without creating or logging into a Demoly account.

### Q64: What does "Private" mean in Demoly?
**A:** A private video cannot be accessed via a standalone link by external users. It requires the viewer to authenticate with an authorized email account that has been granted explicit viewing permissions or belongs to the parent workspace.

### Q65: Can access permissions be revoked after sharing a link?
**A:** Yes. If a workspace admin removes an email address or team member from the access list, that user immediately loses access; reopening the link will display an unauthorized error.

### Q66: What workspace roles and permissions are supported?
**A:**
- **Admin:** Full organization management, billing, role assignment, project creation, video deletion, and raw video restoration.
- **Editor:** Can record, edit, trim, mask, publish, and delete assigned videos.
- **Viewer:** Read-only access to view recordings, search via AI, and leave timestamped comments.

### Q67: Can viewers download the video files?
**A:** Not in V1. A dedicated video download feature is currently on the roadmap.

### Q68: Will creators be able to prevent viewers from downloading videos?
**A:** Yes. An admin/creator toggle will allow users to disable video downloads on a per-video or workspace level once downloading is released.

### Q69: Are public Demoly links indexed by search engines?
**A:** Public links currently do not enforce `noindex` restrictions and can be indexed. However, Demoly is tailored for client handoffs rather than public SEO hosting; privacy controls allow teams to make videos strictly private whenever needed.

---
## Category 7: AI Architecture, Visual Indexing & Search Engine
### Q70: What AI models power Demoly's backend intelligence?
**A:** Demoly utilizes a multi-model architecture:
- **DeepSeek:** Powers large language model (LLM) reasoning, text processing, transcript understanding, and conversational QA.
- **Google Gemini:** Powers vision processing, multimodal image understanding, and visual frame analysis.
*(Note: Underlying AI model providers are internal architectural details and not marketed publicly).*

### Q71: What data streams are processed and indexed by Demoly's AI?
**A:**
1. Speech audio transcripts (when audio is present)
2. DOM structure, code hierarchies, and text nodes
3. OCR / on-screen rendered text
4. Mouse clicks, movements, and user interactions
5. Timestamped layout state changes
6. Video metadata
7. High-resolution visual screenshots captured at specific event timestamps

### Q72: How does Demoly's Visual Indexing work without consuming massive bandwidth?
**A:** Demoly does **not** process heavy video pixel streams frame-by-frame. Instead, it continuously indexes textual and layout changes from the DOM tree. When a user asks a question that requires visual spatial verification (e.g., verifying a color, diagram, or unlabelled graphic), the system captures and analyzes a targeted screenshot from that exact DOM timestamp. This hybrid approach provides full visual intelligence while keeping processing fast and efficient.

### Q73: Give an example of a query that ONLY visual/DOM indexing can answer (where transcripts fail).
**A:** A creator records a user creation workflow and fills out a form on screen while talking about general settings, never mentioning the word "email."
- **Transcript-only tool:** Cannot answer *"What fields are required to invite a user?"*
- **Demoly:** Inspects the captured DOM/visual state of the form, detects the `Email Address (*required)` field, and provides the correct answer with the exact timestamp.

### Q74: Give an example of a query where speech transcripts are essential.
**A:** A creator demonstrates a scrollable dashboard containing 100 users, but only 15 are visible on screen. If the creator verbally explains *"We have active clients like Acme Corp and Globex on this tier,"* Demoly uses the speech transcript to answer questions about Acme Corp even though the name was scrolled out of view.

### Q75: How does Demoly handle recordings with zero audio or speech?
**A:** Demoly relies entirely on its DOM extraction engine. It analyzes buttons, alt text, headings, input labels, division structures, navigation events, and visual state changes to index the entire recording.

### Q76: What UI components and elements can Demoly's AI understand?
**A:** Demoly recognizes buttons, navigation bars, dropdown menus, input forms, modals, tables, dashboards, analytical charts, images, embedded video players, and custom web elements.

### Q77: Can Demoly detect and understand sequential workflows?
**A:** Yes. Demoly tracks sequential events (e.g., *1. Open Settings -> 2. Click Team -> 3. Select Invite -> 4. Assign Admin Role*). When both DOM events and audio transcripts exist, sequence recognition is highly reliable; with DOM-only silent recordings, the LLM reconstructs sequences with ~50–60% baseline confidence.

### Q78: Can the AI answer questions about the state of the web application at a specific second?
**A:** Yes. Because DOM states are tied to precise timestamps, the AI can describe the exact state of the UI at any point in the recording.

### Q79: How accurate are Demoly's timestamp references in AI search?
**A:** Timestamps are currently **80% to 85% accurate**. When a feature is discussed or displayed multiple times across a video, Demoly provides a primary match along with secondary candidate timestamps.

### Q80: What happens when the AI cannot find an answer?
**A:** Demoly evaluates confidence scores. If confidence is low, it avoids asserting false facts, states that the information could not be verified with certainty, and suggests the closest matching timestamp or related workflow found in the recording.

### Q81: What causes AI hallucinations and how does Demoly mitigate them?
**A:**
- **Causes:** Hallucinations typically arise when a topic is mentioned repeatedly across different timestamps with slight variations, or when questions are overly vague and lack context.
- **Mitigation:** Demoly consolidates ambiguous matches into a structured response presenting multiple verified timestamp links for the user to choose from.

### Q82: How should users formulate questions to get the most accurate answers from Demoly?
**A:** Users should ask specific, goal-oriented questions referencing the exact feature, screen name, or action (e.g., *"How do I export the monthly invoicing report from the billing tab?"* rather than *"How do reports work?"*).

### Q83: Does the AI assistant maintain conversational context for follow-up questions?
**A:** Yes. Within an active chat session, Demoly retains context, enabling users to ask progressive follow-up questions (e.g., *"What button was clicked first?"* followed by *"What happened after that?"*). Starting a new chat resets the conversational context.

### Q84: What are the known AI limitations in the current version?
**A:**
1. **Large Workspace Context Limits:** In massive projects with 50–100+ videos, searching across all videos simultaneously can experience context degradation.
2. **Language Support:** Currently optimized strictly for English.
3. **Silent Complex Sequences:** Silent DOM-only recordings with intricate multi-branch logic have lower sequence inference accuracy than narrated recordings.

### Q85: What languages are supported by the AI today and what is planned?
**A:** English is the only officially supported language in V1. Multilingual transcription and conversational querying (e.g., querying in Spanish, Russian, or Uzbek) are on the product roadmap.

---
## Category 8: AI Capabilities, Multi-Video Search & Documentation Roadmap
### Q86: Can Demoly search and answer queries across multiple videos simultaneously?
**A:** Yes. If a user has permission to view an entire project folder or workspace, the AI search can evaluate all videos in that folder to answer cross-video questions.

### Q87: Can Demoly compare two different recordings?
**A:** Yes. Users can mention or paste the names of two specific videos in the chat prompt, and the AI will analyze and compare differences between the demonstrated workflows. A dedicated UI tagging system for multi-video comparison is in development.

### Q88: Can Demoly automatically generate written documentation from a video?
**A:** Automated documentation generation is in active development for post-V1 releases. It will transform recorded walkthroughs into structured, step-by-step Standard Operating Procedures (SOPs) and handover guides.

### Q89: What will Demoly's auto-generated documentation contain?
**A:**
- Formatted step-by-step written instructions
- Timestamp references for each phase
- High-resolution UI screenshots extracted at key action moments
- Visual indicators (e.g., highlighted click points and cursor paths)

### Q90: What export formats will be supported for generated documentation?
**A:** Documentation will be exportable as **PDF** and **DOCX (Microsoft Word)** files, as well as editable directly inside Demoly’s web editor.

### Q91: Will users be able to edit AI-generated documentation?
**A:** Yes. Users will have full editing control to modify text, rearrange steps, replace screenshots, and customize layouts.

### Q92: Can documentation be generated or regenerated after a video is edited?
**A:** Yes. Documentation generation will be a standalone, on-demand action that can be executed or regenerated at any time, even after videos have been trimmed or updated.

### Q93: Can Demoly answer "How do I perform X?" in addition to "Where is X located?"
**A:** Yes. Demoly synthesizes full action recipes explaining how to complete tasks step-by-step, accompanied by direct timestamp links to where each step is demonstrated.

### Q94: Can Demoly summarize an entire video?
**A:** Yes. Video summarization is live in the production application today, generating instant overviews of demonstrated features.

### Q95: Can Demoly automatically extract a list of all features shown in a video?
**A:** Yes. Users can prompt the AI to extract an itemized catalog of all features, tools, and configurations demonstrated in a single video or across an entire client project.

### Q96: Can Demoly automatically detect UI bugs or anomalies during recording?
**A:** Automated anomaly detection is on the roadmap. When implemented, Demoly will automatically flag console errors, unhandled exceptions, and failed 4xx/5xx API network calls that occur during a recording session.

---
## Category 9: Bug Reporting, Developer Tooling & MCP Integration
### Q97: How does Demoly improve technical bug reporting compared to screenshots or Slack?
**A:** Traditional bug reporting requires taking screenshots, writing manual reproduction steps, and manually copying console logs. Demoly captures the exact visual interaction on screen while automatically recording background browser metadata, giving developers full reproduction context in a single link.

### Q98: What technical diagnostic data will Demoly capture for developers?
**A:** On the developer roadmap, Demoly will record:
- Browser console logs (`console.log`, `console.error`, `console.warn`)
- Network inspection tabs (HTTP requests, payloads, response codes, latencies)
- API failure traces
- Active DOM hierarchies and runtime errors

### Q99: What is Demoly's MCP (Model Context Protocol) Server integration?
**A:** Demoly is building an **MCP Server** that connects directly to AI coding environments such as **Cursor, Antigravity, and Claude Code**. When a QA engineer records a bug in Demoly, the MCP server feeds the video timestamps, DOM states, console errors, and network payloads directly to the developer's AI coding agent, allowing the agent to diagnose and fix the bug with zero manual transcription.

### Q100: How do developers collaborate with QA and PMs on reported bugs inside Demoly?
**A:** Developers can open the shared Demoly link, review pinned timestamp comments, inspect the exact DOM state at the moment of failure, reply with clarifying comments, and mark the issue as resolved.

---
## Category 10: Pricing, Plans & Workspace Administration
### Q101: What are Demoly's pricing tiers and plan structures?
**A:** Demoly offers three pricing tiers:
1. **Free Plan:**
- Unlimited number of video recordings
- Unlimited recording duration per video
- Single-seat access (no team member invites)
- Limited AI searches and search history
2. **Pro Plan (Per Seat):**
- Unlimited video recordings & duration
- Multi-seat team collaboration (add PMs, developers, QA)
- Unlimited AI searches and query history
- Available on monthly or annual subscription billing
3. **Enterprise Plan (Custom Organization):**
- Unlimited organization-wide seats and workspaces
- Dedicated support, custom billing, and tailored security controls
- Managed via Demoly sales

### Q102: What is the billing model?
**A:** Pro plans operate on a recurring monthly or annual SaaS subscription. Enterprise plans are customized based on agency volume and requirements.

### Q103: How do project folders and workspace permissions function?
**A:** Agencies can create dedicated folders per client (e.g., `Client_LawFirm_Alpha`). Folders can be shared globally with the client organization or restricted to specific client team members with Viewer-only access.

### Q104: Can team members delete recordings?
**A:** Yes. Authorized creators and workspace admins can permanently delete recordings from their workspace.

---
## Category 11: Security, Data Handling & Failure Edge Cases
### Q105: How is user and recording data secured?
**A:**
- All recording and DOM metadata is stored in secure, private cloud server environments.
- Video and client interaction data is encrypted at rest and in transit within Demoly’s databases.
- Deletion requests permanently remove video assets and associated DOM index records.

### Q106: How are Chrome extension permissions scoped?
**A:** The Chrome extension requests standard tab capture and audio permissions required to read active tab DOM trees and microphone input. Users retain control to mask passwords and proprietary data before publishing.

### Q107: What happens if a recording or server processing fails?
**A:** Demoly displays an explicit failure notification to the user. Internal system error logs alert the Demoly engineering team to investigate, and users can reach out via built-in support channels for manual recovery assistance.

### Q108: Can redacted information ever be inspected or recovered by unauthorized viewers?
**A:** No. While raw underlying DOM data is retained in the private database for workspace admins to undo edits, the public viewer presentation layer strips redacted data completely. External viewers cannot inspect the DOM or unmask redacted elements.

### Q109: What is the long-term future vision for Demoly?
**A:** Demoly aims to become the comprehensive **operating system for agency client handoffs and technical QA**:
1. **End-to-End Handover Hub:** Interactive video repositories paired with auto-generated, synchronized documentation.
2. **Integrated Client Support Ticketing:** Clients raise tickets directly against recorded video SOPs.
3. **Autonomous Bug Remediation:** Visual bug recordings coupled with MCP connections to AI coding agents to detect, reproduce, and auto-fix frontend and backend defects seamlessly.
