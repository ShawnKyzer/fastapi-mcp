"""
FastAPI MCP Server implementation following SOLID principles.
"""

import logging
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

from .interfaces import IDataLoader, ISearchEngine

logger = logging.getLogger(__name__)


class FastAPIMCPServer:
    """MCP Server for FastAPI documentation."""
    
    def __init__(self, data_loader: IDataLoader, search_engine: ISearchEngine):
        self.data_loader = data_loader
        self.search_engine = search_engine
        self.mcp = FastMCP(
            name="FastAPI Documentation Server",
            instructions="""
            This server provides access to the latest FastAPI documentation indexed in Elasticsearch.
            Use the available tools to search for FastAPI-related information, get specific documentation
            sections, and refresh the documentation index when needed.
            
            Available capabilities:
            - Search FastAPI documentation with semantic search
            - Get specific documentation sections by ID
            - Refresh documentation from the latest GitHub repository
            - Filter searches by tags (api, pydantic, async, dependencies, security, etc.)
            """
        )
        self._register_tools()
    
    def _register_tools(self):
        """Register MCP tools."""
        
        @self.mcp.tool
        async def search_fastapi_docs(
            query: str,
            tags: Optional[List[str]] = None,
            max_results: int = 10
        ) -> Dict[str, Any]:
            """
            Search FastAPI documentation using semantic search.
            
            Args:
                query: Search query (e.g., "how to create API endpoints", "pydantic models", "async dependencies")
                tags: Optional list of tags to filter by (api, pydantic, async, dependencies, security, database, testing, deployment)
                max_results: Maximum number of results to return (default: 10)
            
            Returns:
                Dictionary containing search results with highlighted content
            """
            try:
                results = await self.search_engine.search_documents(query, tags, max_results)
                
                formatted_results = []
                for hit in results:
                    source = hit["_source"]
                    highlight = hit.get("highlight", {})
                    
                    result = {
                        "id": source["id"],
                        "title": source["title"],
                        "section": source["section"],
                        "subsection": source.get("subsection"),
                        "url": source["url"],
                        "tags": source["tags"],
                        "score": hit["_score"],
                        "content": source["content"][:500] + "..." if len(source["content"]) > 500 else source["content"]
                    }
                    
                    if highlight:
                        result["highlights"] = highlight
                    
                    formatted_results.append(result)
                
                return {
                    "query": query,
                    "total_results": len(formatted_results),
                    "results": formatted_results
                }
            except Exception as e:
                logger.error(f"Search failed: {e}")
                return {"error": f"Search failed: {str(e)}"}

        @self.mcp.tool
        async def get_fastapi_doc_by_id(doc_id: str) -> Dict[str, Any]:
            """
            Get a specific FastAPI documentation section by its ID.
            
            Args:
                doc_id: The document ID from search results
            
            Returns:
                Complete document content
            """
            try:
                doc = await self.search_engine.get_document_by_id(doc_id)
                if doc:
                    return doc
                else:
                    return {"error": f"Document with ID '{doc_id}' not found"}
            except Exception as e:
                logger.error(f"Failed to get document: {e}")
                return {"error": f"Failed to get document: {str(e)}"}

        @self.mcp.tool
        async def refresh_fastapi_docs() -> Dict[str, Any]:
            """
            Refresh the FastAPI documentation by fetching the latest version from GitHub
            and re-indexing it in Elasticsearch.
            
            Returns:
                Status of the refresh operation
            """
            return await self.data_loader.refresh_data()

        @self.mcp.tool
        async def get_available_tags() -> Dict[str, Any]:
            """
            Get all available tags that can be used for filtering searches.
            
            Returns:
                List of available tags with descriptions
            """
            return {
                "tags": {
                    "api": "API endpoints and routing",
                    "http-methods": "HTTP methods (GET, POST, PUT, DELETE, etc.)",
                    "pydantic": "Pydantic models and validation",
                    "async": "Asynchronous programming",
                    "dependencies": "Dependency injection",
                    "security": "Authentication and authorization",
                    "database": "Database integration",
                    "testing": "Testing FastAPI applications",
                    "deployment": "Deployment and Docker",
                    "validation": "Data validation and schemas",
                    "middleware": "Middleware components",
                    "cors": "Cross-Origin Resource Sharing",
                    "websocket": "WebSocket connections",
                    "background-tasks": "Background task processing",
                    "file-upload": "File upload handling"
                }
            }
    
    def run(self):
        """Run the MCP server."""
        self.mcp.run()
    
    async def close(self):
        """Close server resources."""
        await self.search_engine.close()
