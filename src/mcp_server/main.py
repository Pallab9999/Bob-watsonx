"""
Main MCP Server implementation — Developer Onboarding Copilot
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from .config import config
from .tools import get_all_tools, execute_tool, TOOLS_REGISTRY
from .ai.provider import ai_provider
from .onboarding.plan_generator import (
    generate_plan,
    get_plan,
    customize_plan,
    update_task_status,
    calculate_progress,
)
from .onboarding.validator import run_validation, get_validation, get_validations_for_task
from .onboarding.contributions import (
    suggest_contributions,
    get_contribution_suggestions,
    generate_pr,
    get_pr_draft,
)


# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# FastAPI app
app = FastAPI(
    title="MCP Server for watsonx Orchestrate",
    description="Model Context Protocol server with tools for watsonx Orchestrate integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class ToolExecutionRequest(BaseModel):
    """Request model for tool execution"""
    tool_name: str
    parameters: Dict[str, Any]


class ToolExecutionResponse(BaseModel):
    """Response model for tool execution"""
    success: bool
    result: Dict[str, Any]
    error: str = None


class ListToolsResponse(BaseModel):
    """Response model for listing tools"""
    tools: List[Dict[str, Any]]


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with server information"""
    return {
        "name": "MCP Server for watsonx Orchestrate",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "list_tools": "/tools",
            "execute_tool": "/tools/execute",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": asyncio.get_event_loop().time()
    }


@app.get("/tools", response_model=ListToolsResponse)
async def list_tools():
    """List all available MCP tools"""
    try:
        tools = get_all_tools()
        logger.info(f"Listed {len(tools)} tools")
        return ListToolsResponse(tools=tools)
    except Exception as e:
        logger.error(f"Error listing tools: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/execute", response_model=ToolExecutionResponse)
async def execute_tool_endpoint(request: ToolExecutionRequest):
    """Execute an MCP tool with given parameters"""
    try:
        logger.info(f"Executing tool: {request.tool_name}")
        logger.debug(f"Parameters: {request.parameters}")
        
        result = await execute_tool(request.tool_name, **request.parameters)
        
        if result.get("success", False):
            logger.info(f"Tool {request.tool_name} executed successfully")
            return ToolExecutionResponse(
                success=True,
                result=result
            )
        else:
            error_msg = result.get("error", "Unknown error")
            logger.error(f"Tool execution failed: {error_msg}")
            return ToolExecutionResponse(
                success=False,
                result=result,
                error=error_msg
            )
            
    except Exception as e:
        logger.error(f"Error executing tool {request.tool_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tools/{tool_name}")
async def get_tool_info(tool_name: str):
    """Get information about a specific tool"""
    if tool_name not in TOOLS_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    tool = TOOLS_REGISTRY[tool_name]
    return tool.to_dict()


# MCP Protocol endpoints
@app.post("/mcp/initialize")
async def mcp_initialize():
    """MCP protocol initialization"""
    return {
        "protocolVersion": "1.0.0",
        "serverInfo": {
            "name": "mcp-watsonx-server",
            "version": "1.0.0"
        },
        "capabilities": {
            "tools": {
                "listChanged": False
            }
        }
    }


@app.post("/mcp/tools/list")
async def mcp_list_tools():
    """MCP protocol: List tools"""
    tools = get_all_tools()
    return {
        "tools": tools
    }


@app.post("/mcp/tools/call")
async def mcp_call_tool(request: Dict[str, Any]):
    """MCP protocol: Call a tool"""
    tool_name = request.get("name")
    arguments = request.get("arguments", {})
    
    if not tool_name:
        raise HTTPException(status_code=400, detail="Tool name is required")
    
    result = await execute_tool(tool_name, **arguments)
    
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(result, indent=2)
            }
        ]
    }


def main():
    """Main entry point for the server"""
    logger.info(f"Starting MCP Server on {config.host}:{config.port}")
    logger.info(f"Debug mode: {config.debug}")
    
    uvicorn.run(
        "mcp_server.main:app",
        host=config.host,
        port=config.port,
        reload=config.debug,
        log_level=config.log_level.lower()
    )


if __name__ == "__main__":
    main()


# ===========================================================================
# Developer Onboarding Copilot — API Models
# ===========================================================================

class UserProfile(BaseModel):
    experience_level: str = "beginner"   # beginner | intermediate | advanced
    role: str = "fullstack"              # frontend | backend | fullstack | data | devops
    goal: Optional[str] = None


class GeneratePlanRequest(BaseModel):
    repo_id: str
    repo_data: Dict[str, Any]
    user_profile: UserProfile


class CustomizePlanRequest(BaseModel):
    focus_modules: Optional[List[str]] = None
    skip_days: Optional[List[int]] = None
    add_goal: Optional[str] = None


class UpdateTaskStatusRequest(BaseModel):
    task_id: str
    status: str   # pending | in_progress | completed


class ChatRequest(BaseModel):
    question: str
    context: Dict[str, Any]


class ValidateRequest(BaseModel):
    task: Dict[str, Any]
    code_submission: str
    run_tests: bool = False
    run_lint: bool = False


class SuggestContributionsRequest(BaseModel):
    repo_id: str
    repo_data: Dict[str, Any]


class GeneratePRRequest(BaseModel):
    task: Dict[str, Any]
    files_changed: List[str]
    tests_performed: List[str]


class AnalyzeRepoRequest(BaseModel):
    repo_data: Dict[str, Any]


# ===========================================================================
# Developer Onboarding Copilot — Endpoints
# ===========================================================================

# ---- AI / Repo analysis -----------------------------------------------

@app.post("/api/analyze-repo", tags=["Onboarding"])
async def analyze_repo(request: AnalyzeRepoRequest):
    """Run AI analysis on a repository and return a structured summary."""
    try:
        result = await ai_provider.analyze_repository(request.repo_data)
        return {"success": True, "analysis": result}
    except Exception as exc:
        logger.error(f"analyze_repo failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


# ---- Plan generation --------------------------------------------------

@app.post("/api/generate-plan", tags=["Onboarding"])
async def api_generate_plan(request: GeneratePlanRequest):
    """Generate a personalised onboarding plan for a repository and user profile."""
    try:
        plan = await generate_plan(
            repo_id=request.repo_id,
            repo_data=request.repo_data,
            user_profile=request.user_profile.model_dump(),
        )
        return {"success": True, "plan": plan}
    except Exception as exc:
        logger.error(f"generate_plan failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/plan/{plan_id}", tags=["Onboarding"])
async def api_get_plan(plan_id: str):
    """Retrieve an existing onboarding plan by ID."""
    plan = get_plan(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    progress = calculate_progress(plan)
    return {"success": True, "plan": plan, "progress": progress}


@app.post("/api/plan/{plan_id}/customize", tags=["Onboarding"])
async def api_customize_plan(plan_id: str, request: CustomizePlanRequest):
    """Apply customisations (focus modules, skip days, extra goal) to a plan."""
    updated = await customize_plan(plan_id, request.model_dump(exclude_none=True))
    if updated is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"success": True, "plan": updated}


@app.patch("/api/plan/{plan_id}/task-status", tags=["Onboarding"])
async def api_update_task_status(plan_id: str, request: UpdateTaskStatusRequest):
    """Update the completion status of a task inside a plan."""
    task = update_task_status(plan_id, request.task_id, request.status)
    if task is None:
        raise HTTPException(status_code=404, detail="Plan or task not found")
    return {"success": True, "task": task}


# ---- Chat  ------------------------------------------------------------

@app.post("/api/chat", tags=["Onboarding"])
async def api_chat(request: ChatRequest):
    """Answer a developer's question about the codebase using repository context."""
    try:
        answer = await ai_provider.answer_question(request.question, request.context)
        return {"success": True, "answer": answer}
    except Exception as exc:
        logger.error(f"chat failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


# ---- Validation -------------------------------------------------------

@app.post("/api/validate", tags=["Onboarding"])
async def api_validate(request: ValidateRequest):
    """Validate a code submission against a task's acceptance criteria."""
    try:
        result = await run_validation(
            task=request.task,
            code_submission=request.code_submission,
            run_tests=request.run_tests,
            run_lint=request.run_lint,
        )
        return {"success": True, "validation": result}
    except Exception as exc:
        logger.error(f"validate failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/validation/{validation_id}/status", tags=["Onboarding"])
async def api_get_validation(validation_id: str):
    """Retrieve a stored validation result."""
    result = get_validation(validation_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Validation not found")
    return {"success": True, "validation": result}


# ---- Contributions & PR -----------------------------------------------

@app.post("/api/contributions/suggest", tags=["Onboarding"])
async def api_suggest_contributions(request: SuggestContributionsRequest):
    """Analyse a repository and suggest good first contribution tasks."""
    try:
        result = await suggest_contributions(request.repo_id, request.repo_data)
        return {"success": True, **result}
    except Exception as exc:
        logger.error(f"suggest_contributions failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/contributions/{suggestion_id}", tags=["Onboarding"])
async def api_get_contributions(suggestion_id: str):
    """Retrieve previously generated contribution suggestions."""
    result = get_contribution_suggestions(suggestion_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Suggestions not found")
    return {"success": True, **result}


@app.post("/api/pr/generate", tags=["Onboarding"])
async def api_generate_pr(request: GeneratePRRequest):
    """Generate a PR title and description for a completed task."""
    try:
        pr = await generate_pr(
            task=request.task,
            files_changed=request.files_changed,
            tests_performed=request.tests_performed,
        )
        return {"success": True, "pr": pr}
    except Exception as exc:
        logger.error(f"generate_pr failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/pr/{pr_id}", tags=["Onboarding"])
async def api_get_pr(pr_id: str):
    """Retrieve a previously generated PR draft."""
    pr = get_pr_draft(pr_id)
    if pr is None:
        raise HTTPException(status_code=404, detail="PR draft not found")
    return {"success": True, "pr": pr}

# Made with Bob
