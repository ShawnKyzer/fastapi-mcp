#!/bin/bash
cd /home/shawn/projects/fastapi-mcp/fastapi-mcp-server
exec uv run python main.py "$@"
