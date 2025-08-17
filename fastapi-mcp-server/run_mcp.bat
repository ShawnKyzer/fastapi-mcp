@echo off
REM Batch file wrapper for FastAPI MCP Server
REM This script sets the working directory and runs the MCP server using uv

REM Change to the directory where this batch file is located
cd /d "%~dp0"

REM Run the MCP server with uv
uv run python main.py %*
