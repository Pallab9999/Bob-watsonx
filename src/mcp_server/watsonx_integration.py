"""
watsonx Orchestrate Integration Module

This module provides utilities for integrating MCP tools with watsonx Orchestrate.
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime


class WatsonxToolAdapter:
    """Adapter to convert MCP tools to watsonx Orchestrate format"""
    
    @staticmethod
    def convert_mcp_tool_to_watsonx(mcp_tool: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert an MCP tool definition to watsonx Orchestrate format
        
        Args:
            mcp_tool: MCP tool definition
            
        Returns:
            watsonx Orchestrate tool definition
        """
        return {
            "id": mcp_tool.get("name", "").replace("_", "-"),
            "name": mcp_tool.get("name", ""),
            "description": mcp_tool.get("description", ""),
            "type": "mcp",
            "schema": {
                "type": "object",
                "properties": mcp_tool.get("inputSchema", {}).get("properties", {}),
                "required": mcp_tool.get("inputSchema", {}).get("required", [])
            },
            "endpoint": "/tools/execute",
            "method": "POST",
            "metadata": {
                "source": "mcp-server",
                "version": "1.0.0",
                "created_at": datetime.utcnow().isoformat()
            }
        }
    
    @staticmethod
    def convert_mcp_tools_to_watsonx(mcp_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert multiple MCP tools to watsonx Orchestrate format
        
        Args:
            mcp_tools: List of MCP tool definitions
            
        Returns:
            List of watsonx Orchestrate tool definitions
        """
        return [WatsonxToolAdapter.convert_mcp_tool_to_watsonx(tool) for tool in mcp_tools]


class WatsonxToolRegistry:
    """Registry for managing watsonx Orchestrate tools"""
    
    def __init__(self):
        """Initialize the tool registry"""
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.metadata = {
            "registry_name": "MCP Server Tool Registry",
            "version": "1.0.0",
            "created_at": datetime.utcnow().isoformat(),
            "tools_count": 0
        }
    
    def register_tool(self, tool_id: str, tool_definition: Dict[str, Any]) -> bool:
        """
        Register a tool in the registry
        
        Args:
            tool_id: Unique tool identifier
            tool_definition: Tool definition
            
        Returns:
            True if registration was successful
        """
        try:
            self.tools[tool_id] = tool_definition
            self.metadata["tools_count"] = len(self.tools)
            self.metadata["last_updated"] = datetime.utcnow().isoformat()
            return True
        except Exception as e:
            print(f"Error registering tool {tool_id}: {str(e)}")
            return False
    
    def register_tools(self, tools: List[Dict[str, Any]]) -> int:
        """
        Register multiple tools
        
        Args:
            tools: List of tool definitions
            
        Returns:
            Number of successfully registered tools
        """
        count = 0
        for tool in tools:
            tool_id = tool.get("id", tool.get("name", ""))
            if self.register_tool(tool_id, tool):
                count += 1
        return count
    
    def get_tool(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get a tool by ID"""
        return self.tools.get(tool_id)
    
    def get_all_tools(self) -> List[Dict[str, Any]]:
        """Get all registered tools"""
        return list(self.tools.values())
    
    def remove_tool(self, tool_id: str) -> bool:
        """Remove a tool from the registry"""
        if tool_id in self.tools:
            del self.tools[tool_id]
            self.metadata["tools_count"] = len(self.tools)
            self.metadata["last_updated"] = datetime.utcnow().isoformat()
            return True
        return False
    
    def export_registry(self) -> Dict[str, Any]:
        """Export the registry as a dictionary"""
        return {
            "metadata": self.metadata,
            "tools": self.tools
        }
    
    def export_to_json(self, filepath: str) -> bool:
        """Export the registry to a JSON file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.export_registry(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting registry to {filepath}: {str(e)}")
            return False
    
    def import_from_json(self, filepath: str) -> bool:
        """Import registry from a JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.metadata = data.get("metadata", self.metadata)
            tools = data.get("tools", {})
            
            for tool_id, tool_def in tools.items():
                self.register_tool(tool_id, tool_def)
            
            return True
        except Exception as e:
            print(f"Error importing registry from {filepath}: {str(e)}")
            return False


class WatsonxToolManifest:
    """Generate watsonx Orchestrate tool manifest"""
    
    @staticmethod
    def generate_manifest(
        tools: List[Dict[str, Any]],
        server_url: str = "http://localhost:8000",
        version: str = "1.0.0"
    ) -> Dict[str, Any]:
        """
        Generate a tool manifest for watsonx Orchestrate
        
        Args:
            tools: List of tool definitions
            server_url: MCP server URL
            version: Manifest version
            
        Returns:
            Tool manifest
        """
        return {
            "manifest_version": "1.0.0",
            "server_info": {
                "name": "MCP Server for watsonx Orchestrate",
                "url": server_url,
                "version": version,
                "type": "mcp"
            },
            "tools": tools,
            "metadata": {
                "created_at": datetime.utcnow().isoformat(),
                "tool_count": len(tools),
                "capabilities": {
                    "async_execution": True,
                    "error_handling": True,
                    "logging": True
                }
            }
        }
    
    @staticmethod
    def save_manifest(manifest: Dict[str, Any], filepath: str) -> bool:
        """Save manifest to file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(manifest, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving manifest to {filepath}: {str(e)}")
            return False
    
    @staticmethod
    def load_manifest(filepath: str) -> Optional[Dict[str, Any]]:
        """Load manifest from file"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading manifest from {filepath}: {str(e)}")
            return None


class WatsonxIntegrationConfig:
    """Configuration for watsonx Orchestrate integration"""
    
    def __init__(
        self,
        server_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        project_id: Optional[str] = None,
        environment: str = "development"
    ):
        """
        Initialize integration configuration
        
        Args:
            server_url: MCP server URL
            api_key: watsonx API key
            project_id: watsonx project ID
            environment: Deployment environment
        """
        self.server_url = server_url
        self.api_key = api_key
        self.project_id = project_id
        self.environment = environment
        self.created_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "server_url": self.server_url,
            "api_key": "***" if self.api_key else None,
            "project_id": self.project_id,
            "environment": self.environment,
            "created_at": self.created_at
        }
    
    def to_json(self) -> str:
        """Convert configuration to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    def save_to_file(self, filepath: str) -> bool:
        """Save configuration to file"""
        try:
            config_data = {
                "server_url": self.server_url,
                "api_key": self.api_key,
                "project_id": self.project_id,
                "environment": self.environment
            }
            with open(filepath, 'w') as f:
                json.dump(config_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving configuration to {filepath}: {str(e)}")
            return False
    
    @staticmethod
    def load_from_file(filepath: str) -> Optional['WatsonxIntegrationConfig']:
        """Load configuration from file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            return WatsonxIntegrationConfig(
                server_url=data.get("server_url", "http://localhost:8000"),
                api_key=data.get("api_key"),
                project_id=data.get("project_id"),
                environment=data.get("environment", "development")
            )
        except Exception as e:
            print(f"Error loading configuration from {filepath}: {str(e)}")
            return None


def create_tool_import_package(
    mcp_tools: List[Dict[str, Any]],
    output_dir: str = "watsonx_tools"
) -> bool:
    """
    Create a complete tool import package for watsonx Orchestrate
    
    Args:
        mcp_tools: List of MCP tools
        output_dir: Output directory for the package
        
    Returns:
        True if package was created successfully
    """
    import os
    
    try:
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert tools to watsonx format
        adapter = WatsonxToolAdapter()
        watsonx_tools = adapter.convert_mcp_tools_to_watsonx(mcp_tools)
        
        # Create registry
        registry = WatsonxToolRegistry()
        registry.register_tools(watsonx_tools)
        
        # Generate manifest
        manifest = WatsonxToolManifest.generate_manifest(watsonx_tools)
        
        # Save files
        registry.export_to_json(os.path.join(output_dir, "registry.json"))
        WatsonxToolManifest.save_manifest(manifest, os.path.join(output_dir, "manifest.json"))
        
        # Create README
        readme_content = f"""# watsonx Orchestrate Tool Package

Generated from MCP Server

## Contents

- `manifest.json`: Tool manifest for watsonx Orchestrate
- `registry.json`: Tool registry with all tool definitions

## Tools Included

{chr(10).join([f"- {tool['name']}: {tool['description']}" for tool in watsonx_tools])}

## Installation

1. Import the tools from `manifest.json` into watsonx Orchestrate
2. Configure the MCP server URL in your watsonx environment
3. Test the tools using the watsonx Orchestrate UI

## Support

For issues or questions, refer to the main project documentation.
"""
        
        with open(os.path.join(output_dir, "README.md"), 'w') as f:
            f.write(readme_content)
        
        return True
        
    except Exception as e:
        print(f"Error creating tool import package: {str(e)}")
        return False

# Made with Bob
