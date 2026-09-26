# MCP Server for watsonx Orchestrate

This project implements a Model Context Protocol (MCP) server with tools that can be integrated into watsonx Orchestrate.

## Project Structure

```
mcp-watsonx-project/
├── src/
│   └── mcp_server/
│       ├── __init__.py
│       ├── main.py
│       ├── tools.py
│       └── config.py
├── tests/
│   ├── __init__.py
│   ├── test_tools.py
│   └── test_server.py
├── docs/
│   ├── API.md
│   └── DEPLOYMENT.md
├── requirements.txt
├── setup.py
└── README.md
```

## Features

- Two custom MCP tools for watsonx Orchestrate integration
- Comprehensive unit tests
- Full documentation
- Easy deployment configuration

## Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

## Running the Server

```bash
python src/mcp_server/main.py
```

## Running Tests

```bash
pytest tests/ -v --cov=src/mcp_server
```

## Documentation

See the `docs/` directory for detailed documentation:
- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## License

MIT License