"""Tests for the standards-compliant Streamable HTTP MCP endpoint."""

from fastapi.testclient import TestClient

from src.mcp_server.main import app


def test_streamable_mcp_initializes():
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "pytest", "version": "1.0.0"},
        },
    }

    with TestClient(app, base_url="http://localhost:8000") as client:
        response = client.post("/mcp/", json=request)

    assert response.status_code == 200
    assert b'"serverInfo"' in response.content
    assert b'"Developer Onboarding Copilot"' in response.content
