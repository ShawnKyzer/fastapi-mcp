# FastAPI MCP Server - AI Assistant Integration Guide

This guide provides step-by-step instructions for integrating the FastAPI MCP Server with popular AI coding assistants: **Kiro**, **Amazon Q**, and **Windsurf**.

## 📋 Prerequisites

Before setting up integrations, ensure you have:

1. **FastAPI MCP Server running** (see main README.md)
2. **Elasticsearch with data loaded** (5,437+ FastAPI documentation chunks)
3. **Python 3.11+** and **uv** installed
4. **MCP server accessible** via stdio transport

## 🚀 Quick Start

### 1. Start the Infrastructure
```bash
# Start Elasticsearch and Kibana
docker-compose up -d

# Load FastAPI documentation data
uv run python data_loader_cli.py

# Verify server works
uv run python main.py
```

### 2. Get Server Path
```bash
# Get absolute path to main.py
pwd
# Example output: /home/user/projects/fastapi-mcp/fastapi-mcp-server
```

---

## 🤖 Kiro AI Integration

### Configuration Steps

1. **Open Kiro AI Settings**
   - Navigate to Settings → Extensions → MCP Servers

2. **Add New MCP Server**
   ```json
   {
     "name": "FastAPI Documentation",
     "command": "uv",
     "args": ["run", "python", "main.py"],
     "cwd": "/path/to/fastapi-mcp-server",
     "env": {}
   }
   ```

3. **Alternative Configuration (Direct Python)**
   ```json
   {
     "name": "FastAPI Documentation", 
     "command": "python",
     "args": ["/path/to/fastapi-mcp-server/main.py"],
     "env": {
       "PYTHONPATH": "/path/to/fastapi-mcp-server"
     }
   }
   ```

### Usage in Kiro
- **Search docs**: "Search FastAPI documentation for dependency injection"
- **Get specific doc**: "Get FastAPI documentation for path parameters"
- **Browse tags**: "What FastAPI documentation tags are available?"

---

## 🔍 Amazon Q Integration

### VS Code Extension Setup

1. **Install Amazon Q Extension**
   - Open VS Code Extensions
   - Search for "Amazon Q"
   - Install and authenticate

2. **Configure MCP Server**
   
   **Option A: Via VS Code Settings**
   ```json
   {
     "amazonQ.mcp.servers": {
       "fastapi-docs": {
         "command": "uv",
         "args": ["run", "python", "main.py"],
         "cwd": "/path/to/fastapi-mcp-server"
       }
     }
   }
   ```

   **Option B: Via MCP Configuration File**
   Create `~/.config/amazon-q/mcp.json`:
   ```json
   {
     "servers": {
       "fastapi-docs": {
         "command": "uv",
         "args": ["run", "python", "main.py"],
         "cwd": "/path/to/fastapi-mcp-server",
         "description": "FastAPI documentation search and retrieval"
       }
     }
   }
   ```

### JetBrains IDE Setup

1. **Install Amazon Q Plugin**
   - Go to Settings → Plugins
   - Search for "Amazon Q"
   - Install and restart IDE

2. **Configure MCP Server**
   - Settings → Tools → Amazon Q → MCP Servers
   - Add new server with the configuration above

### Usage in Amazon Q
- **Chat integration**: "@fastapi-docs How do I create API endpoints?"
- **Code assistance**: "Show me FastAPI dependency injection examples"
- **Documentation lookup**: "Find FastAPI security documentation"

---

## 🌊 Windsurf Integration

### Configuration Steps

1. **Open Windsurf Settings**
   - Navigate to Settings → MCP Servers
   - Or edit configuration file directly

2. **Add MCP Server Configuration**
   
   **Via Settings UI:**
   - Server Name: `FastAPI Documentation`
   - Command: `uv`
   - Arguments: `["run", "python", "main.py"]`
   - Working Directory: `/path/to/fastapi-mcp-server`

   **Via Configuration File** (`~/.windsurf/mcp-servers.json`):
   ```json
   {
     "servers": {
       "fastapi-docs": {
         "command": "uv",
         "args": ["run", "python", "main.py"],
         "cwd": "/path/to/fastapi-mcp-server",
         "description": "FastAPI documentation server with 5400+ indexed docs"
       }
     }
   }
   ```

3. **Alternative: Direct Python Execution**
   ```json
   {
     "servers": {
       "fastapi-docs": {
         "command": "python3",
         "args": ["/path/to/fastapi-mcp-server/main.py"],
         "env": {
           "PYTHONPATH": "/path/to/fastapi-mcp-server"
         }
       }
     }
   }
   ```

### Usage in Windsurf
- **Contextual help**: Ask about FastAPI concepts while coding
- **Documentation search**: "Find FastAPI middleware documentation"
- **Code examples**: "Show me FastAPI WebSocket implementation"

---

## 🛠 Available MCP Tools

The FastAPI MCP Server provides these tools to all AI assistants:

### `search_fastapi_docs`
Search through FastAPI documentation with optional tag filtering.

**Parameters:**
- `query` (string): Search query
- `tags` (array, optional): Filter by tags (e.g., ["api", "pydantic"])
- `max_results` (number, optional): Maximum results (default: 10)

**Example:**
```json
{
  "query": "dependency injection",
  "tags": ["dependencies"],
  "max_results": 5
}
```

### `get_fastapi_doc_by_id`
Retrieve a specific documentation chunk by its ID.

**Parameters:**
- `doc_id` (string): Document ID from search results

### `refresh_fastapi_docs`
Refresh the documentation index with latest content from GitHub.

**Parameters:** None

### `get_available_tags`
Get all available tags for filtering documentation.

**Parameters:** None

---

## 🏷 Available Documentation Tags

The server automatically extracts and indexes these tag categories:

- **API Features**: `api`, `router`, `endpoint`, `path`
- **HTTP Methods**: `get`, `post`, `put`, `delete`, `patch`
- **Data Validation**: `pydantic`, `basemodel`, `validation`
- **Async/Await**: `async`, `await`
- **Dependencies**: `dependencies`, `dependency-injection`
- **Security**: `security`, `authentication`, `oauth2`
- **Database**: `database`, `sql`, `orm`
- **Testing**: `testing`, `pytest`
- **Deployment**: `deployment`, `docker`, `production`
- **Advanced**: `middleware`, `websockets`, `background-tasks`

---

## 🔧 Troubleshooting

### Common Issues

**1. Server Not Starting**
```bash
# Check if Elasticsearch is running
curl http://localhost:9200/_cluster/health

# Check if data is loaded
curl http://localhost:9200/fastapi_docs/_count
```

**2. Permission Issues**
```bash
# Make sure main.py is executable
chmod +x main.py

# Check Python path
which python3
```

**3. Port Conflicts**
```bash
# Check if ports are available
netstat -tulpn | grep :9200  # Elasticsearch
netstat -tulpn | grep :5601  # Kibana
```

**4. MCP Connection Issues**
- Verify the working directory path is correct
- Ensure `uv` is in your PATH
- Check that all dependencies are installed: `uv sync`

### Debugging Commands

```bash
# Test MCP server directly
echo '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' | uv run python main.py

# Check server logs
uv run python main.py 2>&1 | tee server.log

# Verify data loading
uv run python -c "
from src.search_engine import ElasticsearchEngine
import asyncio
async def test():
    engine = ElasticsearchEngine('http://localhost:9200', 'fastapi_docs')
    results = await engine.search_documents('FastAPI', max_results=1)
    print(f'Found {len(results)} results')
asyncio.run(test())
"
```

---

## 📊 Monitoring & Analytics

### Kibana Dashboard
Access comprehensive analytics at: http://localhost:5601

**Features:**
- Documentation tags distribution
- Section breakdown analysis  
- Content search and filtering
- Usage patterns and trends

### Health Checks
```bash
# Elasticsearch health
curl http://localhost:9200/_cluster/health

# Document count
curl http://localhost:9200/fastapi_docs/_count

# Sample search
curl -X GET "localhost:9200/fastapi_docs/_search?q=FastAPI&size=1"
```

---

## 🚀 Advanced Configuration

### Custom Environment Variables

Create `.env` file in the server directory:
```bash
ELASTICSEARCH_URL=http://localhost:9200
FASTAPI_REPO_URL=https://github.com/fastapi/fastapi.git
DOCS_INDEX_NAME=fastapi_docs
LOG_LEVEL=INFO
```

### Performance Tuning

**For High-Volume Usage:**
```json
{
  "command": "uv",
  "args": ["run", "python", "main.py"],
  "env": {
    "ELASTICSEARCH_TIMEOUT": "30",
    "MAX_SEARCH_RESULTS": "50",
    "CACHE_TTL": "3600"
  }
}
```

### Security Considerations

**Production Deployment:**
- Enable Elasticsearch authentication
- Use HTTPS for Elasticsearch connection
- Implement rate limiting
- Add request logging and monitoring

---

## 📚 Example Usage Scenarios

### 1. Learning FastAPI
**Query**: "How do I create my first FastAPI application?"
**Expected**: Step-by-step tutorial content with code examples

### 2. Debugging Issues  
**Query**: "FastAPI dependency injection not working"
**Expected**: Troubleshooting guides and common solutions

### 3. Advanced Features
**Query**: "FastAPI WebSocket implementation with authentication"
**Expected**: Advanced examples with security integration

### 4. Best Practices
**Query**: "FastAPI production deployment checklist"
**Expected**: Deployment guides and optimization tips

---

## 🤝 Support & Contributing

### Getting Help
- **Issues**: Report bugs or request features on GitHub
- **Documentation**: Check the main README.md for setup details
- **Community**: Join FastAPI Discord/forums for general questions

### Contributing
- Fork the repository
- Create feature branches
- Add tests for new functionality
- Submit pull requests with clear descriptions

---

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

---

**Happy coding with FastAPI! 🚀**
