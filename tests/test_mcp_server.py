"""
Tests for MCP server.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.mcp_server import FastAPIMCPServer


@pytest.mark.asyncio
class TestFastAPIMCPServer:
    """Test cases for FastAPIMCPServer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_data_loader = AsyncMock()
        self.mock_search_engine = AsyncMock()
        self.mcp_server = FastAPIMCPServer(self.mock_data_loader, self.mock_search_engine)
    
    def test_server_initialization(self):
        """Test server initialization."""
        assert self.mcp_server.data_loader == self.mock_data_loader
        assert self.mcp_server.search_engine == self.mock_search_engine
        assert self.mcp_server.mcp is not None
        assert self.mcp_server.mcp.name == "FastAPI Documentation Server"
    
    async def test_search_fastapi_docs_success(self):
        """Test successful search operation."""
        # Mock search results
        mock_results = [
            {
                "_source": {
                    "id": "test-1",
                    "title": "Test Doc",
                    "section": "Test Section",
                    "subsection": "Test Subsection",
                    "url": "https://test.com",
                    "tags": ["test"],
                    "content": "Test content"
                },
                "_score": 1.0,
                "highlight": {"content": ["Test <em>content</em>"]}
            }
        ]
        self.mock_search_engine.search_documents.return_value = mock_results
        
        # Get the tool function
        tools = await self.mcp_server.mcp.get_tools()
        search_tool = None
        for tool in tools.values():
            if tool.name == "search_fastapi_docs":
                search_tool = tool
                break
        
        assert search_tool is not None
        
        # Call the tool function directly
        result = await search_tool.fn("test query", None, 10)
        
        assert result["query"] == "test query"
        assert result["total_results"] == 1
        assert len(result["results"]) == 1
        assert result["results"][0]["id"] == "test-1"
        
        self.mock_search_engine.search_documents.assert_called_once_with("test query", None, 10)
    
    async def test_search_fastapi_docs_with_tags(self):
        """Test search with tag filtering."""
        self.mock_search_engine.search_documents.return_value = []
        
        tools = await self.mcp_server.mcp.get_tools()
        search_tool = None
        for tool in tools.values():
            if tool.name == "search_fastapi_docs":
                search_tool = tool
                break
        
        result = await search_tool.fn("test query", ["api", "pydantic"], 5)
        
        self.mock_search_engine.search_documents.assert_called_once_with("test query", ["api", "pydantic"], 5)
    
    async def test_search_fastapi_docs_error(self):
        """Test search operation with error."""
        self.mock_search_engine.search_documents.side_effect = Exception("Search error")
        
        tools = await self.mcp_server.mcp.get_tools()
        search_tool = None
        for tool in tools.values():
            if tool.name == "search_fastapi_docs":
                search_tool = tool
                break
        
        result = await search_tool.fn("test query")
        
        assert "error" in result
        assert "Search failed: Search error" in result["error"]
    
    async def test_get_fastapi_doc_by_id_success(self):
        """Test successful document retrieval by ID."""
        mock_doc = {"id": "test-1", "title": "Test Doc", "content": "Test content"}
        self.mock_search_engine.get_document_by_id.return_value = mock_doc
        
        tools = await self.mcp_server.mcp.get_tools()
        get_doc_tool = None
        for tool in tools.values():
            if tool.name == "get_fastapi_doc_by_id":
                get_doc_tool = tool
                break
        
        result = await get_doc_tool.fn("test-1")
        
        assert result == mock_doc
        self.mock_search_engine.get_document_by_id.assert_called_once_with("test-1")
    
    async def test_get_fastapi_doc_by_id_not_found(self):
        """Test document retrieval when document not found."""
        self.mock_search_engine.get_document_by_id.return_value = None
        
        tools = await self.mcp_server.mcp.get_tools()
        get_doc_tool = None
        for tool in tools.values():
            if tool.name == "get_fastapi_doc_by_id":
                get_doc_tool = tool
                break
        
        result = await get_doc_tool.fn("nonexistent")
        
        assert "error" in result
        assert "Document with ID 'nonexistent' not found" in result["error"]
    
    async def test_refresh_fastapi_docs(self):
        """Test documentation refresh."""
        mock_result = {"status": "success", "document_count": 10}
        self.mock_data_loader.refresh_data.return_value = mock_result
        
        tools = await self.mcp_server.mcp.get_tools()
        refresh_tool = None
        for tool in tools.values():
            if tool.name == "refresh_fastapi_docs":
                refresh_tool = tool
                break
        
        result = await refresh_tool.fn()
        
        assert result == mock_result
        self.mock_data_loader.refresh_data.assert_called_once()
    
    async def test_get_available_tags(self):
        """Test getting available tags."""
        tools = await self.mcp_server.mcp.get_tools()
        tags_tool = None
        for tool in tools.values():
            if tool.name == "get_available_tags":
                tags_tool = tool
                break
        
        result = await tags_tool.fn()
        
        assert "tags" in result
        assert "api" in result["tags"]
        assert "pydantic" in result["tags"]
        assert "async" in result["tags"]
    
    async def test_close(self):
        """Test server cleanup."""
        await self.mcp_server.close()
        self.mock_search_engine.close.assert_called_once()
