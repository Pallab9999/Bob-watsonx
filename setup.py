from setuptools import setup, find_packages

setup(
    name="mcp-watsonx-server",
    version="1.0.0",
    description="MCP Server for watsonx Orchestrate Integration",
    author="IBM Bob",
    author_email="bob@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "mcp>=1.0.0",
        "pydantic>=2.0.0",
        "httpx>=0.24.0",
        "uvicorn>=0.23.0",
        "fastapi>=0.100.0",
        "ibm-watsonx-orchestrate>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mcp-watsonx-server=mcp_server.main:main",
        ],
    },
)

# Made with Bob
