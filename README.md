# FastAPI MCP Server

A Model Context Protocol (MCP) server that provides semantic search capabilities for FastAPI documentation. It fetches the latest FastAPI documentation from GitHub, indexes it in Elasticsearch, and exposes search tools for AI coding assistants.

## Features

- **Automatic Documentation Fetching**: Clones/updates the latest FastAPI documentation from the official GitHub repository
- **Elasticsearch Integration**: Indexes documentation with semantic search capabilities
- **Smart Content Processing**: Extracts and chunks documentation with proper tagging
- **MCP Compatible**: Works with Windsurf, Claude Desktop, and other MCP-compatible AI assistants
- **Tag-based Filtering**: Search by specific topics (API, Pydantic, async, dependencies, security, etc.)
- **Real-time Updates**: Refresh documentation on demand

## Prerequisites

### All Platforms
- Python 3.11+
- Docker and Docker Compose (for Elasticsearch)
- uv (Python package manager)

### Windows 11 Specific
- PowerShell 5.1+ or PowerShell Core 7+
- Windows Terminal (recommended)
- Docker Desktop for Windows

## Quick Start

### 1. Start Elasticsearch

**Linux/macOS:**
```bash
docker-compose up -d
```

**Windows (PowerShell):**
```powershell
docker-compose up -d
```

Wait for Elasticsearch to be healthy:
```bash
docker-compose ps
```

### 2. Install Dependencies

**All Platforms:**
```bash
uv sync
```

### 3. Run the MCP Server

**Linux/macOS:**
```bash
# Using the wrapper script (recommended for MCP clients)
./run_mcp.sh

# Or directly
uv run python main.py
```

**Windows:**
```powershell
# Using PowerShell wrapper (recommended for MCP clients)
.\run_mcp.ps1

# Using batch file
.\run_mcp.bat

# Or directly
uv run python main.py
```

The server will automatically:
- Connect to Elasticsearch
- Check if documentation index exists
- Clone FastAPI repository and index documentation if needed
- Start the MCP server on stdio transport

## Available Tools

### `search_fastapi_docs`
Search FastAPI documentation with semantic search.

**Parameters:**
- `query` (str): Search query (e.g., "how to create API endpoints")
- `tags` (List[str], optional): Filter by tags
- `max_results` (int): Maximum results to return (default: 10)

**Example:**
```json
{
  "query": "pydantic models validation",
  "tags": ["pydantic", "api"],
  "max_results": 5
}
```

### `get_fastapi_doc_by_id`
Get a specific documentation section by ID.

**Parameters:**
- `doc_id` (str): Document ID from search results

### `refresh_fastapi_docs`
Refresh documentation by fetching the latest version from GitHub.

**Returns:** Status of the refresh operation

### `get_available_tags`
Get all available tags for filtering searches.

**Available Tags:**
- `api`: API endpoints and routing
- `http-methods`: HTTP methods (GET, POST, PUT, DELETE, etc.)
- `pydantic`: Pydantic models and validation
- `async`: Asynchronous programming
- `dependencies`: Dependency injection
- `security`: Authentication and authorization
- `database`: Database integration
- `testing`: Testing FastAPI applications
- `deployment`: Deployment and Docker

## Integration with AI Assistants

### Windsurf

**Linux/macOS** - Add to your Windsurf MCP configuration (`~/.codeium/windsurf/mcp_config.json`):
```json
{
  "fastapi-docs": {
    "command": "/path/to/fastapi-mcp/run_mcp.sh",
    "args": []
  }
}
```

**Windows** - Add to your Windsurf MCP configuration (`%USERPROFILE%\.codeium\windsurf\mcp_config.json`):
```json
{
  "fastapi-docs": {
    "command": "powershell.exe",
    "args": ["-ExecutionPolicy", "Bypass", "-File", "C:\\path\\to\\fastapi-mcp\\run_mcp.ps1"]
  }
}
```

### Claude Desktop

**Linux/macOS** - Add to your Claude Desktop configuration:
```json
{
  "mcpServers": {
    "fastapi-docs": {
      "command": "/path/to/fastapi-mcp/run_mcp.sh",
      "args": []
    }
  }
}
```

**Windows** - Add to your Claude Desktop configuration (`%APPDATA%\Claude\claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "fastapi-docs": {
      "command": "powershell.exe",
      "args": ["-ExecutionPolicy", "Bypass", "-File", "C:\\path\\to\\fastapi-mcp\\run_mcp.ps1"]
    }
  }
}
```

**Note**: Replace the paths with the actual absolute path to your installation directory.

## Development

### Project Structure
```
fastapi-mcp/
├── src/                     # Source code modules
│   ├── config.py           # Configuration settings
│   ├── mcp_server.py       # Main MCP server implementation
│   ├── search_engine.py    # Elasticsearch integration
│   ├── document_fetcher.py # GitHub repository fetching
│   ├── document_processor.py # Documentation processing
│   └── data_loader.py      # Data loading and indexing
├── tests/                  # Test suite
├── scripts/                # Utility scripts
│   ├── data_loader_cli.py  # CLI for data loading
│   └── setup_kibana_dashboard.py # Kibana dashboard setup
├── dashboards/             # Kibana dashboards
│   └── kibana-dashboard.ndjson
├── docs/                   # Additional documentation
│   └── AI_ASSISTANT_INTEGRATION.md
├── main.py                 # Entry point
├── run_mcp.sh             # MCP wrapper script (Linux/macOS)
├── run_mcp.ps1            # MCP wrapper script (Windows PowerShell)
├── run_mcp.bat            # MCP wrapper script (Windows Batch)
├── docker-compose.yml     # Elasticsearch setup
├── pyproject.toml         # Dependencies and project config
└── README.md              # This file
```

### Testing the Server

**1. Start Elasticsearch:**

Linux/macOS:
```bash
docker-compose up -d
```

Windows (PowerShell):
```powershell
docker-compose up -d
```

**2. Run the server directly:**

Linux/macOS:
```bash
uv run python main.py
```

Windows (PowerShell):
```powershell
uv run python main.py
```

**3. Test with MCP client tools** (available when connected to an AI assistant):
- `search_fastapi_docs`: Search documentation
- `get_fastapi_doc_by_id`: Get specific document
- `refresh_fastapi_docs`: Update documentation
- `get_available_tags`: List available tags

### Customization

Edit `src/config.py` to customize:
- **Elasticsearch URL**: Change `ELASTICSEARCH_URL` (default: `http://localhost:9200`)
- **Index Name**: Modify `INDEX_NAME` (default: `fastapi_docs`)
- **Repository Path**: Adjust `TEMP_REPO_PATH` (default: `/tmp/fastapi_repo`)
- **FastAPI Repository**: Change `FASTAPI_REPO_URL` if using a fork

## Additional Tools

### CLI Data Loader
Use the CLI tool to manually load or refresh documentation:

Linux/macOS:
```bash
uv run python scripts/data_loader_cli.py
```

Windows (PowerShell):
```powershell
uv run python scripts/data_loader_cli.py
```

### Kibana Dashboard
Set up Kibana for monitoring and visualization:

Linux/macOS:
```bash
uv run python scripts/setup_kibana_dashboard.py
```

Windows (PowerShell):
```powershell
uv run python scripts/setup_kibana_dashboard.py
```

## Troubleshooting

### Elasticsearch Connection Issues
- Ensure Docker is running: `docker ps`
- Check Elasticsearch health: `curl http://localhost:9200/_cluster/health`
- View logs: `docker-compose logs elasticsearch`

### Repository Clone Issues
- Check internet connectivity
- Verify GitHub access
- Clear temp directory: `rm -rf /tmp/fastapi_repo`

### Memory Issues
- Increase Elasticsearch heap size in `docker-compose.yml`
- Reduce `max_results` in search queries

### MCP Configuration Issues

**Linux/macOS:**
- Ensure the wrapper script has execute permissions: `chmod +x run_mcp.sh`
- Use absolute paths in MCP configuration
- Check that Elasticsearch is running before starting the MCP server

**Windows:**
- Ensure PowerShell execution policy allows script execution: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Use absolute paths with proper Windows path format (e.g., `C:\path\to\file`)
- For PowerShell scripts in MCP config, use `powershell.exe` with `-ExecutionPolicy Bypass` flag
- Check that Docker Desktop is running before starting the MCP server

## License

This project is open source and available under the MIT License.