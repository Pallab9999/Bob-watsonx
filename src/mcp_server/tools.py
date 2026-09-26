"""
MCP Tools for watsonx Orchestrate Integration
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import statistics


class MCPTool:
    """Base class for MCP tools"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary representation"""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.get_input_schema(),
        }
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for tool inputs"""
        raise NotImplementedError
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        raise NotImplementedError


class GetWeatherTool(MCPTool):
    """Tool to get weather information for a location"""
    
    def __init__(self):
        super().__init__(
            name="get_weather",
            description="Get current weather information for a specified location. Returns temperature, conditions, humidity, and wind speed."
        )
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and country (e.g., 'London, UK' or 'New York, USA')"
                },
                "units": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature units",
                    "default": "celsius"
                }
            },
            "required": ["location"]
        }
    
    async def execute(self, location: str, units: str = "celsius") -> Dict[str, Any]:
        """
        Execute the weather tool
        
        Args:
            location: City and country
            units: Temperature units (celsius or fahrenheit)
            
        Returns:
            Dictionary with weather information
        """
        # Simulated weather data (in production, this would call a real weather API)
        temp_c = 22.5
        temp_f = temp_c * 9/5 + 32
        
        temperature = temp_c if units == "celsius" else temp_f
        unit_symbol = "°C" if units == "celsius" else "°F"
        
        return {
            "success": True,
            "location": location,
            "timestamp": datetime.utcnow().isoformat(),
            "weather": {
                "temperature": f"{temperature:.1f}{unit_symbol}",
                "condition": "Partly Cloudy",
                "humidity": "65%",
                "wind_speed": "15 km/h",
                "description": f"Current weather in {location}"
            }
        }


class CalculateStatisticsTool(MCPTool):
    """Tool to calculate statistical measures from a list of numbers"""
    
    def __init__(self):
        super().__init__(
            name="calculate_statistics",
            description="Calculate statistical measures (mean, median, mode, standard deviation, min, max) from a list of numbers."
        )
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "numbers": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "List of numbers to analyze",
                    "minItems": 1
                },
                "measures": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["mean", "median", "mode", "stdev", "min", "max", "all"]
                    },
                    "description": "Statistical measures to calculate. Use 'all' for all measures.",
                    "default": ["all"]
                }
            },
            "required": ["numbers"]
        }
    
    async def execute(self, numbers: List[float], measures: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute the statistics calculation tool
        
        Args:
            numbers: List of numbers to analyze
            measures: List of statistical measures to calculate
            
        Returns:
            Dictionary with calculated statistics
        """
        if not numbers:
            return {
                "success": False,
                "error": "Numbers list cannot be empty"
            }
        
        if measures is None or "all" in measures:
            measures = ["mean", "median", "mode", "stdev", "min", "max"]
        
        results = {
            "success": True,
            "count": len(numbers),
            "statistics": {}
        }
        
        try:
            if "mean" in measures:
                results["statistics"]["mean"] = round(statistics.mean(numbers), 2)
            
            if "median" in measures:
                results["statistics"]["median"] = round(statistics.median(numbers), 2)
            
            if "mode" in measures:
                try:
                    results["statistics"]["mode"] = round(statistics.mode(numbers), 2)
                except statistics.StatisticsError:
                    results["statistics"]["mode"] = "No unique mode"
            
            if "stdev" in measures and len(numbers) > 1:
                results["statistics"]["stdev"] = round(statistics.stdev(numbers), 2)
            
            if "min" in measures:
                results["statistics"]["min"] = round(min(numbers), 2)
            
            if "max" in measures:
                results["statistics"]["max"] = round(max(numbers), 2)
            
            return results
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error calculating statistics: {str(e)}"
            }


# Tool instances
get_weather_tool = GetWeatherTool()
calculate_statistics_tool = CalculateStatisticsTool()

# Registry of all available tools
TOOLS_REGISTRY = {
    "get_weather": get_weather_tool,
    "calculate_statistics": calculate_statistics_tool,
}


def get_all_tools() -> List[Dict[str, Any]]:
    """Get all available tools as dictionary representations"""
    return [tool.to_dict() for tool in TOOLS_REGISTRY.values()]


async def execute_tool(tool_name: str, **kwargs) -> Dict[str, Any]:
    """
    Execute a tool by name with given parameters
    
    Args:
        tool_name: Name of the tool to execute
        **kwargs: Tool parameters
        
    Returns:
        Tool execution result
    """
    if tool_name not in TOOLS_REGISTRY:
        return {
            "success": False,
            "error": f"Tool '{tool_name}' not found"
        }
    
    tool = TOOLS_REGISTRY[tool_name]
    return await tool.execute(**kwargs)

# Made with Bob
