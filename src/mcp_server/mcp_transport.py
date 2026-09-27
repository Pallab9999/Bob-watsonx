"""Standards-compliant Streamable HTTP transport for watsonx Orchestrate."""

import os

try:
    # MCP 2.x renamed FastMCP to MCPServer.
    from mcp.server import MCPServer as _MCPServer
except ImportError:
    # Keep compatibility with the MCP 1.x package used by early project setups.
    from mcp.server.fastmcp import FastMCP as _MCPServer

from mcp.server.transport_security import TransportSecuritySettings

from .tools import execute_tool


watsonx_mcp = _MCPServer(
    "Developer Onboarding Copilot",
    instructions=(
        "Use the tools to retrieve weather or calculate statistics. "
        "Ask for missing required values before calling a tool."
    ),
)


@watsonx_mcp.tool()
async def get_weather(location: str, units: str = "celsius") -> dict:
    """Get current weather for a city and country in Celsius or Fahrenheit."""
    return await execute_tool("get_weather", location=location, units=units)


@watsonx_mcp.tool()
async def calculate_statistics(numbers: list[float], measures: list[str] | None = None) -> dict:
    """Calculate mean, median, mode, standard deviation, minimum, and maximum."""
    return await execute_tool("calculate_statistics", numbers=numbers, measures=measures)


def streamable_http_app():
    """Create the MCP ASGI app with an optional deployment host allowlist."""
    allowed_hosts = [
        host.strip()
        for host in os.getenv("MCP_ALLOWED_HOSTS", "").split(",")
        if host.strip()
    ]
    options = {"streamable_http_path": "/"}
    if allowed_hosts:
        allowed_origins = [
            origin.strip()
            for origin in os.getenv("MCP_ALLOWED_ORIGINS", "").split(",")
            if origin.strip()
        ]
        options["transport_security"] = TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=allowed_hosts,
            allowed_origins=allowed_origins,
        )
    return watsonx_mcp.streamable_http_app(**options)
