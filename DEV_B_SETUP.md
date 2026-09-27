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
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
venv\Scripts\Activate.ps1
# Windows CMD:
venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (Windows PowerShell)
$env:LLM_API_KEY="your-api-key-here"
$env:LLM_BASE_URL="https://api.openai.com/v1"
$env:LLM_MODEL="gpt-4o-mini"

# Or create a .env file in the root directory:
# LLM_API_KEY=your-api-key-here
# LLM_BASE_URL=https://api.openai.com/v1
# LLM_MODEL=gpt-4o-mini

# Run the backend server
python -m src.mcp_server.main
```

The backend API will be available at: **http://localhost:8000**
API documentation: **http://localhost:8000/docs**

### 3. Frontend Setup (in a new terminal)

```bash
cd frontend
npm install
npm start
```

The frontend will open at: **http://localhost:3000**

## 🧪 Test the Prototype

### Quick API Test

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test repository analysis (example)
curl -X POST http://localhost:8000/api/analyze-repo \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/example/repo"}'
```

### Frontend Flow

1. Open http://localhost:3000
2. Enter a GitHub repository URL
3. View the AI-generated analysis
4. Explore the onboarding plan
5. Try the chat interface
6. Test code validation

## 📋 Key Features to Test

- ✅ Repository analysis
- ✅ Personalized onboarding plan generation
- ✅ Interactive codebase chat
- ✅ Code validation
- ✅ First contribution suggestions
- ✅ PR description generation

## 🔧 Troubleshooting

### Backend Issues

- **Port 8000 already in use**: Change port in `src/mcp_server/config.py`
- **Module not found**: Ensure virtual environment is activated
- **API key errors**: Verify environment variables are set correctly

### Frontend Issues

- **Port 3000 already in use**: The app will prompt to use a different port
- **API connection errors**: Ensure backend is running on port 8000
- **npm install fails**: Try `npm install --legacy-peer-deps`

## 📚 Additional Resources

- [Full README](README.md)
- [User Guide](docs/USER_GUIDE.md)
- [API Documentation](docs/API.md)
- [Demo Script](docs/DEMO_SCRIPT.md)

## 🤝 Need Help?

Contact the team or check the documentation in the `docs/` folder.