"""
Main MCP Server implementation
"""

import asyncio
import json
import logging
from typing import Any, Dict, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from .config import config
from .tools import get_all_tools, execute_tool, TOOLS_REGISTRY


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

# Made with Bob
