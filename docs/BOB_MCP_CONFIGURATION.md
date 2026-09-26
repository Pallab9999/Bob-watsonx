# Configuring Bob to Access MCP Servers

This guide provides instructions for configuring Bob (IBM's AI assistant) to access MCP servers for watsonx Orchestrate development.

## Table of Contents

1. [Overview](#overview)
2. [Available MCP Servers](#available-mcp-servers)
3. [Configuration Steps](#configuration-steps)
4. [Verification](#verification)
5. [Usage Examples](#usage-examples)
6. [Troubleshooting](#troubleshooting)

## Overview

Bob can be configured to access specialized MCP servers that provide:
- **wxo-docs**: Public documentation for watsonx Orchestrate ADK
- **orchestrate-adk**: watsonx Orchestrate SDK for creating agents and tools

This enables Bob to:
- Answer questions about watsonx Orchestrate
- Provide code examples and best practices
- Help with agent and tool development
- Assist with troubleshooting and debugging

## Available MCP Servers

### 1. wxo-docs Server

**Purpose**: Provides access to watsonx Orchestrate documentation

**Capabilities**:
- Search documentation
- Retrieve API references
- Get code examples
- Access best practices guides

**Server URL**: `mcp://wxo-docs.example.com`

**Tools Available**:
- `search_docs`: Search documentation
- `get_api_reference`: Get API documentation
- `get_examples`: Get code examples
- `get_best_practices`: Get best practices

### 2. orchestrate-adk Server

**Purpose**: Provides access to watsonx Orchestrate SDK

**Capabilities**:
- Access SDK documentation
- Get SDK examples
- Retrieve SDK API reference
- Access SDK source code

**Server URL**: `mcp://orchestrate-adk.example.com`

**Tools Available**:
- `get_sdk_docs`: Get SDK documentation
- `get_sdk_examples`: Get SDK examples
- `get_sdk_api`: Get SDK API reference
- `search_sdk`: Search SDK

## Configuration Steps

### Step 1: Prepare MCP Server Configuration

Create a configuration file `bob_mcp_config.json`:

```json
{
  "mcp_servers": [
    {
      "name": "wxo-docs",
      "url": "mcp://wxo-docs.example.com",
      "description": "watsonx Orchestrate Documentation",
      "enabled": true,
      "tools": [
        "search_docs",
        "get_api_reference",
        "get_examples",
        "get_best_practices"
      ]
    },
    {
      "name": "orchestrate-adk",
      "url": "mcp://orchestrate-adk.example.com",
      "description": "watsonx Orchestrate SDK",
      "enabled": true,
      "tools": [
        "get_sdk_docs",
        "get_sdk_examples",
        "get_sdk_api",
        "search_sdk"
      ]
    }
  ],
  "bob_configuration": {
    "enable_mcp": true,
    "auto_connect": true,
    "timeout": 30,
    "retry_attempts": 3
  }
}
```

### Step 2: Register MCP Servers with Bob

```bash
# Using Bob CLI
bob config add-mcp-server \
  --name wxo-docs \
  --url mcp://wxo-docs.example.com \
  --description "watsonx Orchestrate Documentation"

bob config add-mcp-server \
  --name orchestrate-adk \
  --url mcp://orchestrate-adk.example.com \
  --description "watsonx Orchestrate SDK"
```

### Step 3: Enable MCP Access

```bash
# Enable MCP support in Bob
bob config set mcp.enabled true
bob config set mcp.auto_connect true
```

### Step 4: Verify Configuration

```bash
# List configured MCP servers
bob config list-mcp-servers

# Test connection to MCP servers
bob mcp test-connection wxo-docs
bob mcp test-connection orchestrate-adk
```

## Configuration File Format

### Complete Configuration Example

```json
{
  "version": "1.0.0",
  "mcp_servers": [
    {
      "id": "wxo-docs-prod",
      "name": "wxo-docs",
      "url": "mcp://wxo-docs.example.com",
      "port": 8001,
      "protocol": "mcp",
      "description": "watsonx Orchestrate Documentation Server",
      "enabled": true,
      "authentication": {
        "type": "api_key",
        "key_env_var": "WXO_DOCS_API_KEY"
      },
      "tools": [
        {
          "name": "search_docs",
          "description": "Search documentation"
        },
        {
          "name": "get_api_reference",
          "description": "Get API reference"
        },
        {
          "name": "get_examples",
          "description": "Get code examples"
        },
        {
          "name": "get_best_practices",
          "description": "Get best practices"
        }
      ],
      "timeout": 30,
      "retry_policy": {
        "max_attempts": 3,
        "backoff_factor": 2
      }
    },
    {
      "id": "orchestrate-adk-prod",
      "name": "orchestrate-adk",
      "url": "mcp://orchestrate-adk.example.com",
      "port": 8002,
      "protocol": "mcp",
      "description": "watsonx Orchestrate SDK Server",
      "enabled": true,
      "authentication": {
        "type": "api_key",
        "key_env_var": "ORCHESTRATE_ADK_API_KEY"
      },
      "tools": [
        {
          "name": "get_sdk_docs",
          "description": "Get SDK documentation"
        },
        {
          "name": "get_sdk_examples",
          "description": "Get SDK examples"
        },
        {
          "name": "get_sdk_api",
          "description": "Get SDK API reference"
        },
        {
          "name": "search_sdk",
          "description": "Search SDK"
        }
      ],
      "timeout": 30,
      "retry_policy": {
        "max_attempts": 3,
        "backoff_factor": 2
      }
    }
  ],
  "bob_configuration": {
    "enable_mcp": true,
    "auto_connect": true,
    "connection_timeout": 30,
    "request_timeout": 60,
    "max_concurrent_requests": 10,
    "cache_enabled": true,
    "cache_ttl": 3600
  }
}
```

## Verification

### Step 1: Check MCP Server Status

```bash
# Check if MCP servers are connected
bob mcp status

# Expected output:
# wxo-docs: Connected
# orchestrate-adk: Connected
```

### Step 2: Test MCP Tools

```bash
# Test wxo-docs tools
bob mcp call wxo-docs search_docs --query "agent creation"

# Test orchestrate-adk tools
bob mcp call orchestrate-adk get_sdk_docs --topic "agents"
```

### Step 3: Verify Bob Can Access Tools

```bash
# Ask Bob to use MCP tools
bob ask "How do I create an agent in watsonx Orchestrate?"

# Bob should use wxo-docs and orchestrate-adk to provide answer
```

## Usage Examples

### Example 1: Get Documentation

```bash
bob ask "What is the watsonx Orchestrate ADK?"

# Bob will:
# 1. Call wxo-docs.search_docs with query "ADK"
# 2. Call orchestrate-adk.get_sdk_docs
# 3. Provide comprehensive answer with references
```

### Example 2: Get Code Examples

```bash
bob ask "Show me an example of creating a custom agent"

# Bob will:
# 1. Call orchestrate-adk.get_sdk_examples with topic "agents"
# 2. Call wxo-docs.get_examples with query "custom agent"
# 3. Provide code examples and explanations
```

### Example 3: Get Best Practices

```bash
bob ask "What are the best practices for agent development?"

# Bob will:
# 1. Call wxo-docs.get_best_practices with topic "agents"
# 2. Call orchestrate-adk.search_sdk with query "best practices"
# 3. Provide comprehensive best practices guide
```

### Example 4: Troubleshooting

```bash
bob ask "How do I debug an agent that's not working?"

# Bob will:
# 1. Call wxo-docs.search_docs with query "debugging"
# 2. Call orchestrate-adk.get_sdk_examples with topic "debugging"
# 3. Provide troubleshooting steps and examples
```

## Environment Variables

Set these environment variables for authentication:

```bash
# wxo-docs API key
export WXO_DOCS_API_KEY="your-api-key-here"

# orchestrate-adk API key
export ORCHESTRATE_ADK_API_KEY="your-api-key-here"

# MCP configuration
export BOB_MCP_CONFIG_FILE="./bob_mcp_config.json"
export BOB_MCP_ENABLED="true"
```

## Advanced Configuration

### Custom Tool Mapping

```json
{
  "tool_mappings": {
    "wxo-docs": {
      "search_docs": {
        "description": "Search watsonx Orchestrate documentation",
        "parameters": {
          "query": "string",
          "limit": "integer"
        }
      }
    },
    "orchestrate-adk": {
      "get_sdk_examples": {
        "description": "Get SDK code examples",
        "parameters": {
          "topic": "string",
          "language": "string"
        }
      }
    }
  }
}
```

### Caching Configuration

```json
{
  "cache_configuration": {
    "enabled": true,
    "ttl": 3600,
    "max_size": "100MB",
    "storage": "memory",
    "invalidation_rules": [
      {
        "pattern": "docs/*",
        "ttl": 7200
      },
      {
        "pattern": "examples/*",
        "ttl": 3600
      }
    ]
  }
}
```

## Troubleshooting

### Issue: MCP Servers Not Connecting

**Symptoms**: Bob cannot connect to MCP servers

**Solutions**:
1. Check server URLs are correct
2. Verify network connectivity
3. Check API keys are set
4. Review Bob logs: `bob logs --level debug`

### Issue: Tools Not Available

**Symptoms**: Bob cannot find MCP tools

**Solutions**:
1. Verify tools are listed in configuration
2. Check server is connected: `bob mcp status`
3. Restart Bob: `bob restart`
4. Reload configuration: `bob config reload`

### Issue: Slow Responses

**Symptoms**: Bob takes long time to respond

**Solutions**:
1. Check server performance
2. Enable caching: `bob config set cache.enabled true`
3. Increase timeout: `bob config set timeout 60`
4. Check network latency

### Issue: Authentication Errors

**Symptoms**: Authentication failed errors

**Solutions**:
1. Verify API keys are set correctly
2. Check API key permissions
3. Regenerate API keys if needed
4. Check key expiration

## Best Practices

1. **Keep Configuration Updated**: Regularly update MCP server URLs and credentials
2. **Enable Caching**: Improve performance by enabling response caching
3. **Monitor Connections**: Regularly check MCP server status
4. **Use Environment Variables**: Store sensitive data in environment variables
5. **Test Regularly**: Periodically test MCP tool access
6. **Document Changes**: Keep track of configuration changes

## Support

For issues or questions:
1. Check this configuration guide
2. Review troubleshooting section
3. Check Bob logs
4. Contact MCP server administrators
5. Consult watsonx Orchestrate documentation

## Additional Resources

- [watsonx Orchestrate Documentation](https://example.com/wxo-docs)
- [watsonx Orchestrate SDK](https://example.com/orchestrate-adk)
- [Bob Configuration Guide](https://example.com/bob-config)
- [MCP Protocol Documentation](https://example.com/mcp-protocol)