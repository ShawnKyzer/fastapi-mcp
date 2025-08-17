#!/bin/bash
cd /home/shawn/projects/fastapi-mcp
exec uv run python main.py "$@"
