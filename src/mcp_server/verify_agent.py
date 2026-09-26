"""
Agent Verification Script

This script verifies that agents are working correctly with the MCP tools.
"""

import asyncio
import json
import sys
from datetime import datetime


async def verify_agent_setup():
    """Verify agent setup"""
    print("\n" + "=" * 70)
    print("Agent Setup Verification")
    print("=" * 70)
    
    try:
        from .watsonx_agent import AgentFactory
        
        # Get available agents
        available_agents = AgentFactory.get_available_agents()
        print(f"\n✓ Available agents: {available_agents}")
        
        if len(available_agents) == 0:
            print("✗ No agents available")
            return False
        
        # Create each agent
        for agent_type in available_agents:
            agent = AgentFactory.create_agent(agent_type)
            if agent:
                print(f"✓ Created {agent_type} agent: {agent.name}")
            else:
                print(f"✗ Failed to create {agent_type} agent")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error verifying agent setup: {str(e)}")
        return False


async def verify_tool_execution():
    """Verify tool execution"""
    print("\n" + "=" * 70)
    print("Tool Execution Verification")
    print("=" * 70)
    
    try:
        from .tools import execute_tool
        
        # Test get_weather tool
        print("\n[1/2] Testing get_weather tool...")
        weather_result = await execute_tool(
            "get_weather",
            location="London, UK",
            units="celsius"
        )
        
        if weather_result.get("success"):
            print("✓ get_weather tool executed successfully")
            print(f"  Location: {weather_result.get('location')}")
            print(f"  Temperature: {weather_result.get('weather', {}).get('temperature')}")
        else:
            print("✗ get_weather tool failed")
            return False
        
        # Test calculate_statistics tool
        print("\n[2/2] Testing calculate_statistics tool...")
        stats_result = await execute_tool(
            "calculate_statistics",
            numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            measures=["mean", "median", "min", "max"]
        )
        
        if stats_result.get("success"):
            print("✓ calculate_statistics tool executed successfully")
            stats = stats_result.get("statistics", {})
            print(f"  Mean: {stats.get('mean')}")
            print(f"  Median: {stats.get('median')}")
            print(f"  Min: {stats.get('min')}")
            print(f"  Max: {stats.get('max')}")
        else:
            print("✗ calculate_statistics tool failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error verifying tool execution: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def verify_weather_agent():
    """Verify weather agent"""
    print("\n" + "=" * 70)
    print("Weather Agent Verification")
    print("=" * 70)
    
    try:
        from .watsonx_agent import WeatherAgent
        from .tools import execute_tool
        
        agent = WeatherAgent(execute_tool)
        print(f"\n✓ Created agent: {agent.name}")
        
        # Test agent execution
        print("\nExecuting agent with user input: 'What is the weather in Paris, France?'")
        execution = await agent.execute(
            "verify-weather-001",
            "What is the weather in Paris, France?"
        )
        
        print(f"✓ Agent execution completed")
        print(f"  State: {execution.state.value}")
        print(f"  Tool calls: {len(execution.tool_calls)}")
        
        if execution.tool_calls:
            for tool_call in execution.tool_calls:
                print(f"  - {tool_call.tool_name}: {'Success' if tool_call.result else 'Failed'}")
        
        if execution.result:
            print(f"  Result: {execution.result.get('summary')}")
        
        if execution.error:
            print(f"✗ Error: {execution.error}")
            return False
        
        return execution.state.value == "completed"
        
    except Exception as e:
        print(f"✗ Error verifying weather agent: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def verify_analytics_agent():
    """Verify analytics agent"""
    print("\n" + "=" * 70)
    print("Analytics Agent Verification")
    print("=" * 70)
    
    try:
        from .watsonx_agent import AnalyticsAgent
        from .tools import execute_tool
        
        agent = AnalyticsAgent(execute_tool)
        print(f"\n✓ Created agent: {agent.name}")
        
        # Test agent execution
        print("\nExecuting agent with user input: 'Calculate statistics for 10, 20, 30, 40, 50'")
        execution = await agent.execute(
            "verify-analytics-001",
            "Calculate statistics for 10, 20, 30, 40, 50"
        )
        
        print(f"✓ Agent execution completed")
        print(f"  State: {execution.state.value}")
        print(f"  Tool calls: {len(execution.tool_calls)}")
        
        if execution.tool_calls:
            for tool_call in execution.tool_calls:
                print(f"  - {tool_call.tool_name}: {'Success' if tool_call.result else 'Failed'}")
        
        if execution.result:
            print(f"  Result: {execution.result.get('summary')}")
        
        if execution.error:
            print(f"✗ Error: {execution.error}")
            return False
        
        return execution.state.value == "completed"
        
    except Exception as e:
        print(f"✗ Error verifying analytics agent: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def verify_agent_api():
    """Verify agent API"""
    print("\n" + "=" * 70)
    print("Agent API Verification")
    print("=" * 70)
    
    try:
        from .agent_api import agent_manager, initialize_agents
        
        # Initialize agents
        print("\nInitializing agents...")
        initialize_agents()
        print("✓ Agents initialized")
        
        # Get available agents
        available = agent_manager.get_available_agents()
        print(f"✓ Available agents: {available}")
        
        # Get agent info
        for agent_type in available:
            info = agent_manager.get_agent_info(agent_type)
            if info:
                print(f"✓ {agent_type}: {info['name']}")
            else:
                print(f"✗ Failed to get info for {agent_type}")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error verifying agent API: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def run_verification():
    """Run all verification tests"""
    print("\n" + "=" * 70)
    print("watsonx Orchestrate Agent Verification")
    print("=" * 70)
    print(f"Start Time: {datetime.now().isoformat()}")
    
    results = []
    
    # Run verification tests
    results.append(("Agent Setup", await verify_agent_setup()))
    results.append(("Tool Execution", await verify_tool_execution()))
    results.append(("Weather Agent", await verify_weather_agent()))
    results.append(("Analytics Agent", await verify_analytics_agent()))
    results.append(("Agent API", await verify_agent_api()))
    
    # Print summary
    print("\n" + "=" * 70)
    print("Verification Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("=" * 70)
    print(f"Results: {passed}/{total} tests passed")
    print(f"End Time: {datetime.now().isoformat()}")
    print("=" * 70)
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_verification())
    sys.exit(0 if success else 1)

# Made with Bob
