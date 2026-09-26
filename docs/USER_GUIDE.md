# User Guide — Developer Onboarding Copilot

## Overview

The Developer Onboarding Copilot helps you get productive in any unfamiliar codebase, faster. This guide walks through each screen of the application.

---

## Step 1: Start — Landing Page (`/`)

When you open the app you'll see the landing page with two options:

- **Start Onboarding** — enter your own GitHub repository URL
- **Try Demo Repository** — load a pre-configured demo to explore features instantly

---

## Step 2: Repository Input (`/input`)

Fill in the form:

| Field | Description |
|-------|-------------|
| **GitHub URL** | Public repository URL (e.g. `https://github.com/owner/repo`) |
| **Experience Level** | Beginner / Intermediate / Advanced — affects plan complexity |
| **Role** | Frontend / Backend / Full Stack / Data / DevOps — affects which modules are prioritised |
| **Goal** _(optional)_ | What do you want to accomplish? e.g. "Add a new REST endpoint" |

Click **Analyse Repository** to proceed.

---

## Step 3: Analysis Screen (`/analyze`)

Watch as the copilot:
1. Connects to the repository
2. Detects the tech stack
3. Maps the directory structure
4. Identifies entry points
5. Finds test frameworks
6. Builds your personalised onboarding plan

This step calls the AI and typically takes 5–15 seconds. You will be redirected automatically when ready.

---

## Step 4: Dashboard (`/dashboard`)

Your central hub showing:

- **Repository info** — name, role, experience level
- **Overview** — plain-English summary of the project
- **Tech stack badges** — detected languages and frameworks
- **Overall progress bar** — completed tasks / total tasks
- **Day cards** — each day of your plan with task previews
- **Quick action buttons** — jump to Codebase Map, Chat, Tasks, or Contributions

Click **Continue Onboarding →** to go to your plan detail.

---

## Step 5: Codebase Map (`/map`)

_(Implemented by Developer A)_

Browse the directory tree, expand modules, and click **"Explain this to me"** on any module for an AI explanation.

---

## Step 6: Onboarding Plan (`/plan`)

_(Implemented by Developer A)_

Interactive day-by-day checklist. Check off tasks as you complete them — the dashboard progress bar updates in real time.

---

## Step 7: Guided Tasks (`/tasks`)

_(Implemented by Developer A)_

Task cards include:
- **Objective** — what you'll accomplish
- **Files to explore** — where to look
- **Hints** — progressive hints (Hint 1 → Hint 2 → Solution)
- **Ask AI** button — opens the chat pre-loaded with task context
- **Validate** button — opens the Validation panel

---

## Step 8: Chat with the Codebase (`/chat`)

Ask any question about the repository in natural language:

- _"Where is the authentication logic?"_
- _"How do I add a new API endpoint?"_
- _"What does `src/utils/parseConfig.ts` do?"_

Responses include:
- File path references
- Fenced code blocks with syntax highlighting
- Step-by-step explanations

**Tip:** Use the quick-action buttons to insert common questions instantly.

---

## Step 9: Validation (`/tasks` → Validate button)

After completing a task:

1. Paste your code or diff into the text area
2. Optionally enable **Run tests check** and **Run lint check**
3. Click **Run Validation**

The panel shows:
- ✓ / ✕ result per check
- Overall score (0–100)
- AI feedback, strengths, and improvement suggestions
- Recommended next steps

---

## Step 10: First Contribution (`/contribute`)

Browse AI-curated starter tasks:

- Filter by **All / Beginner / Intermediate**
- Each card shows why it's a good first task, estimated time, and acceptance criteria
- Click **Start This Task →** to open the Validation panel pre-loaded with that task

---

## Step 11: PR Preparation (`/pr`)

When you're ready to open a pull request:

1. The task you completed is pre-filled
2. Add the list of files you changed (one per line)
3. Add a description of tests you performed (one per line)
4. Click **Generate PR Description**

You'll get:
- A **PR title** following conventional-commits format
- A **PR description** with What / Why / How / Testing sections
- A **pre-merge checklist**
- Suggested **labels**
- A **Copy PR Template** button for instant clipboard copy

---

## Troubleshooting

| Issue | Solution |
|-------|---------|
| Analysis fails | Check that `LLM_API_KEY` is set on the backend |
| Chat returns generic answers | Include `repo_data` in context when building the request |
| PR generation times out | Increase `LLM_TIMEOUT` in the environment |
| Frontend can't reach backend | Ensure the `proxy` in `frontend/package.json` matches the backend port |

---

*Made with IBM Bob*
