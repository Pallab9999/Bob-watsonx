"""
Unit tests for MCP tools
"""

import pytest
import asyncio
from src.mcp_server.tools import (
    GetWeatherTool,
    CalculateStatisticsTool,
    get_weather_tool,
    calculate_statistics_tool,
    get_all_tools,
    execute_tool,
    TOOLS_REGISTRY
)


class TestGetWeatherTool:
    """Tests for GetWeatherTool"""
    
    def test_tool_initialization(self):
        """Test tool is properly initialized"""
        tool = GetWeatherTool()
        assert tool.name == "get_weather"
        assert "weather" in tool.description.lower()
    
    def test_input_schema(self):
        """Test input schema is correctly defined"""
        tool = GetWeatherTool()
        schema = tool.get_input_schema()
        
        assert schema["type"] == "object"
        assert "location" in schema["properties"]
        assert "units" in schema["properties"]
        assert "location" in schema["required"]
    
    def test_to_dict(self):
        """Test tool dictionary representation"""
        tool = GetWeatherTool()
        tool_dict = tool.to_dict()
        
        assert tool_dict["name"] == "get_weather"
        assert "description" in tool_dict
        assert "inputSchema" in tool_dict
    
    @pytest.mark.asyncio
    async def test_execute_celsius(self):
        """Test weather tool execution with celsius"""
        tool = GetWeatherTool()
        result = await tool.execute(location="London, UK", units="celsius")
        
        assert result["success"] is True
        assert result["location"] == "London, UK"
        assert "weather" in result
        assert "°C" in result["weather"]["temperature"]
        assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_execute_fahrenheit(self):
        """Test weather tool execution with fahrenheit"""
        tool = GetWeatherTool()
        result = await tool.execute(location="New York, USA", units="fahrenheit")
        
        assert result["success"] is True
        assert result["location"] == "New York, USA"
        assert "°F" in result["weather"]["temperature"]
    
    @pytest.mark.asyncio
    async def test_execute_default_units(self):
        """Test weather tool execution with default units"""
        tool = GetWeatherTool()
        result = await tool.execute(location="Paris, France")
        
        assert result["success"] is True
        assert "°C" in result["weather"]["temperature"]


class TestCalculateStatisticsTool:
    """Tests for CalculateStatisticsTool"""
    
    def test_tool_initialization(self):
        """Test tool is properly initialized"""
        tool = CalculateStatisticsTool()
        assert tool.name == "calculate_statistics"
        assert "statistical" in tool.description.lower()
    
    def test_input_schema(self):
        """Test input schema is correctly defined"""
        tool = CalculateStatisticsTool()
        schema = tool.get_input_schema()
        
        assert schema["type"] == "object"
        assert "numbers" in schema["properties"]
        assert "measures" in schema["properties"]
        assert "numbers" in schema["required"]
    
    @pytest.mark.asyncio
    async def test_execute_all_measures(self):
        """Test statistics calculation with all measures"""
        tool = CalculateStatisticsTool()
        numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = await tool.execute(numbers=numbers, measures=["all"])
        
        assert result["success"] is True
        assert result["count"] == 10
        assert "statistics" in result
        assert result["statistics"]["mean"] == 5.5
        assert result["statistics"]["median"] == 5.5
        assert result["statistics"]["min"] == 1
        assert result["statistics"]["max"] == 10
    
    @pytest.mark.asyncio
    async def test_execute_specific_measures(self):
        """Test statistics calculation with specific measures"""
        tool = CalculateStatisticsTool()
        numbers = [10, 20, 30, 40, 50]
        result = await tool.execute(numbers=numbers, measures=["mean", "median"])
        
        assert result["success"] is True
        assert "mean" in result["statistics"]
        assert "median" in result["statistics"]
        assert result["statistics"]["mean"] == 30
        assert result["statistics"]["median"] == 30
    
    @pytest.mark.asyncio
    async def test_execute_single_number(self):
        """Test statistics calculation with single number"""
        tool = CalculateStatisticsTool()
        numbers = [42]
        result = await tool.execute(numbers=numbers)
        
        assert result["success"] is True
        assert result["statistics"]["mean"] == 42
        assert result["statistics"]["median"] == 42
        assert result["statistics"]["min"] == 42
        assert result["statistics"]["max"] == 42
    
    @pytest.mark.asyncio
    async def test_execute_empty_list(self):
        """Test statistics calculation with empty list"""
        tool = CalculateStatisticsTool()
        result = await tool.execute(numbers=[])
        
        assert result["success"] is False
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_execute_with_mode(self):
        """Test statistics calculation with mode"""
        tool = CalculateStatisticsTool()
        numbers = [1, 2, 2, 3, 4, 4, 4, 5]
        result = await tool.execute(numbers=numbers, measures=["mode"])
        
        assert result["success"] is True
        assert result["statistics"]["mode"] == 4
    
    @pytest.mark.asyncio
    async def test_execute_no_unique_mode(self):
        """Test statistics calculation when no unique mode exists"""
        tool = CalculateStatisticsTool()
        numbers = [1, 2, 3, 4, 5]
        result = await tool.execute(numbers=numbers, measures=["mode"])
        
        assert result["success"] is True
        # Should handle no unique mode gracefully


class TestToolRegistry:
    """Tests for tool registry and helper functions"""
    
    def test_tools_registry(self):
        """Test tools are registered correctly"""
        assert "get_weather" in TOOLS_REGISTRY
        assert "calculate_statistics" in TOOLS_REGISTRY
        assert len(TOOLS_REGISTRY) == 2
    
    def test_get_all_tools(self):
        """Test getting all tools"""
        tools = get_all_tools()
        assert len(tools) == 2
        assert all("name" in tool for tool in tools)
        assert all("description" in tool for tool in tools)
        assert all("inputSchema" in tool for tool in tools)
    
    @pytest.mark.asyncio
    async def test_execute_tool_weather(self):
        """Test executing weather tool through registry"""
        result = await execute_tool("get_weather", location="Tokyo, Japan")
        assert result["success"] is True
        assert result["location"] == "Tokyo, Japan"
    
    @pytest.mark.asyncio
    async def test_execute_tool_statistics(self):
        """Test executing statistics tool through registry"""
        result = await execute_tool("calculate_statistics", numbers=[1, 2, 3, 4, 5])
        assert result["success"] is True
        assert "statistics" in result
    
    @pytest.mark.asyncio
    async def test_execute_tool_not_found(self):
        """Test executing non-existent tool"""
        result = await execute_tool("non_existent_tool")
        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"].lower()


class TestToolInstances:
    """Tests for global tool instances"""
    
    def test_get_weather_tool_instance(self):
        """Test get_weather_tool instance"""
        assert get_weather_tool is not None
        assert isinstance(get_weather_tool, GetWeatherTool)
        assert get_weather_tool.name == "get_weather"
    
    def test_calculate_statistics_tool_instance(self):
        """Test calculate_statistics_tool instance"""
        assert calculate_statistics_tool is not None
        assert isinstance(calculate_statistics_tool, CalculateStatisticsTool)
        assert calculate_statistics_tool.name == "calculate_statistics"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob
