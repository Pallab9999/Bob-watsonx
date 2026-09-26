"""
MCP Server for watsonx Orchestrate Integration
"""

__version__ = "1.0.0"
__author__ = "IBM Bob"

from .main import app, main
from .tools import get_weather_tool, calculate_statistics_tool

__all__ = [
    "app",
    "main",
    "get_weather_tool",
    "calculate_statistics_tool",
]

# Made with Bob
