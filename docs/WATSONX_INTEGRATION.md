# watsonx Orchestrate Integration Guide

This guide provides comprehensive instructions for integrating the MCP Server with watsonx Orchestrate.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Tool Import](#tool-import)
4. [Agent Creation](#agent-creation)
5. [Agent Execution](#agent-execution)
6. [API Reference](#api-reference)
7. [Troubleshooting](#troubleshooting)

## Overview

The MCP Server provides two tools that can be integrated into watsonx Orchestrate:

1. **get_weather**: Retrieve weather information for a location
2. **calculate_statistics**: Calculate statistical measures from data

These tools are exposed through REST APIs and can be used by watsonx Orchestrate agents.

## Prerequisites

- MCP Server running and accessible
- watsonx Orchestrate environment configured
- API credentials for watsonx Orchestrate
- Python 3.8+ (for running integration scripts)

## Tool Import

### Step 1: Generate Tool Package

Run the import script to generate the tool package:

```bash
python src/mcp_server/import_tools.py --output-dir watsonx_tools
```

This creates:
- `watsonx_tools/manifest.json`: Tool manifest for import
- `watsonx_tools/registry.json`: Tool registry
- `watsonx_tools/README.md`: Documentation

### Step 2: Review Generated Files

```bash
cat watsonx_tools/manifest.json
```

The manifest contains:
- Tool definitions in watsonx format
- Server information
- Tool metadata and capabilities

### Step 3: Import into watsonx Orchestrate

1. Log in to watsonx Orchestrate
2. Navigate to Tools/Integrations
3. Click "Import Tools"
4. Upload `watsonx_tools/manifest.json`
5. Configure the MCP server URL
6. Click "Import"

### Step 4: Verify Import

1. Go to Tools section
2. Search for "get_weather" and "calculate_statistics"
3. Verify both tools are listed and active

## Agent Creation

### Available Agents

The system provides two pre-built agents:

#### 1. Weather Agent

Specialized for weather-related queries.

**Example Usage:**
```json
{
  "agent_type": "weather",
  "user_input": "What's the weather in London, UK?"
}
```

#### 2. Analytics Agent

Specialized for data analysis and statistics.

**Example Usage:**
```json
{
  "agent_type": "analytics",
  "user_input": "Calculate statistics for: 10, 20, 30, 40, 50"
}
```

### Creating Custom Agents

To create a custom agent:

1. Extend the `WatsonxAgent` class
2. Implement `_parse_user_input()` method
3. Register with `AgentFactory`

Example:

```python
from mcp_server.watsonx_agent import WatsonxAgent

class CustomAgent(WatsonxAgent):
    def __init__(self, tool_executor=None):
        super().__init__(
            name="Custom Agent",
            description="My custom agent",
            tools=[...],
            tool_executor=tool_executor
        )
    
    def _parse_user_input(self, user_input, context=None):
        # Implement custom parsing logic
        pass
```

## Agent Execution

### API Endpoints

#### 1. List Available Agents

**GET** `/agents`

```bash
curl http://localhost:8000/agents
```

Response:
```json
{
  "agents": ["weather", "analytics"],
  "count": 2
}
```

#### 2. Get Agent Information

**GET** `/agents/{agent_type}`

```bash
curl http://localhost:8000/agents/weather
```

Response:
```json
{
  "success": true,
  "agent": {
    "name": "Weather Agent",
    "description": "Agent for retrieving weather information",
    "tools": [...],
    "created_at": "2024-01-15T10:30:00.000Z",
    "execution_count": 5
  }
}
```

#### 3. Execute Agent

**POST** `/agents/execute`

```bash
curl -X POST http://localhost:8000/agents/execute \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "weather",
    "user_input": "What is the weather in Paris, France?",
    "context": {}
  }'
```

Response:
```json
{
  "success": true,
  "execution_id": "550e8400-e29b-41d4-a716-446655440000",
  "agent_name": "Weather Agent",
  "state": "completed",
  "result": {
    "summary": "Executed 1 tool(s)",
    "tool_results": [
      {
        "tool": "get_weather",
        "result": {
          "success": true,
          "location": "Paris, France",
          "weather": {
            "temperature": "22.5°C",
            "condition": "Partly Cloudy",
            "humidity": "65%",
            "wind_speed": "15 km/h"
          }
        }
      }
    ],
    "execution_time": "0.45s"
  },
  "error": null
}
```

#### 4. Get Execution History

**GET** `/agents/executions?agent_type=weather&limit=10`

```bash
curl "http://localhost:8000/agents/executions?agent_type=weather&limit=10"
```

Response:
```json
{
  "success": true,
  "count": 5,
  "executions": [
    {
      "execution_id": "550e8400-e29b-41d4-a716-446655440000",
      "agent_name": "Weather Agent",
      "user_input": "What is the weather in Paris, France?",
      "state": "completed",
      "tool_calls": [...],
      "result": {...},
      "error": null,
      "start_time": "2024-01-15T10:30:00.000Z",
      "end_time": "2024-01-15T10:30:00.450Z"
    }
  ]
}
```

#### 5. Get Specific Execution

**GET** `/agents/executions/{execution_id}`

```bash
curl http://localhost:8000/agents/executions/550e8400-e29b-41d4-a716-446655440000
```

## API Reference

### Agent Execution Request

```json
{
  "agent_type": "string (required)",
  "user_input": "string (required)",
  "context": {
    "key": "value"
  }
}
```

### Agent Execution Response

```json
{
  "success": boolean,
  "execution_id": "string",
  "agent_name": "string",
  "state": "idle|running|completed|failed|paused",
  "result": {
    "summary": "string",
    "tool_results": [...],
    "execution_time": "string"
  },
  "error": "string or null"
}
```

### Tool Call Structure

```json
{
  "tool_name": "string",
  "parameters": {
    "key": "value"
  },
  "result": {...},
  "error": "string or null",
  "timestamp": "ISO 8601 timestamp"
}
```

## Integration with watsonx Orchestrate

### Step 1: Create Orchestration Flow

1. In watsonx Orchestrate, create a new flow
2. Add an "Execute Tool" action
3. Select the imported MCP tools

### Step 2: Configure Tool Parameters

For each tool, configure:
- Input parameters
- Error handling
- Output mapping

### Step 3: Add Agent Execution

1. Add an "Execute Agent" action
2. Select agent type (weather, analytics, etc.)
3. Map user input from flow variables
4. Configure result handling

### Step 4: Test the Flow

1. Click "Test"
2. Provide sample input
3. Verify tool execution and results

## Troubleshooting

### Tools Not Appearing in watsonx

**Problem**: Imported tools don't appear in watsonx Orchestrate

**Solutions**:
1. Verify MCP server is running: `curl http://localhost:8000/health`
2. Check manifest.json is valid: `python -m json.tool watsonx_tools/manifest.json`
3. Verify server URL in watsonx configuration
4. Check firewall/network connectivity

### Agent Execution Fails

**Problem**: Agent execution returns error

**Solutions**:
1. Check MCP server logs for errors
2. Verify tool parameters are correct
3. Test tool directly: `curl -X POST http://localhost:8000/tools/execute ...`
4. Check agent type is valid: `curl http://localhost:8000/agents`

### Tool Execution Timeout

**Problem**: Tool execution times out

**Solutions**:
1. Increase timeout in watsonx configuration
2. Check MCP server performance
3. Verify network connectivity
4. Check server logs for slow operations

### Invalid Tool Parameters

**Problem**: Tool execution fails with parameter error

**Solutions**:
1. Review tool schema: `curl http://localhost:8000/tools/{tool_name}`
2. Verify parameter types match schema
3. Check required parameters are provided
4. Validate parameter values

## Best Practices

1. **Error Handling**: Always implement error handling in agent flows
2. **Logging**: Enable detailed logging for debugging
3. **Testing**: Test tools individually before using in agents
4. **Performance**: Monitor execution times and optimize as needed
5. **Security**: Use API keys and secure connections in production
6. **Documentation**: Document custom agents and their usage

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review MCP server logs
3. Consult watsonx Orchestrate documentation
4. Contact support team

## Additional Resources

- [MCP Server API Documentation](API.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Main README](../README.md)