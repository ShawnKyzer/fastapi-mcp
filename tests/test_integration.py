"""
Integration tests for the FastAPI MCP Server.
"""

import pytest
from unittest.mock import patch, AsyncMock
from pathlib import Path

from src.config import Config
from src.data_loader import FastAPIDataLoader
from src.document_fetcher import FastAPIDocumentFetcher
from src.document_processor import FastAPIDocumentProcessor
from src.mcp_server import FastAPIMCPServer
from src.search_engine import ElasticsearchEngine


@pytest.mark.asyncio
class TestIntegration:
    """Integration test cases."""
    
    @patch('src.search_engine.AsyncElasticsearch')
    @patch('src.document_fetcher.Repo')
    async def test_full_data_loading_workflow(self, mock_repo_class, mock_es_class, temp_test_dir):
        """Test the complete data loading workflow."""
        # Mock Elasticsearch
        mock_es = AsyncMock()
        mock_es.indices.exists.return_value = False
        mock_es.indices.create.return_value = {"acknowledged": True}
        mock_es_class.return_value = mock_es
        
        # Mock Git repo
        mock_repo_class.clone_from.return_value = None
        
        # Mock async_bulk for indexing
        with patch('src.search_engine.async_bulk', return_value=(1, [])):
            # Create components
            config = Config()
            processor = FastAPIDocumentProcessor(config.FASTAPI_DOCS_URL)
            fetcher = FastAPIDocumentFetcher(
                config.FASTAPI_REPO_URL,
                str(temp_test_dir),
                processor,
                config.FASTAPI_DOCS_URL
            )
            search_engine = ElasticsearchEngine(config.ELASTICSEARCH_URL, config.INDEX_NAME)
            data_loader = FastAPIDataLoader(fetcher, search_engine)
            
            # Test data loading
            result = await data_loader.load_data()
            
            assert result["status"] == "success"
            assert result["document_count"] > 0
            
            # Verify Elasticsearch operations were called
            mock_es.indices.create.assert_called_once()
    
    @patch('src.search_engine.AsyncElasticsearch')
    async def test_mcp_server_with_mocked_dependencies(self, mock_es_class):
        """Test MCP server with mocked dependencies."""
        # Mock Elasticsearch
        mock_es = AsyncMock()
        mock_es.search.return_value = {
            "hits": {
                "hits": [
                    {
                        "_source": {
                            "id": "test-1",
                            "title": "Test Doc",
                            "content": "Test content",
                            "url": "https://test.com",
                            "section": "Test",
                            "tags": ["test"]
                        },
                        "_score": 1.0
                    }
                ]
            }
        }
        mock_es_class.return_value = mock_es
        
        # Create components
        mock_data_loader = AsyncMock()
        search_engine = ElasticsearchEngine("http://localhost:9200", "test_index")
        mcp_server = FastAPIMCPServer(mock_data_loader, search_engine)
        
        # Test that server initializes correctly
        assert mcp_server.mcp is not None
        tools = await mcp_server.mcp.get_tools()
        assert len(tools) == 4  # Should have 4 tools
        
        tool_names = [tool.name for tool in tools.values()]
        expected_tools = ["search_fastapi_docs", "get_fastapi_doc_by_id", "refresh_fastapi_docs", "get_available_tags"]
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
