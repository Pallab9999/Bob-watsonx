# MCP Server Deployment Script (PowerShell)
# This script sets up and deploys the MCP Server for watsonx Orchestrate

param(
    [Parameter(Position=0)]
    [ValidateSet("setup", "test", "start", "validate", "full")]
    [string]$Command = "start",
    
    [string]$Host = "0.0.0.0",
    [int]$Port = 8000
)

# Configuration
$VENV_DIR = "venv"
$PYTHON_CMD = "python"

# Functions
function Print-Status {
    param([string]$Message)
    Write-Host "[✓] $Message" -ForegroundColor Green
}

function Print-Error {
    param([string]$Message)
    Write-Host "[✗] $Message" -ForegroundColor Red
}

function Print-Info {
    param([string]$Message)
    Write-Host "[i] $Message" -ForegroundColor Yellow
}

function Check-Python {
    Print-Info "Checking Python installation..."
    
    try {
        $version = & $PYTHON_CMD --version 2>&1
        Print-Status "Python found: $version"
        return $true
    }
    catch {
        Print-Error "Python is not installed or not in PATH"
        return $false
    }
}

function Create-VirtualEnvironment {
    Print-Info "Creating virtual environment..."
    
    if (Test-Path $VENV_DIR) {
        Print-Info "Virtual environment already exists"
    }
    else {
        & $PYTHON_CMD -m venv $VENV_DIR
        Print-Status "Virtual environment created"
    }
}

function Activate-VirtualEnvironment {
    Print-Info "Activating virtual environment..."
    
    $activateScript = Join-Path $VENV_DIR "Scripts" "Activate.ps1"
    
    if (Test-Path $activateScript) {
        & $activateScript
        Print-Status "Virtual environment activated"
    }
    else {
        Print-Error "Could not find activation script"
        return $false
    }
    
    return $true
}

function Install-Dependencies {
    Print-Info "Installing dependencies..."
    
    & $PYTHON_CMD -m pip install --upgrade pip setuptools wheel
    & $PYTHON_CMD -m pip install -r requirements.txt
    
    Print-Status "Dependencies installed"
}

function Run-Tests {
    Print-Info "Running unit tests..."
    
    & $PYTHON_CMD -m pytest tests/ -v --tb=short
    
    if ($LASTEXITCODE -eq 0) {
        Print-Status "All tests passed"
        return $true
    }
    else {
        Print-Error "Some tests failed"
        return $false
    }
}

function Start-Server {
    Print-Info "Starting MCP Server..."
    Print-Info "Server will run on http://$Host`:$Port"
    
    $env:MCP_HOST = $Host
    $env:MCP_PORT = $Port
    
    & $PYTHON_CMD src/mcp_server/main.py
}

function Validate-Server {
    Print-Info "Validating server..."
    
    Start-Sleep -Seconds 2
    
    & $PYTHON_CMD src/mcp_server/client.py "http://localhost:$Port"
    
    if ($LASTEXITCODE -eq 0) {
        Print-Status "Server validation successful"
        return $true
    }
    else {
        Print-Error "Server validation failed"
        return $false
    }
}

function Show-Help {
    Write-Host "Usage: .\deploy.ps1 [Command] [Options]"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  setup    - Set up the project (create venv, install dependencies)"
    Write-Host "  test     - Run unit tests"
    Write-Host "  start    - Start the MCP server (default)"
    Write-Host "  validate - Validate the running server"
    Write-Host "  full     - Run full deployment (setup, test, start)"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Host <string>  - Server host (default: 0.0.0.0)"
    Write-Host "  -Port <int>     - Server port (default: 8000)"
}

# Main execution
function Main {
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "MCP Server Deployment Script" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    
    switch ($Command) {
        "setup" {
            if (-not (Check-Python)) { exit 1 }
            Create-VirtualEnvironment
            if (-not (Activate-VirtualEnvironment)) { exit 1 }
            Install-Dependencies
            Print-Status "Setup completed successfully"
        }
        
        "test" {
            if (-not (Activate-VirtualEnvironment)) { exit 1 }
            if (-not (Run-Tests)) { exit 1 }
        }
        
        "start" {
            if (-not (Activate-VirtualEnvironment)) { exit 1 }
            Start-Server
        }
        
        "validate" {
            if (-not (Validate-Server)) { exit 1 }
        }
        
        "full" {
            if (-not (Check-Python)) { exit 1 }
            Create-VirtualEnvironment
            if (-not (Activate-VirtualEnvironment)) { exit 1 }
            Install-Dependencies
            if (-not (Run-Tests)) { exit 1 }
            Start-Server
        }
        
        default {
            Show-Help
            exit 1
        }
    }
}

Main

# Made with Bob
