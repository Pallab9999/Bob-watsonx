# Agent Verification Guide for watsonx Orchestrate

This guide provides step-by-step instructions for verifying that agents are working correctly in watsonx Orchestrate.

## Table of Contents

1. [Pre-Verification Checklist](#pre-verification-checklist)
2. [Server Verification](#server-verification)
3. [Tool Verification](#tool-verification)
4. [Agent Verification](#agent-verification)
5. [Integration Verification](#integration-verification)
6. [Performance Testing](#performance-testing)
7. [Troubleshooting](#troubleshooting)

## Pre-Verification Checklist

Before starting verification, ensure:

- [ ] MCP Server is installed and configured
- [ ] Python 3.8+ is installed
- [ ] All dependencies are installed: `pip install -r requirements.txt`
- [ ] MCP Server is running: `python src/mcp_server/main.py`
- [ ] watsonx Orchestrate environment is accessible
- [ ] Network connectivity between server and watsonx is confirmed

## Server Verification

### 1. Check Server Health

```bash
curl http://localhost:8000/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "timestamp": 1234567890.123
}
```

**Verification**: Status should be "healthy"

### 2. Check Server Information

```bash
curl http://localhost:8000/
```

**Expected Response**:
```json
{
  "name": "MCP Server for watsonx Orchestrate",
  "version": "1.0.0",
  "status": "running",
  "endpoints": {
    "list_tools": "/tools",
    "execute_tool": "/tools/execute",
    "health": "/health"
  }
}
```

**Verification**: Server name and version should match

### 3. Check Server Logs

```bash
# Check for any errors in server logs
tail -f server.log
```

**Expected**: No error messages, only info/debug logs

## Tool Verification

### 1. List Available Tools

```bash
curl http://localhost:8000/tools
```

**Expected Response**:
```json
{
  "tools": [
    {
      "name": "get_weather",
      "description": "Get current weather information...",
      "inputSchema": { ... }
    },
    {
      "name": "calculate_statistics",
      "description": "Calculate statistical measures...",
      "inputSchema": { ... }
    }
  ]
}
```

**Verification**:
- [ ] Both tools are listed
- [ ] Tool names are correct
- [ ] Descriptions are present
- [ ] Input schemas are defined

### 2. Test get_weather Tool

```bash
curl -X POST http://localhost:8000/tools/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_weather",
    "parameters": {
      "location": "London, UK",
      "units": "celsius"
    }
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "result": {
    "success": true,
    "location": "London, UK",
    "timestamp": "2024-01-15T10:30:00.000Z",
    "weather": {
      "temperature": "22.5°C",
      "condition": "Partly Cloudy",
      "humidity": "65%",
      "wind_speed": "15 km/h",
      "description": "Current weather in London, UK"
    }
  },
  "error": null
}
```

**Verification**:
- [ ] Success is true
- [ ] Location matches input
- [ ] Weather data is present
- [ ] Temperature includes unit symbol

### 3. Test calculate_statistics Tool

```bash
curl -X POST http://localhost:8000/tools/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "calculate_statistics",
    "parameters": {
      "numbers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
      "measures": ["mean", "median", "min", "max", "stdev"]
    }
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "result": {
    "success": true,
    "count": 10,
    "statistics": {
      "mean": 5.5,
      "median": 5.5,
      "min": 1,
      "max": 10,
      "stdev": 3.03
    }
  },
  "error": null
}
```

**Verification**:
- [ ] Success is true
- [ ] Count matches input array length
- [ ] All requested measures are calculated
- [ ] Values are mathematically correct

## Agent Verification

### 1. List Available Agents

```bash
curl http://localhost:8000/agents
```

**Expected Response**:
```json
{
  "agents": ["weather", "analytics"],
  "count": 2
}
```

**Verification**:
- [ ] Both agents are listed
- [ ] Count is 2

### 2. Get Agent Information

```bash
curl http://localhost:8000/agents/weather
```

**Expected Response**:
```json
{
  "success": true,
  "agent": {
    "name": "Weather Agent",
    "description": "Agent for retrieving weather information",
    "tools": [...],
    "created_at": "2024-01-15T10:30:00.000Z",
    "execution_count": 0
  }
}
```

**Verification**:
- [ ] Agent name is correct
- [ ] Description is present
- [ ] Tools are listed
- [ ] Created timestamp is present

### 3. Execute Weather Agent

```bash
curl -X POST http://localhost:8000/agents/execute \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "weather",
    "user_input": "What is the weather in Paris, France?",
    "context": {}
  }'
```

**Expected Response**:
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
        "result": { ... }
      }
    ],
    "execution_time": "0.45s"
  },
  "error": null
}
```

**Verification**:
- [ ] Success is true
- [ ] Execution ID is generated
- [ ] State is "completed"
- [ ] Result contains tool results
- [ ] No errors

### 4. Execute Analytics Agent

```bash
curl -X POST http://localhost:8000/agents/execute \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "analytics",
    "user_input": "Calculate statistics for: 10, 20, 30, 40, 50",
    "context": {}
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "execution_id": "550e8400-e29b-41d4-a716-446655440001",
  "agent_name": "Analytics Agent",
  "state": "completed",
  "result": {
    "summary": "Executed 1 tool(s)",
    "tool_results": [
      {
        "tool": "calculate_statistics",
        "result": { ... }
      }
    ],
    "execution_time": "0.35s"
  },
  "error": null
}
```

**Verification**:
- [ ] Success is true
- [ ] State is "completed"
- [ ] Statistics are calculated
- [ ] No errors

### 5. Get Execution History

```bash
curl "http://localhost:8000/agents/executions?agent_type=weather&limit=5"
```

**Expected Response**:
```json
{
  "success": true,
  "count": 1,
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

**Verification**:
- [ ] Success is true
- [ ] Executions are returned
- [ ] Timestamps are present
- [ ] Tool calls are recorded

## Integration Verification

### 1. Verify Tool Import Package

```bash
# Check if tool package was created
ls -la watsonx_tools/

# Expected files:
# - manifest.json
# - registry.json
# - README.md
```

**Verification**:
- [ ] manifest.json exists
- [ ] registry.json exists
- [ ] README.md exists

### 2. Validate Manifest

```bash
# Validate JSON syntax
python -m json.tool watsonx_tools/manifest.json > /dev/null && echo "Valid JSON"

# Check manifest structure
cat watsonx_tools/manifest.json | grep -E '"name"|"version"|"tools"'
```

**Verification**:
- [ ] JSON is valid
- [ ] Manifest contains tools
- [ ] Version is present

### 3. Verify watsonx Integration

In watsonx Orchestrate:

1. Navigate to Tools/Integrations
2. Check if MCP tools are imported
3. Verify tool definitions match manifest
4. Test tool execution in watsonx UI

**Verification**:
- [ ] Tools appear in watsonx
- [ ] Tool descriptions are correct
- [ ] Tool parameters match schema
- [ ] Tools execute successfully

## Performance Testing

### 1. Response Time Test

```bash
# Test tool execution time
time curl -X POST http://localhost:8000/tools/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_weather",
    "parameters": {"location": "London, UK"}
  }'
```

**Expected**: Response time < 1 second

### 2. Load Test

```bash
# Test with multiple concurrent requests
for i in {1..10}; do
  curl -X POST http://localhost:8000/tools/execute \
    -H "Content-Type: application/json" \
    -d '{"tool_name": "get_weather", "parameters": {"location": "London, UK"}}' &
done
wait
```

**Expected**: All requests complete successfully

### 3. Agent Execution Time

```bash
# Measure agent execution time
time curl -X POST http://localhost:8000/agents/execute \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "weather",
    "user_input": "Weather in London"
  }'
```

**Expected**: Execution time < 2 seconds

## Troubleshooting

### Issue: Server Not Responding

**Symptoms**: Connection refused or timeout

**Solutions**:
1. Check if server is running: `ps aux | grep python`
2. Check port is available: `netstat -an | grep 8000`
3. Restart server: `python src/mcp_server/main.py`
4. Check firewall settings

### Issue: Tools Not Found

**Symptoms**: 404 error when listing tools

**Solutions**:
1. Verify tools are registered in tools.py
2. Check server logs for import errors
3. Restart server
4. Verify Python path is correct

### Issue: Agent Execution Fails

**Symptoms**: Agent returns error state

**Solutions**:
1. Check tool executor is configured
2. Verify tool parameters are correct
3. Check server logs for errors
4. Test tool directly

### Issue: Incorrect Results

**Symptoms**: Tool returns unexpected values

**Solutions**:
1. Verify input parameters
2. Check tool implementation
3. Test with different inputs
4. Review tool documentation

## Verification Checklist

Complete this checklist to verify everything is working:

### Server
- [ ] Server is running
- [ ] Health check passes
- [ ] Server info is correct
- [ ] No errors in logs

### Tools
- [ ] Both tools are listed
- [ ] get_weather tool works
- [ ] calculate_statistics tool works
- [ ] Tool parameters are correct

### Agents
- [ ] Both agents are listed
- [ ] Weather agent executes
- [ ] Analytics agent executes
- [ ] Execution history is recorded

### Integration
- [ ] Tool package is created
- [ ] Manifest is valid
- [ ] Tools are imported in watsonx
- [ ] Tools work in watsonx UI

### Performance
- [ ] Response time < 1 second
- [ ] Load test passes
- [ ] Agent execution < 2 seconds
- [ ] No memory leaks

## Next Steps

After verification:

1. **Deploy to Production**: Follow deployment guide
2. **Configure Security**: Set up authentication and HTTPS
3. **Monitor Performance**: Set up monitoring and alerting
4. **Create Custom Agents**: Develop domain-specific agents
5. **Integrate with Workflows**: Use agents in watsonx workflows

## Support

For issues:
1. Check this verification guide
2. Review troubleshooting section
3. Check server logs
4. Consult API documentation
5. Contact support team