"""
Configuration settings for the MCP server
"""

import os
from typing import Optional
from pydantic import BaseModel


class ServerConfig(BaseModel):
    """Server configuration settings"""
    
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    log_level: str = "INFO"
    
    # API Keys and credentials
    weather_api_key: Optional[str] = None
    watsonx_api_key: Optional[str] = None
    watsonx_project_id: Optional[str] = None
    
    class Config:
        env_prefix = "MCP_"


def load_config() -> ServerConfig:
    """Load configuration from environment variables"""
    return ServerConfig(
        host=os.getenv("MCP_HOST", "0.0.0.0"),
        port=int(os.getenv("MCP_PORT", "8000")),
        debug=os.getenv("MCP_DEBUG", "false").lower() == "true",
        log_level=os.getenv("MCP_LOG_LEVEL", "INFO"),
        weather_api_key=os.getenv("WEATHER_API_KEY"),
        watsonx_api_key=os.getenv("WATSONX_API_KEY"),
        watsonx_project_id=os.getenv("WATSONX_PROJECT_ID"),
    )


# Global config instance
config = load_config()

# Made with Bob
