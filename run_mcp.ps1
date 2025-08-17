# PowerShell wrapper script for FastAPI MCP Server
# This script sets the working directory and runs the MCP server using uv

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Change to the script directory
Set-Location $ScriptDir

# Run the MCP server with uv
& uv run python main.py @args
