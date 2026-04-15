# 🚀 Agent Media Team: Autonomous Marketing AI

Welcome to the **Agent Media Team**, a fully autonomous, 6-member AI marketing squad that operates entirely within a Discord Server to manage social media campaigns, generate visuals, write copy, execute code, and perform real-time SEO research. 

This README serves as both the technical documentation of the repository and a historical ledger charting every phase, paradigm shift, error encountered, and solution implemented during the initial builds, deployments, and debugging sessions.

---

## 🎭 The Team Roster
Our agency uses a specialized division of labor rather than a single generalized LLM. Supabase persists their memory, and Webhooks allow them to speak as distinct personalities inside Discord:
1. **MORGAN** *(General Manager)*: Triage, task assignment, and campaign orchestration.
2. **SCOUT** *(SEO & Research)*: Data-driven trend analysis and optimal timing recommendations.
3. **ALEX** *(Content Writer)*: Creative hooks, threads, and captions adapted per platform.
4. **PIXEL** *(Image Prompter)*: Aesthetic generation, DALL-E/Leonardo workflows.
5. **ECHO** *(Poster & Distributor)*: formatting, cross-posting, and schedule management.
6. **CIPHER** *(Tech Expert)*: GitHub interactions, README modifications, and GitHub API automation.

---

## 🏗️ Architecture & Tech Stack
*   **Core Engine**: Python 3.x
*   **Interface**: `discord.py` (Bot and Webhooks)
*   **AI Brain**: **Groq** (`llama-3.3-70b-versatile` via `AsyncGroq`)
*   **Database/Memory**: Supabase (PostgreSQL) tracking conversation history and campaign states.
*   **Server/Hosting**: Flask (for health checks) deployed on **Render**.
*   **Automation**: Playwright (for scraping/browser interactions)

---

## 📖 The Developer's Journey: Issues, Successes & Pivots

What started as a simple Discord bot evolved into a highly optimized, asynchronous AI pipeline due to deployment constraints and API hurdles. Here is the exact timeline of the architecture decisions made:

### Stage 1: Initial Construction & Webhook Spawning
**The Goal**: Build a marketing team that felt "alive" in a Discord channel.
*   **Decision**: Instead of one bot prefixing messages (e.g., `Bot: [Morgan] Hello`), we utilized Discord Webhooks via `utils/personamanager.py` to give each AI its own name, avatar, and independent voice.
*   **Success**: The team successfully assembled and triaged requests in Discord, passing data back and forth.

### Stage 2: The LLM Engine Roulettes & 402 Errors
**The Goal**: Make the agents intelligent without accruing massive hardware/API bills.
*   **Initial Setup**: We started using **Gemini / Google AI Studio**.
*   **Pivot to OpenRouter**: To get access to a broader swath of free Llama-3 endpoints, we quickly switched to OpenRouter. We pushed the changes to GitHub and Render.
*   **The Issue**: We encountered **HTTP 402 (Payment Required)** errors. OpenRouter routes to hundreds of models, but default configurations and regional locks frequently tripped billing checks even when requesting free models.
*   **The Final Pivot (Groq)**: We abandoned OpenRouter to remove billing friction entirely and switched to **Groq API**. Groq provides natively blazing-fast LPU inference entirely for free. We defaulted the system to `llama-3.3-70b-versatile`.

### Stage 3: The "Always Offline" Render Conundrum
**The Issue**: After successful deployment to Render's Free Tier, the Discord bots would periodically go offline, abandoning the discord server.
*   **The Cause**: Render spins down free web services after 15 minutes of inactivity to save compute. When the container sleeps, the Discord bot process dies.
*   **The Solution**: We integrated a Flask server in `web/app.py` running a `keep_alive()` background thread on port 10000. By exposing a `/health` endpoint, we allowed external cron services (like Cron-job.org) to ping the app every 5 minutes, permanently tricking Render into staying awake.

### Stage 4: The "Typing... but never replying" Freeze
**The Issue**: The final bug. You'd prompt Morgan, you'd see `Morgan is typing...` in Discord, but no message ever arrived. 
*   **The Cause**: Two compounding factors: 
    1. The API request was running synchronously via `requests`, effectively freezing the Discord event loop and timing out the network socket. 
    2. If the API key was missing in the Render environment, `groq` threw fatal errors that were silently swallowed in the background thread.
*   **The Solution**: 
    1. **Asynchronous Architecture**: We completely refactored `orchestrator.py` to use `AsyncGroq` and updated `main.py` to `await generate_response()`. This allowed Discord to handle background tasks seamlessly while waiting for Groq's multi-second inference.
    2. **Graceful Error Handling**: Implemented a failsafe intercept. If `GROQ_API_KEY` is completely missing or is a placeholder, the bot refuses to freeze and instead instantly replies in the Discord channel: *"❌ **SYSTEM ERROR**: Groq API Key is missing..."*

---

## 🚀 Deployment & Operations

### Pushing Updates to Render
This project follows a strict GitOps workflow:
1.  All code changes (API swaps, engine migrations) were done locally.
2.  Changes were grouped into granular commits (e.g., `git commit -m "Scale to Groq..."`).
3.  Pushed to `main` via `git push`.
4.  Render intercepts the webhook and automatically triggers a new isolated Docker/Python container build to apply updates. 

### Running Locally (Development)
If you wish to spin up the agency locally:
1. Clone the repo and configure your `.env` (copying from `.env.example`).
2. Run `pip install -r requirements.txt`.
3. Obtain API keys for **Groq** (AI), **Supabase** (DB), and **Discord** (Bot Token).
4. Run `python main.py`

*Enjoy your fully autonomous, extremely fast, financially cost-free marketing engine!*
