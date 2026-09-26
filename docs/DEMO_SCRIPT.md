# Demo Script — Developer Onboarding Copilot

> **Duration:** 3–5 minutes  
> **Audience:** Hackathon judges  
> **Goal:** Show how the copilot turns a stranger's repo into an interactive learning journey

---

## Pre-demo Setup (do before presenting)

1. Start the backend: `python -m mcp_server.main`
2. Start the frontend: `cd frontend && npm start`
3. Open `http://localhost:3000` in Chrome
4. Have DevTools closed (clean look)
5. Set `LLM_API_KEY` in your terminal

---

## Script

### [0:00 – 0:30] Hook — The Problem

> _"Every developer has been there — you join a new team, clone an unfamiliar repo, and spend your first week just trying to understand where everything is. We asked: what if an AI could guide you through that process the same way a senior colleague would?"_

---

### [0:30 – 1:00] Landing Page

- Open `http://localhost:3000`
- Point at the three-step value proposition: **Understand → Learn → Contribute**

> _"The Developer Onboarding Copilot transforms any public GitHub repository into a personalised learning path. Let me show you."_

- Click **Try Demo Repository** (loads pre-configured data instantly)

---

### [1:00 – 1:45] Analysis Screen

> _"Watch as the copilot analyses the codebase in real time — detecting the tech stack, mapping the structure, finding entry points, and finally calling the AI to generate a plan specifically for this developer's experience level and role."_

- Point at each step as it ticks off
- When it completes: _"Your onboarding path is ready."_

---

### [1:45 – 2:30] Dashboard

> _"The dashboard gives you a bird's-eye view. You can see the detected tech stack, your overall progress, and a day-by-day breakdown of the plan the AI generated."_

- Point at: tech badges, progress bar, day cards
- Click on **Day 1** to show task previews

> _"Every plan is personalised — a beginner front-end developer gets a different Day 1 than an experienced back-end engineer."_

- Click **Ask the Codebase →**

---

### [2:30 – 3:15] Chat Interface

> _"This is the heart of the experience. Instead of grep-ing through files or reading stale docs, you can just ask."_

- Type: **"Where is the main entry point?"**
- Wait for response — point at the file reference in the answer

> _"Notice it references actual files — not generic advice. The context window contains the full repository structure."_

- Type: **"How do I add a new API endpoint?"**

> _"Developers get step-by-step instructions with code examples. Every answer is grounded in this specific codebase."_

---

### [3:15 – 3:45] First Contribution

- Navigate to **First Contribution**

> _"When the developer is ready to contribute, we analyse the repository for safe, well-scoped starter tasks — things like adding a test, improving an error message, or adding input validation."_

- Show one card — point at difficulty badge, time estimate, acceptance criteria
- Click **Start This Task →** to open Validation

---

### [3:45 – 4:15] Validation

> _"The developer pastes their code, we run it through AI code review plus optional test and lint checks, and they get structured feedback — score, strengths, improvement suggestions — before they even open a PR."_

- Paste a short code snippet
- Click **Run Validation**
- Point at the score and feedback sections

---

### [4:15 – 4:45] PR Preparation

- Navigate to **PR Preparation**

> _"And when they're ready to submit, the copilot generates the entire pull request description — title following conventional commits, a structured What / Why / How / Testing body, and a pre-merge checklist. One click to copy."_

- Fill in 2–3 file names
- Click **Generate PR Description**
- Click **Copy PR Template**

---

### [4:45 – 5:00] Close

> _"In under five minutes, a developer who had never seen this codebase now understands its architecture, has completed their first task, and has a PR ready to open. That's what the Developer Onboarding Copilot does — powered by IBM watsonx and built with IBM Bob."_

---

## Key Talking Points

- **IBM watsonx integration** — the `AIProvider` class routes all AI calls through watsonx; swap one env variable to change providers
- **MCP protocol** — all tools are exposed as standard MCP endpoints for watsonx Orchestrate
- **IBM Bob** — entire project built using Bob as the development AI assistant
- **Personalisation** — same repo produces different plans for beginner vs senior, frontend vs backend
- **Privacy-safe** — no repository code is stored; only structure metadata is sent to the AI

## Anticipated Questions

| Question | Answer |
|----------|--------|
| _"Does it support private repos?"_ | MVP is public repos; auth token support is the first post-hackathon feature |
| _"How long does analysis take?"_ | 5–15 seconds for plan generation; the repo analysis is immediate |
| _"What models does it support?"_ | Any OpenAI-compatible API — GPT-4o-mini is default; set `LLM_BASE_URL` for watsonx |
| _"Is it integrated with GitHub?"_ | Repository ingestion (Dev A) fetches via GitHub REST API |
| _"What's the architecture?"_ | FastAPI backend + React frontend; MCP server exposes all AI tools |

---

*Made with IBM Bob*
