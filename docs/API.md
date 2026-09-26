# MCP Server API Documentation

## Overview

This document describes the API endpoints for the MCP Server for watsonx Orchestrate.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the server does not require authentication. In production, implement API key or OAuth2 authentication.

## Endpoints

### 1. Root Endpoint

**GET** `/`

Returns server information and available endpoints.

**Response:**
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

### 2. Health Check

**GET** `/health`

Check if the server is running and healthy.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1234567890.123
}
```

### 3. List Tools

**GET** `/tools`

Get a list of all available MCP tools.

**Response:**
```json
{
  "tools": [
    {
      "name": "get_weather",
      "description": "Get current weather information for a specified location...",
      "inputSchema": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "The city and country"
          },
          "units": {
            "type": "string",
            "enum": ["celsius", "fahrenheit"],
            "default": "celsius"
          }
        },
        "required": ["location"]
      }
    },
    {
      "name": "calculate_statistics",
      "description": "Calculate statistical measures from a list of numbers...",
      "inputSchema": {
        "type": "object",
        "properties": {
          "numbers": {
            "type": "array",
            "items": {"type": "number"},
            "description": "List of numbers to analyze"
          },
          "measures": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Statistical measures to calculate"
          }
        },
        "required": ["numbers"]
      }
    }
  ]
}
```

### 4. Get Tool Information

**GET** `/tools/{tool_name}`

Get detailed information about a specific tool.

**Parameters:**
- `tool_name` (string, required): Name of the tool

**Example:**
```
GET /tools/get_weather
```

**Response:**
```json
{
  "name": "get_weather",
  "description": "Get current weather information for a specified location...",
  "inputSchema": { ... }
}
```

**Error Response (404):**
```json
{
  "detail": "Tool 'invalid_tool' not found"
}
```

### 5. Execute Tool

**POST** `/tools/execute`

Execute a specific tool with given parameters.

**Request Body:**
```json
{
  "tool_name": "get_weather",
  "parameters": {
    "location": "London, UK",
    "units": "celsius"
  }
}
```

**Response (Success):**
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

**Response (Failure):**
```json
{
  "success": false,
  "result": {
    "success": false,
    "error": "Tool 'invalid_tool' not found"
  },
  "error": "Tool 'invalid_tool' not found"
}
```

## MCP Protocol Endpoints

### 1. Initialize

**POST** `/mcp/initialize`

Initialize the MCP protocol connection.

**Response:**
```json
{
  "protocolVersion": "1.0.0",
  "serverInfo": {
    "name": "mcp-watsonx-server",
    "version": "1.0.0"
  },
  "capabilities": {
    "tools": {
      "listChanged": false
    }
  }
}
```

### 2. List Tools (MCP Protocol)

**POST** `/mcp/tools/list`

List all available tools using MCP protocol.

**Response:**
```json
{
  "tools": [ ... ]
}
```

### 3. Call Tool (MCP Protocol)

**POST** `/mcp/tools/call`

Call a tool using MCP protocol.

**Request Body:**
```json
{
  "name": "get_weather",
  "arguments": {
    "location": "Paris, France"
  }
}
```

**Response:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"success\": true, \"location\": \"Paris, France\", ...}"
    }
  ]
}
```

## Tools

### Tool 1: get_weather

Get current weather information for a specified location.

**Parameters:**
- `location` (string, required): City and country (e.g., "London, UK")
- `units` (string, optional): Temperature units - "celsius" or "fahrenheit" (default: "celsius")

**Returns:**
- `success` (boolean): Whether the operation was successful
- `location` (string): The requested location
- `timestamp` (string): ISO 8601 timestamp
- `weather` (object): Weather information including temperature, condition, humidity, wind speed

**Example:**
```bash
curl -X POST http://localhost:8000/tools/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_weather",
    "parameters": {
      "location": "Tokyo, Japan",
      "units": "celsius"
    }
  }'
```

### Tool 2: calculate_statistics

Calculate statistical measures from a list of numbers.

**Parameters:**
- `numbers` (array of numbers, required): List of numbers to analyze
- `measures` (array of strings, optional): Statistical measures to calculate
  - Available measures: "mean", "median", "mode", "stdev", "min", "max", "all"
  - Default: ["all"]

**Returns:**
- `success` (boolean): Whether the operation was successful
- `count` (integer): Number of values analyzed
- `statistics` (object): Calculated statistics

**Example:**
```bash
curl -X POST http://localhost:8000/tools/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "calculate_statistics",
    "parameters": {
      "numbers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
      "measures": ["mean", "median", "stdev"]
    }
  }'
```

## Error Handling

The API returns appropriate HTTP status codes:

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error responses include a `detail` field with error information:

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Rate Limiting

Currently, no rate limiting is implemented. In production, implement rate limiting to prevent abuse.

## CORS

The server allows requests from all origins (`*`). In production, restrict CORS to specific domains.

## Logging

All requests and tool executions are logged. Log level can be configured via the `MCP_LOG_LEVEL` environment variable.

## Configuration

Server configuration can be set via environment variables:

- `MCP_HOST`: Server host (default: "0.0.0.0")
- `MCP_PORT`: Server port (default: 8000)
- `MCP_DEBUG`: Enable debug mode (default: false)
- `MCP_LOG_LEVEL`: Logging level (default: "INFO")
- `WEATHER_API_KEY`: API key for weather service (optional)
- `WATSONX_API_KEY`: API key for watsonx (optional)
- `WATSONX_PROJECT_ID`: watsonx project ID (optional)