# Quick Setup Guide for Dev B

## 🚀 Clone and Run the Prototype

### 1. Clone the Repository

```bash
git clone https://github.com/Pallab9999/Bob-watsonx.git
cd Bob-watsonx
```

### 2. Backend Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Windows PowerShell:
venv\Scripts\Activate.ps1
# Windows CMD:
venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
# Linux/Mac:
export LLM_API_KEY="your-api-key-here"
export LLM_BASE_URL="https://api.openai.com/v1"   # swap for IBM watsonx endpoint
export LLM_MODEL="gpt-4o-mini"
export LLM_TIMEOUT="60"

# Windows PowerShell:
$env:LLM_API_KEY="your-api-key-here"
$env:LLM_BASE_URL="https://api.openai.com/v1"
$env:LLM_MODEL="gpt-4o-mini"

# Or create a .env file in the root directory:
# LLM_API_KEY=your-api-key-here
# LLM_BASE_URL=https://api.openai.com/v1
# LLM_MODEL=gpt-4o-mini

# Run the backend server
uvicorn src.mcp_server.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend API will be available at: **http://localhost:8000**  
Interactive API docs (Swagger UI): **http://localhost:8000/docs**

### 3. Frontend Setup (in a new terminal)

```bash
cd frontend
npm install
npm start
```

The frontend will open at: **http://localhost:3000**

> The frontend proxies all `/api/*` requests to `http://localhost:8000` automatically — no extra config needed.

---

## 🧪 Test the Prototype

### Quick API Test

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What does this repo do?", "context": {"repo_summary": {}}}'
```

### Frontend Flow

1. Open **http://localhost:3000**
2. Click **Try Demo Repository** (loads pre-configured demo data)
3. Watch the Analysis screen tick through all 6 steps
4. Explore the Dashboard — tech badges, progress bar, day cards
5. Click **Ask the Codebase** and ask anything about the repo
6. Navigate to **First Contribution** and start a task
7. Paste code in the **Validation** panel and run a review
8. Go to **PR Preparation** and generate a PR description

---

## 📋 Key Features to Test

- ✅ Repository analysis (AI-powered summary)
- ✅ Personalised onboarding plan generation
- ✅ Interactive codebase chat
- ✅ Code validation with AI feedback
- ✅ First contribution suggestions
- ✅ PR description generation

---

## 🔧 Troubleshooting

### Backend Issues

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'fastapi'` | Virtual environment not activated — run `source venv/bin/activate` |
| `LLM request failed [401]` | `LLM_API_KEY` is not set or is invalid |
| Port 8000 already in use | Change port: `uvicorn src.mcp_server.main:app --port 8001` |

### Frontend Issues

| Problem | Fix |
|---------|-----|
| Port 3000 already in use | The app will prompt to use a different port — press `Y` |
| API connection errors | Ensure the backend is running on port 8000 before using AI features |
| `npm install` fails | Try `npm install --legacy-peer-deps` |
| Build fails with `ajv` error on Node 18+ | Run `npm install ajv@^8 --legacy-peer-deps` then retry |

---

## 🔌 API Endpoints (Developer B)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/analyze-repo` | AI analysis of repository data |
| `POST` | `/api/generate-plan` | Generate personalised onboarding plan |
| `GET`  | `/api/plan/{id}` | Retrieve plan with progress |
| `POST` | `/api/plan/{id}/customize` | Customise focus modules / skip days |
| `PATCH`| `/api/plan/{id}/task-status` | Update task completion status |
| `POST` | `/api/chat` | Context-aware codebase Q&A |
| `POST` | `/api/validate` | Validate code against task criteria |
| `GET`  | `/api/validation/{id}/status` | Retrieve validation result |
| `POST` | `/api/contributions/suggest` | Get good-first-task suggestions |
| `POST` | `/api/pr/generate` | Generate PR title + description |
| `GET`  | `/api/pr/{id}` | Retrieve PR draft |

---

## 📚 Additional Resources

- [Full README](README.md)
- [User Guide](docs/USER_GUIDE.md)
- [API Documentation](docs/API.md)
- [Demo Script](docs/DEMO_SCRIPT.md)

## 🤝 Need Help?

Contact the team or check the documentation in the `docs/` folder.

---

*Made with IBM Bob*
