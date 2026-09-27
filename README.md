# Developer Onboarding Copilot

> **IBM Bob 2.0 Hackathon** · AI-powered Developer Onboarding · Built with IBM watsonx & Bob

Transform any unfamiliar GitHub repository into an interactive, personalised learning journey — from first clone to first contribution in record time.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **Repository Analysis** | Detects languages, frameworks, entry points, and test suites automatically |
| 🧭 **Personalised Plan** | AI generates a day-by-day onboarding plan tailored to your experience level and role |
| 💬 **Codebase Chat** | Ask anything about the repository and get context-aware, file-referenced answers |
| ✅ **Code Validation** | Submit your work and get instant AI feedback against task acceptance criteria |
| 🌱 **First Contribution** | Curated beginner-safe tasks based on actual gaps in the codebase |
| 📝 **PR Generator** | Auto-generates a PR title, description, and pre-merge checklist |

---

## 🏗 Project Structure

```
Bob-watsonx/
├── src/
│   └── mcp_server/
│       ├── main.py                    # FastAPI app + all API endpoints
│       ├── config.py                  # Server configuration
│       ├── tools.py                   # Original MCP tools
│       ├── ai/
│       │   ├── provider.py            # AIProvider — LLM abstraction layer (Dev B)
│       │   └── prompts.py             # All prompt templates (Dev B)
│       └── onboarding/
│           ├── plan_generator.py      # Plan generation & management (Dev B)
│           ├── validator.py           # Code submission validation (Dev B)
│           └── contributions.py      # First-task & PR generation (Dev B)
├── frontend/
│   └── src/
│       ├── App.tsx                    # Routing (Dev B)
│       ├── types/index.ts             # TypeScript types (Dev B)
│       ├── services/api.ts            # API client (Dev B)
│       └── components/
│           ├── Analysis.tsx           # Analysis loading screen (Dev B)
│           ├── Dashboard.tsx          # Progress dashboard (Dev B)
│           ├── ChatInterface.tsx      # AI codebase chat (Dev B)
│           ├── Validation.tsx         # Code validation panel (Dev B)
│           ├── FirstContribution.tsx  # Good-first-task browser (Dev B)
│           └── PRPreparation.tsx      # PR description generator (Dev B)
├── tests/
├── docs/
└── requirements.txt
```

---

## 🚀 Getting Started

### Backend

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variables
export LLM_API_KEY="your-openai-or-compatible-key"
export LLM_BASE_URL="https://api.openai.com/v1"   # or watsonx endpoint
export LLM_MODEL="gpt-4o-mini"

# 4. Run the server
python -m mcp_server.main
# → API docs at http://localhost:8000/docs
```

For native watsonx.ai inference and watsonx Orchestrate ADK setup, see
[watsonx-orchestrate/README.md](watsonx-orchestrate/README.md).

### Frontend

```bash
cd frontend
npm install
npm start
# → Opens http://localhost:3000
```

---

## 🔌 API Endpoints (Developer B additions)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/analyze-repo` | AI analysis of raw repository data |
| `POST` | `/api/generate-plan` | Generate personalised onboarding plan |
| `GET`  | `/api/plan/{id}` | Retrieve plan with progress |
| `POST` | `/api/plan/{id}/customize` | Customise focus/skip days |
| `PATCH`| `/api/plan/{id}/task-status` | Update task completion status |
| `POST` | `/api/chat` | Context-aware codebase Q&A |
| `POST` | `/api/validate` | Validate code against task criteria |
| `GET`  | `/api/validation/{id}/status` | Get validation result |
| `POST` | `/api/contributions/suggest` | Get good-first-task suggestions |
| `POST` | `/api/pr/generate` | Generate PR title + description |
| `GET`  | `/api/pr/{id}` | Retrieve PR draft |

Full interactive docs: `http://localhost:8000/docs`

---

## 🤖 IBM Bob & watsonx Integration

- The `AIProvider` class in [`src/mcp_server/ai/provider.py`](src/mcp_server/ai/provider.py) supports OpenAI-compatible services and native **watsonx.ai** through `LLM_PROVIDER=watsonx`
- Native watsonx.ai inference uses `WATSONX_API_KEY`, `WATSONX_PROJECT_ID`, `WATSONX_URL`, and `WATSONX_MODEL`
- The server exposes a standards-compliant Streamable HTTP MCP endpoint at `/mcp/` for integration with **watsonx Orchestrate**, alongside its legacy `/mcp/*` compatibility routes

---

## 🧪 Running Tests

```bash
pytest tests/ -v --cov=src/mcp_server
```

---

## 📚 Documentation

- [User Guide](docs/USER_GUIDE.md) — step-by-step walkthrough
- [Demo Script](docs/DEMO_SCRIPT.md) — 3-5 minute judge demo
- [API Reference](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

---

## 👥 Team

| Role | Focus |
|------|-------|
| Developer A | GitHub integration, repo analysis, frontend setup, codebase map, task list |
| Developer B | AI layer, plan generation, dashboard, chat, validation, contributions, PR prep |

---

## 📄 License

MIT License · Made with ❤️ and IBM Bob
