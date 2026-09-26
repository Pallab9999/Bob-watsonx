"""
MCP Client for testing and validating the MCP Server
"""

import asyncio
import httpx
import json
from typing import Dict, Any, Optional, List
from datetime import datetime


class MCPClient:
    """Client for interacting with the MCP Server"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the MCP client
        
        Args:
            base_url: Base URL of the MCP server
        """
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url)
    
    async def close(self):
        """Close the client connection"""
        await self.client.aclose()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check server health"""
        response = await self.client.get("/health")
        response.raise_for_status()
        return response.json()
    
    async def get_server_info(self) -> Dict[str, Any]:
        """Get server information"""
        response = await self.client.get("/")
        response.raise_for_status()
        return response.json()
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools"""
        response = await self.client.get("/tools")
        response.raise_for_status()
        data = response.json()
        return data.get("tools", [])
    
    async def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """Get information about a specific tool"""
        response = await self.client.get(f"/tools/{tool_name}")
        response.raise_for_status()
        return response.json()
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with given parameters
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            
        Returns:
            Tool execution result
        """
        request_data = {
            "tool_name": tool_name,
            "parameters": parameters
        }
        response = await self.client.post("/tools/execute", json=request_data)
        response.raise_for_status()
        return response.json()
    
    async def mcp_initialize(self) -> Dict[str, Any]:
        """Initialize MCP protocol"""
        response = await self.client.post("/mcp/initialize")
        response.raise_for_status()
        return response.json()
    
    async def mcp_list_tools(self) -> List[Dict[str, Any]]:
        """List tools using MCP protocol"""
        response = await self.client.post("/mcp/tools/list")
        response.raise_for_status()
        data = response.json()
        return data.get("tools", [])
    
    async def mcp_call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool using MCP protocol"""
        request_data = {
            "name": tool_name,
            "arguments": arguments
        }
        response = await self.client.post("/mcp/tools/call", json=request_data)
        response.raise_for_status()
        return response.json()


async def test_server_connectivity(client: MCPClient) -> bool:
    """Test basic server connectivity"""
    try:
        info = await client.get_server_info()
        print(f"✓ Server is running: {info['name']} v{info['version']}")
        return True
    except Exception as e:
        print(f"✗ Failed to connect to server: {e}")
        return False


async def test_health_check(client: MCPClient) -> bool:
    """Test health check endpoint"""
    try:
        health = await client.health_check()
        print(f"✓ Server health: {health['status']}")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False


async def test_list_tools(client: MCPClient) -> bool:
    """Test listing tools"""
    try:
        tools = await client.list_tools()
        print(f"✓ Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description'][:60]}...")
        return True
    except Exception as e:
        print(f"✗ Failed to list tools: {e}")
        return False


async def test_get_weather_tool(client: MCPClient) -> bool:
    """Test get_weather tool"""
    try:
        print("\n--- Testing get_weather tool ---")
        result = await client.execute_tool(
            "get_weather",
            {"location": "London, UK", "units": "celsius"}
        )
        
        if result["success"]:
            weather = result["result"]["weather"]
            print(f"✓ Weather for {result['result']['location']}:")
            print(f"  Temperature: {weather['temperature']}")
            print(f"  Condition: {weather['condition']}")
            print(f"  Humidity: {weather['humidity']}")
            print(f"  Wind Speed: {weather['wind_speed']}")
            return True
        else:
            print(f"✗ Tool execution failed: {result.get('error')}")
            return False
    except Exception as e:
        print(f"✗ Error testing weather tool: {e}")
        return False


async def test_calculate_statistics_tool(client: MCPClient) -> bool:
    """Test calculate_statistics tool"""
    try:
        print("\n--- Testing calculate_statistics tool ---")
        numbers = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        result = await client.execute_tool(
            "calculate_statistics",
            {"numbers": numbers, "measures": ["mean", "median", "min", "max", "stdev"]}
        )
        
        if result["success"]:
            stats = result["result"]["statistics"]
            print(f"✓ Statistics for {numbers}:")
            print(f"  Mean: {stats.get('mean')}")
            print(f"  Median: {stats.get('median')}")
            print(f"  Min: {stats.get('min')}")
            print(f"  Max: {stats.get('max')}")
            print(f"  Std Dev: {stats.get('stdev')}")
            return True
        else:
            print(f"✗ Tool execution failed: {result.get('error')}")
            return False
    except Exception as e:
        print(f"✗ Error testing statistics tool: {e}")
        return False


async def test_mcp_protocol(client: MCPClient) -> bool:
    """Test MCP protocol endpoints"""
    try:
        print("\n--- Testing MCP Protocol ---")
        
        # Initialize
        init_result = await client.mcp_initialize()
        print(f"✓ MCP Initialize: {init_result['serverInfo']['name']} v{init_result['serverInfo']['version']}")
        
        # List tools
        tools = await client.mcp_list_tools()
        print(f"✓ MCP List Tools: Found {len(tools)} tools")
        
        # Call tool
        call_result = await client.mcp_call_tool(
            "get_weather",
            {"location": "Paris, France"}
        )
        print(f"✓ MCP Call Tool: Executed successfully")
        
        return True
    except Exception as e:
        print(f"✗ MCP protocol test failed: {e}")
        return False


async def run_validation_tests(base_url: str = "http://localhost:8000"):
    """Run all validation tests"""
    client = MCPClient(base_url)
    
    try:
        print("=" * 60)
        print("MCP Server Validation Tests")
        print("=" * 60)
        print(f"Server URL: {base_url}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 60)
        
        results = []
        
        # Run tests
        results.append(("Server Connectivity", await test_server_connectivity(client)))
        results.append(("Health Check", await test_health_check(client)))
        results.append(("List Tools", await test_list_tools(client)))
        results.append(("Get Weather Tool", await test_get_weather_tool(client)))
        results.append(("Calculate Statistics Tool", await test_calculate_statistics_tool(client)))
        results.append(("MCP Protocol", await test_mcp_protocol(client)))
        
        # Print summary
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {test_name}")
        
        print("=" * 60)
        print(f"Results: {passed}/{total} tests passed")
        print("=" * 60)
        
        return passed == total
        
    finally:
        await client.close()


if __name__ == "__main__":
    import sys
    
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    success = asyncio.run(run_validation_tests(base_url))
    sys.exit(0 if success else 1)

# Made with Bob
