"""
Unit tests for MCP Server endpoints
"""

import pytest
import json
from fastapi.testclient import TestClient
from src.mcp_server.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


class TestServerEndpoints:
    """Tests for server endpoints"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_list_tools(self, client):
        """Test list tools endpoint"""
        response = client.get("/tools")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert len(data["tools"]) == 2
        
        tool_names = [tool["name"] for tool in data["tools"]]
        assert "get_weather" in tool_names
        assert "calculate_statistics" in tool_names
    
    def test_get_tool_info(self, client):
        """Test get tool info endpoint"""
        response = client.get("/tools/get_weather")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "get_weather"
        assert "description" in data
        assert "inputSchema" in data
    
    def test_get_tool_info_not_found(self, client):
        """Test get tool info for non-existent tool"""
        response = client.get("/tools/non_existent")
        assert response.status_code == 404
    
    def test_execute_weather_tool(self, client):
        """Test executing weather tool"""
        request_data = {
            "tool_name": "get_weather",
            "parameters": {
                "location": "London, UK",
                "units": "celsius"
            }
        }
        response = client.post("/tools/execute", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "result" in data
        assert data["result"]["location"] == "London, UK"
    
    def test_execute_statistics_tool(self, client):
        """Test executing statistics tool"""
        request_data = {
            "tool_name": "calculate_statistics",
            "parameters": {
                "numbers": [1, 2, 3, 4, 5],
                "measures": ["mean", "median"]
            }
        }
        response = client.post("/tools/execute", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "result" in data
        assert "statistics" in data["result"]
    
    def test_execute_invalid_tool(self, client):
        """Test executing invalid tool"""
        request_data = {
            "tool_name": "invalid_tool",
            "parameters": {}
        }
        response = client.post("/tools/execute", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False


class TestMCPProtocolEndpoints:
    """Tests for MCP protocol endpoints"""
    
    def test_mcp_initialize(self, client):
        """Test MCP initialize endpoint"""
        response = client.post("/mcp/initialize")
        assert response.status_code == 200
        data = response.json()
        assert "protocolVersion" in data
        assert "serverInfo" in data
        assert "capabilities" in data
    
    def test_mcp_list_tools(self, client):
        """Test MCP list tools endpoint"""
        response = client.post("/mcp/tools/list")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert len(data["tools"]) == 2
    
    def test_mcp_call_tool(self, client):
        """Test MCP call tool endpoint"""
        request_data = {
            "name": "get_weather",
            "arguments": {
                "location": "Paris, France"
            }
        }
        response = client.post("/mcp/tools/call", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert len(data["content"]) > 0
        assert data["content"][0]["type"] == "text"
    
    def test_mcp_call_tool_missing_name(self, client):
        """Test MCP call tool without tool name"""
        request_data = {
            "arguments": {}
        }
        response = client.post("/mcp/tools/call", json=request_data)
        assert response.status_code == 400


class TestCORSHeaders:
    """Tests for CORS headers"""
    
    def test_cors_headers_present(self, client):
        """Test CORS headers are present in response"""
        response = client.get("/", headers={"Origin": "http://localhost:3000"})
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


class TestErrorHandling:
    """Tests for error handling"""
    
    def test_execute_tool_with_invalid_parameters(self, client):
        """Test executing tool with invalid parameters"""
        request_data = {
            "tool_name": "calculate_statistics",
            "parameters": {
                "numbers": []  # Empty list should fail
            }
        }
        response = client.post("/tools/execute", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob
