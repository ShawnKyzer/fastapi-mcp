# FastAPI MCP Server

A Model Context Protocol (MCP) server that fetches the latest FastAPI documentation from GitHub and indexes it in Elasticsearch for AI coding assistants like Amazon Q, Windsurf, and Kiro.

## Features

- **Automatic Documentation Fetching**: Clones/updates the latest FastAPI documentation from the official GitHub repository
- **Elasticsearch Integration**: Indexes documentation with semantic search capabilities
- **Smart Content Processing**: Extracts and chunks documentation with proper tagging
- **MCP Compatible**: Works with Amazon Q, Windsurf, Kiro, and other MCP-compatible AI assistants
- **Tag-based Filtering**: Search by specific topics (API, Pydantic, async, dependencies, security, etc.)

## Prerequisites

- Python 3.11+
- Docker and Docker Compose
- uv (Python package manager)

## Quick Start

### 1. Start Elasticsearch

```bash
docker-compose up -d
```

Wait for Elasticsearch to be healthy:
```bash
docker-compose ps
```

### 2. Install Dependencies

```bash
uv sync
```

### 3. Run the MCP Server

```bash
uv run python fastapi_mcp_server.py
```

The server will automatically:
- Clone the FastAPI repository
- Extract and process documentation
- Create and populate the Elasticsearch index
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

### Amazon Q
Add the server to your Amazon Q configuration:
```json
{
  "mcpServers": {
    "fastapi-docs": {
      "command": "uv",
      "args": ["run", "python", "/path/to/fastapi_mcp_server.py"]
    }
  }
}
```

### Windsurf
Add to your Windsurf MCP configuration:
```json
{
  "fastapi-docs": {
    "command": "uv",
    "args": ["run", "python", "/path/to/fastapi_mcp_server.py"],
    "cwd": "/path/to/fastapi-mcp-server"
  }
}
```

### Kiro
Configure in Kiro settings:
```json
{
  "mcp_servers": {
    "fastapi-docs": {
      "command": ["uv", "run", "python", "/path/to/fastapi_mcp_server.py"],
      "cwd": "/path/to/fastapi-mcp-server"
    }
  }
}
```

## Development

### Project Structure
```
fastapi-mcp-server/
├── fastapi_mcp_server.py    # Main MCP server
├── docker-compose.yml       # Elasticsearch setup
├── pyproject.toml          # Dependencies
└── README.md               # This file
```

### Testing the Server

1. Start Elasticsearch:
   ```bash
   docker-compose up -d
   ```

2. Run the server:
   ```bash
   uv run python fastapi_mcp_server.py
   ```

3. Test with FastMCP client:
   ```python
   import asyncio
   from fastmcp import Client
   
   async def test_search():
       client = Client("fastapi_mcp_server.py")
       async with client:
           result = await client.call_tool("search_fastapi_docs", {
               "query": "create API endpoint",
               "max_results": 3
           })
           print(result)
   
   asyncio.run(test_search())
   ```

### Customization

- **Elasticsearch URL**: Modify `ELASTICSEARCH_URL` in the server code
- **Index Name**: Change `INDEX_NAME` for different index names
- **Repository Path**: Adjust `TEMP_REPO_PATH` for different clone locations

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

## License

This project is open source and available under the MIT License.