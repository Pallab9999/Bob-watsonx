"""
Example agents and usage patterns for watsonx Orchestrate
"""

import asyncio
import json
from typing import Dict, Any, Optional

from .watsonx_agent import (
    WatsonxAgent,
    WeatherAgent,
    AnalyticsAgent,
    AgentFactory,
    AgentExecution
)
from .tools import execute_tool


class CompoundAgent(WatsonxAgent):
    """Agent that can use multiple tools in sequence"""
    
    def __init__(self, tool_executor=None):
        """Initialize compound agent"""
        tools = [
            {
                "name": "get_weather",
                "description": "Get weather information"
            },
            {
                "name": "calculate_statistics",
                "description": "Calculate statistics"
            }
        ]
        super().__init__(
            name="Compound Agent",
            description="Agent that can use multiple tools",
            tools=tools,
            tool_executor=tool_executor
        )
    
    def _parse_user_input(self, user_input: str, context: Optional[Dict[str, Any]] = None):
        """Parse user input for compound queries"""
        from .watsonx_agent import ToolCall
        tool_calls = []
        
        # Check for weather queries
        if any(word in user_input.lower() for word in ["weather", "temperature"]):
            location = self._extract_location(user_input)
            if location:
                tool_calls.append(ToolCall("get_weather", {"location": location}))
        
        # Check for statistics queries
        if any(word in user_input.lower() for word in ["statistics", "calculate", "average"]):
            numbers = self._extract_numbers(user_input)
            if numbers:
                tool_calls.append(ToolCall("calculate_statistics", {"numbers": numbers}))
        
        return tool_calls


class SmartWeatherAgent(WatsonxAgent):
    """Enhanced weather agent with additional features"""
    
    def __init__(self, tool_executor=None):
        """Initialize smart weather agent"""
        tools = [
            {
                "name": "get_weather",
                "description": "Get weather information"
            }
        ]
        super().__init__(
            name="Smart Weather Agent",
            description="Enhanced weather agent with smart features",
            tools=tools,
            tool_executor=tool_executor
        )
    
    def _parse_user_input(self, user_input: str, context: Optional[Dict[str, Any]] = None):
        """Parse user input with smart features"""
        from .watsonx_agent import ToolCall
        tool_calls = []
        
        # Extract location
        location = self._extract_location(user_input)
        if location:
            # Determine units
            units = "celsius"
            if any(word in user_input.lower() for word in ["fahrenheit", "°f", "f"]):
                units = "fahrenheit"
            
            tool_calls.append(ToolCall("get_weather", {
                "location": location,
                "units": units
            }))
        
        return tool_calls


class DataAnalysisAgent(WatsonxAgent):
    """Advanced data analysis agent"""
    
    def __init__(self, tool_executor=None):
        """Initialize data analysis agent"""
        tools = [
            {
                "name": "calculate_statistics",
                "description": "Calculate statistics"
            }
        ]
        super().__init__(
            name="Data Analysis Agent",
            description="Advanced data analysis agent",
            tools=tools,
            tool_executor=tool_executor
        )
    
    def _parse_user_input(self, user_input: str, context: Optional[Dict[str, Any]] = None):
        """Parse user input for data analysis"""
        from .watsonx_agent import ToolCall
        tool_calls = []
        
        # Extract numbers
        numbers = self._extract_numbers(user_input)
        if numbers:
            # Determine which measures to calculate
            measures = ["all"]
            if "mean" in user_input.lower():
                measures = ["mean"]
            elif "median" in user_input.lower():
                measures = ["median"]
            elif "mode" in user_input.lower():
                measures = ["mode"]
            elif "stdev" in user_input.lower() or "standard" in user_input.lower():
                measures = ["stdev"]
            
            tool_calls.append(ToolCall("calculate_statistics", {
                "numbers": numbers,
                "measures": measures
            }))
        
        return tool_calls


async def example_weather_agent():
    """Example: Using the weather agent"""
    print("\n" + "=" * 60)
    print("Example 1: Weather Agent")
    print("=" * 60)
    
    agent = WeatherAgent(execute_tool)
    
    user_input = "What's the weather in Tokyo, Japan?"
    print(f"\nUser Input: {user_input}")
    
    execution = await agent.execute("exec-001", user_input)
    
    print(f"\nExecution Result:")
    print(json.dumps(execution.to_dict(), indent=2))


async def example_analytics_agent():
    """Example: Using the analytics agent"""
    print("\n" + "=" * 60)
    print("Example 2: Analytics Agent")
    print("=" * 60)
    
    agent = AnalyticsAgent(execute_tool)
    
    user_input = "Calculate statistics for: 10, 20, 30, 40, 50, 60, 70, 80, 90, 100"
    print(f"\nUser Input: {user_input}")
    
    execution = await agent.execute("exec-002", user_input)
    
    print(f"\nExecution Result:")
    print(json.dumps(execution.to_dict(), indent=2))


async def example_compound_agent():
    """Example: Using the compound agent"""
    print("\n" + "=" * 60)
    print("Example 3: Compound Agent")
    print("=" * 60)
    
    agent = CompoundAgent(execute_tool)
    
    user_input = "Get weather for London, UK and calculate stats for 5, 10, 15, 20, 25"
    print(f"\nUser Input: {user_input}")
    
    execution = await agent.execute("exec-003", user_input)
    
    print(f"\nExecution Result:")
    print(json.dumps(execution.to_dict(), indent=2))


async def example_smart_weather_agent():
    """Example: Using the smart weather agent"""
    print("\n" + "=" * 60)
    print("Example 4: Smart Weather Agent")
    print("=" * 60)
    
    agent = SmartWeatherAgent(execute_tool)
    
    user_input = "What's the weather in New York, USA in Fahrenheit?"
    print(f"\nUser Input: {user_input}")
    
    execution = await agent.execute("exec-004", user_input)
    
    print(f"\nExecution Result:")
    print(json.dumps(execution.to_dict(), indent=2))


async def example_data_analysis_agent():
    """Example: Using the data analysis agent"""
    print("\n" + "=" * 60)
    print("Example 5: Data Analysis Agent")
    print("=" * 60)
    
    agent = DataAnalysisAgent(execute_tool)
    
    user_input = "Analyze the mean of: 100, 200, 300, 400, 500"
    print(f"\nUser Input: {user_input}")
    
    execution = await agent.execute("exec-005", user_input)
    
    print(f"\nExecution Result:")
    print(json.dumps(execution.to_dict(), indent=2))


async def example_agent_factory():
    """Example: Using the agent factory"""
    print("\n" + "=" * 60)
    print("Example 6: Agent Factory")
    print("=" * 60)
    
    # Get available agents
    available = AgentFactory.get_available_agents()
    print(f"\nAvailable Agents: {available}")
    
    # Create agents dynamically
    for agent_type in available:
        agent = AgentFactory.create_agent(agent_type, execute_tool)
        if agent:
            print(f"\n✓ Created {agent_type} agent: {agent.name}")


async def example_agent_execution_flow():
    """Example: Complete agent execution flow"""
    print("\n" + "=" * 60)
    print("Example 7: Complete Agent Execution Flow")
    print("=" * 60)
    
    # Create agent
    agent = WeatherAgent(execute_tool)
    print(f"\n1. Created agent: {agent.name}")
    
    # Get agent info
    info = agent.get_agent_info()
    print(f"2. Agent info: {info['name']} - {info['description']}")
    
    # Execute agent
    user_input = "Weather in Paris, France"
    print(f"3. Executing with input: {user_input}")
    
    execution = await agent.execute("exec-flow", user_input)
    print(f"4. Execution state: {execution.state.value}")
    
    # Get execution details
    print(f"5. Tool calls made: {len(execution.tool_calls)}")
    for tool_call in execution.tool_calls:
        print(f"   - {tool_call.tool_name}: {tool_call.result is not None}")
    
    # Get result
    if execution.result:
        print(f"6. Result summary: {execution.result.get('summary')}")


async def run_all_examples():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("watsonx Orchestrate Agent Examples")
    print("=" * 80)
    
    try:
        await example_weather_agent()
        await example_analytics_agent()
        await example_compound_agent()
        await example_smart_weather_agent()
        await example_data_analysis_agent()
        await example_agent_factory()
        await example_agent_execution_flow()
        
        print("\n" + "=" * 80)
        print("All examples completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ Error running examples: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_all_examples())

# Made with Bob
