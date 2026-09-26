# watsonx Orchestrate Agent Guide

This guide provides comprehensive information about creating, deploying, and using agents with the MCP Server.

## Table of Contents

1. [Agent Overview](#agent-overview)
2. [Available Agents](#available-agents)
3. [Creating Custom Agents](#creating-custom-agents)
4. [Agent Execution](#agent-execution)
5. [Testing Agents](#testing-agents)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Agent Overview

An agent is an intelligent system that:
- Understands user input
- Determines which tools to use
- Executes tools in sequence
- Generates meaningful results

### Agent Lifecycle

```
User Input → Parse Input → Execute Tools → Generate Result → Return Output
```

### Agent States

- **IDLE**: Agent is ready but not executing
- **RUNNING**: Agent is currently executing
- **COMPLETED**: Agent execution finished successfully
- **FAILED**: Agent execution encountered an error
- **PAUSED**: Agent execution is paused

## Available Agents

### 1. Weather Agent

**Purpose**: Retrieve weather information for locations

**Capabilities**:
- Get current weather
- Support multiple temperature units (Celsius, Fahrenheit)
- Extract location from natural language

**Example Usage**:
```json
{
  "agent_type": "weather",
  "user_input": "What's the weather in London, UK?"
}
```

**Supported Queries**:
- "Weather in Paris, France"
- "Temperature in New York in Fahrenheit"
- "Current conditions in Tokyo, Japan"

### 2. Analytics Agent

**Purpose**: Perform data analysis and statistical calculations

**Capabilities**:
- Calculate mean, median, mode
- Compute standard deviation
- Find min/max values
- Extract numbers from text

**Example Usage**:
```json
{
  "agent_type": "analytics",
  "user_input": "Calculate statistics for: 10, 20, 30, 40, 50"
}
```

**Supported Queries**:
- "Statistics for 1, 2, 3, 4, 5"
- "Calculate mean of 100, 200, 300"
- "Find average of these numbers: 5, 10, 15, 20"

## Creating Custom Agents

### Step 1: Extend WatsonxAgent

```python
from mcp_server.watsonx_agent import WatsonxAgent, ToolCall

class MyCustomAgent(WatsonxAgent):
    def __init__(self, tool_executor=None):
        super().__init__(
            name="My Custom Agent",
            description="Description of my agent",
            tools=[...],
            tool_executor=tool_executor
        )
```

### Step 2: Implement Input Parsing

```python
def _parse_user_input(self, user_input, context=None):
    """Parse user input to determine tool calls"""
    tool_calls = []
    
    # Your custom parsing logic here
    if "keyword" in user_input.lower():
        tool_calls.append(ToolCall("tool_name", {"param": "value"}))
    
    return tool_calls
```

### Step 3: Register with Factory

```python
from mcp_server.watsonx_agent import AgentFactory

# Add to AgentFactory.create_agent()
agents = {
    "my_agent": MyCustomAgent,
    ...
}
```

### Complete Example

```python
from mcp_server.watsonx_agent import WatsonxAgent, ToolCall

class SalesAgent(WatsonxAgent):
    """Agent for sales-related queries"""
    
    def __init__(self, tool_executor=None):
        tools = [
            {"name": "get_sales_data", "description": "Get sales data"},
            {"name": "calculate_statistics", "description": "Calculate stats"}
        ]
        super().__init__(
            name="Sales Agent",
            description="Agent for sales analysis",
            tools=tools,
            tool_executor=tool_executor
        )
    
    def _parse_user_input(self, user_input, context=None):
        tool_calls = []
        
        if "sales" in user_input.lower():
            # Extract parameters from user input
            tool_calls.append(ToolCall("get_sales_data", {}))
        
        if "statistics" in user_input.lower() or "analyze" in user_input.lower():
            numbers = self._extract_numbers(user_input)
            if numbers:
                tool_calls.append(ToolCall("calculate_statistics", {
                    "numbers": numbers
                }))
        
        return tool_calls
```

## Agent Execution

### Via REST API

#### Execute Agent

```bash
curl -X POST http://localhost:8000/agents/execute \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "weather",
    "user_input": "What is the weather in Berlin, Germany?",
    "context": {}
  }'
```

**Response**:
```json
{
  "success": true,
  "execution_id": "550e8400-e29b-41d4-a716-446655440000",
  "agent_name": "Weather Agent",
  "state": "completed",
  "result": {
    "summary": "Executed 1 tool(s)",
    "tool_results": [...],
    "execution_time": "0.45s"
  },
  "error": null
}
```

#### Get Execution History

```bash
curl "http://localhost:8000/agents/executions?agent_type=weather&limit=5"
```

### Via Python

```python
import asyncio
from mcp_server.watsonx_agent import WeatherAgent
from mcp_server.tools import execute_tool

async def main():
    agent = WeatherAgent(execute_tool)
    execution = await agent.execute(
        "exec-001",
        "What's the weather in Rome, Italy?"
    )
    print(execution.to_dict())

asyncio.run(main())
```

## Testing Agents

### Unit Tests

```python
import pytest
from mcp_server.watsonx_agent import WeatherAgent
from mcp_server.tools import execute_tool

@pytest.mark.asyncio
async def test_weather_agent():
    agent = WeatherAgent(execute_tool)
    execution = await agent.execute("test-001", "Weather in London")
    
    assert execution.state.value == "completed"
    assert len(execution.tool_calls) > 0
    assert execution.result is not None
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_agent_with_real_tools():
    agent = WeatherAgent(execute_tool)
    execution = await agent.execute(
        "test-002",
        "What is the weather in Tokyo, Japan?"
    )
    
    assert execution.state.value == "completed"
    assert execution.result["tool_results"][0]["tool"] == "get_weather"
```

### Manual Testing

```bash
# Run verification script
python src/mcp_server/verify_agent.py

# Run examples
python src/mcp_server/agent_examples.py
```

## Best Practices

### 1. Input Parsing

- Use natural language processing for better understanding
- Extract parameters carefully
- Handle edge cases and invalid input
- Provide helpful error messages

### 2. Tool Selection

- Choose appropriate tools for the task
- Minimize unnecessary tool calls
- Handle tool failures gracefully
- Implement fallback strategies

### 3. Error Handling

```python
def _parse_user_input(self, user_input, context=None):
    try:
        # Parsing logic
        pass
    except Exception as e:
        # Log error
        print(f"Error parsing input: {e}")
        return []
```

### 4. Performance

- Cache frequently used data
- Optimize tool execution order
- Monitor execution time
- Implement timeouts

### 5. Logging

```python
import logging

logger = logging.getLogger(__name__)

async def execute(self, execution_id, user_input, context=None):
    logger.info(f"Executing agent with input: {user_input}")
    # ... execution logic ...
    logger.info(f"Execution {execution_id} completed")
```

### 6. Documentation

- Document agent purpose and capabilities
- Provide usage examples
- List supported queries
- Explain tool selection logic

## Troubleshooting

### Agent Not Executing

**Problem**: Agent execution fails or returns error

**Solutions**:
1. Check MCP server is running: `curl http://localhost:8000/health`
2. Verify agent type is valid: `curl http://localhost:8000/agents`
3. Check tool executor is configured
4. Review server logs for errors

### Tool Not Found

**Problem**: Agent can't find required tool

**Solutions**:
1. Verify tool is registered: `curl http://localhost:8000/tools`
2. Check tool name matches exactly
3. Verify tool executor is passed to agent
4. Check tool parameters are correct

### Incorrect Results

**Problem**: Agent returns unexpected results

**Solutions**:
1. Test tool directly: `curl -X POST http://localhost:8000/tools/execute ...`
2. Review input parsing logic
3. Check tool parameters
4. Verify context is correct

### Performance Issues

**Problem**: Agent execution is slow

**Solutions**:
1. Monitor tool execution time
2. Optimize input parsing
3. Reduce number of tool calls
4. Check server resources

## Advanced Topics

### Context Passing

```python
context = {
    "user_id": "user123",
    "session_id": "session456",
    "preferences": {"units": "celsius"}
}

execution = await agent.execute(
    "exec-001",
    "What's the weather?",
    context=context
)
```

### Execution History

```python
# Get all executions
executions = agent.get_all_executions()

# Get specific execution
execution = agent.get_execution("exec-001")

# Export execution
execution_dict = execution.to_dict()
```

### Custom Tool Executor

```python
async def custom_executor(tool_name, **kwargs):
    # Custom execution logic
    if tool_name == "get_weather":
        # Custom weather logic
        pass
    return result

agent = WeatherAgent(custom_executor)
```

## Examples

### Example 1: Simple Weather Query

```bash
curl -X POST http://localhost:8000/agents/execute \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "weather",
    "user_input": "Weather in Madrid, Spain"
  }'
```

### Example 2: Data Analysis

```bash
curl -X POST http://localhost:8000/agents/execute \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "analytics",
    "user_input": "Analyze: 100, 200, 300, 400, 500"
  }'
```

### Example 3: With Context

```bash
curl -X POST http://localhost:8000/agents/execute \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "weather",
    "user_input": "Weather in Rome",
    "context": {
      "user_preference": "fahrenheit"
    }
  }'
```

## Support

For issues or questions:
1. Check this guide
2. Review API documentation
3. Check troubleshooting section
4. Review server logs
5. Contact support team