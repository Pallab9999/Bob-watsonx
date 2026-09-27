# watsonx Orchestrate Setup

## Native watsonx.ai inference

Set these variables before starting the backend. Obtain the API key, project ID,
and service URL from the watsonx.ai project's **Developer access** page.

```powershell
$env:LLM_PROVIDER = "watsonx"
$env:WATSONX_API_KEY = "<IBM Cloud API key>"
$env:WATSONX_PROJECT_ID = "<watsonx.ai project ID>"
$env:WATSONX_URL = "https://<region>.ml.cloud.ibm.com"
$env:WATSONX_MODEL = "ibm/granite-3-3-8b-instruct"
```

Install project dependencies and start the backend with the project virtual
environment:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn src.mcp_server.main:app --host 0.0.0.0 --port 8000
```

The standard Streamable HTTP MCP endpoint is `http://localhost:8000/mcp/`.
For remote watsonx Orchestrate discovery, deploy the server behind HTTPS and
set the deployment hostname before startup:

```powershell
$env:MCP_ALLOWED_HOSTS = "<public-host>,<public-host>:443"
```

Use its public URL after deployment. Do not expose an unauthenticated server to
the internet.

## Orchestrate ADK tooling

The ADK is developer tooling, not an application dependency. Install the
watsonx Orchestrate ADK and `uv`. Copy the `wxo-docs` entry from
`bob-global-mcp.json.example` into IBM Bob's **Global MCP** configuration and
the `orchestrate-adk` entry from `bob-project-mcp.json.example` into its
**Project MCP** configuration.

For a remote MCP import, create a draft connection in watsonx Orchestrate and
import the toolkit using the server's HTTPS URL:

```powershell
orchestrate toolkits import `
  --kind mcp `
  --name developer_onboarding_copilot `
  --description "Developer onboarding MCP tools" `
  --url "https://<public-host>/mcp/" `
  --transport streamable_http `
  --tools "*" `
  --app-id "<orchestrate-connection-name>"
```

Use separate draft and live credentials in watsonx Orchestrate. Never add API
keys, project IDs, or service URLs containing secrets to committed files.
