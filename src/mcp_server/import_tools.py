"""
Script to import MCP tools into watsonx Orchestrate
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

from .tools import get_all_tools
from .watsonx_integration import (
    WatsonxToolAdapter,
    WatsonxToolRegistry,
    WatsonxToolManifest,
    WatsonxIntegrationConfig,
    create_tool_import_package
)


async def import_tools_to_watsonx(
    output_dir: str = "watsonx_tools",
    server_url: str = "http://localhost:8000",
    config_file: Optional[str] = None
) -> bool:
    """
    Import MCP tools to watsonx Orchestrate format
    
    Args:
        output_dir: Output directory for tool package
        server_url: MCP server URL
        config_file: Optional configuration file path
        
    Returns:
        True if import was successful
    """
    try:
        print("=" * 60)
        print("MCP Tools Import to watsonx Orchestrate")
        print("=" * 60)
        
        # Get MCP tools
        print("\n[1/5] Retrieving MCP tools...")
        mcp_tools = get_all_tools()
        print(f"✓ Found {len(mcp_tools)} tools")
        
        for tool in mcp_tools:
            print(f"  - {tool['name']}: {tool['description'][:50]}...")
        
        # Convert to watsonx format
        print("\n[2/5] Converting tools to watsonx Orchestrate format...")
        adapter = WatsonxToolAdapter()
        watsonx_tools = adapter.convert_mcp_tools_to_watsonx(mcp_tools)
        print(f"✓ Converted {len(watsonx_tools)} tools")
        
        # Create registry
        print("\n[3/5] Creating tool registry...")
        registry = WatsonxToolRegistry()
        registered_count = registry.register_tools(watsonx_tools)
        print(f"✓ Registered {registered_count} tools")
        
        # Generate manifest
        print("\n[4/5] Generating watsonx Orchestrate manifest...")
        manifest = WatsonxToolManifest.generate_manifest(watsonx_tools, server_url)
        print("✓ Manifest generated")
        
        # Create import package
        print("\n[5/5] Creating tool import package...")
        success = create_tool_import_package(watsonx_tools, output_dir)
        
        if success:
            print(f"✓ Tool package created in '{output_dir}' directory")
            
            # Print summary
            print("\n" + "=" * 60)
            print("Import Summary")
            print("=" * 60)
            print(f"Output Directory: {output_dir}")
            print(f"Tools Imported: {len(watsonx_tools)}")
            print(f"Server URL: {server_url}")
            print("\nGenerated Files:")
            print(f"  - {output_dir}/manifest.json")
            print(f"  - {output_dir}/registry.json")
            print(f"  - {output_dir}/README.md")
            print("\nNext Steps:")
            print("1. Review the generated files in the output directory")
            print("2. Import manifest.json into watsonx Orchestrate")
            print("3. Configure the MCP server URL in watsonx")
            print("4. Test the tools in watsonx Orchestrate")
            print("=" * 60)
            
            return True
        else:
            print("✗ Failed to create tool import package")
            return False
            
    except Exception as e:
        print(f"✗ Error during import: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def print_tool_details(tools: list) -> None:
    """Print detailed information about tools"""
    print("\n" + "=" * 60)
    print("Tool Details")
    print("=" * 60)
    
    for i, tool in enumerate(tools, 1):
        print(f"\n[Tool {i}] {tool['name']}")
        print(f"Description: {tool['description']}")
        print(f"ID: {tool['id']}")
        print(f"Type: {tool['type']}")
        print(f"Endpoint: {tool['endpoint']}")
        print(f"Method: {tool['method']}")
        
        if 'schema' in tool:
            schema = tool['schema']
            print(f"Input Schema:")
            print(f"  Type: {schema.get('type')}")
            print(f"  Properties: {list(schema.get('properties', {}).keys())}")
            print(f"  Required: {schema.get('required', [])}")


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Import MCP tools to watsonx Orchestrate"
    )
    parser.add_argument(
        "--output-dir",
        default="watsonx_tools",
        help="Output directory for tool package (default: watsonx_tools)"
    )
    parser.add_argument(
        "--server-url",
        default="http://localhost:8000",
        help="MCP server URL (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--config",
        help="Configuration file path"
    )
    parser.add_argument(
        "--details",
        action="store_true",
        help="Print detailed tool information"
    )
    
    args = parser.parse_args()
    
    # Get tools
    mcp_tools = get_all_tools()
    
    if args.details:
        adapter = WatsonxToolAdapter()
        watsonx_tools = adapter.convert_mcp_tools_to_watsonx(mcp_tools)
        print_tool_details(watsonx_tools)
        return
    
    # Import tools
    success = await import_tools_to_watsonx(
        output_dir=args.output_dir,
        server_url=args.server_url,
        config_file=args.config
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob
