"""
Tests for search engine.
"""

import pytest
from unittest.mock import AsyncMock, patch

from src.search_engine import ElasticsearchEngine
from src.interfaces import DocumentChunk


@pytest.mark.asyncio
class TestElasticsearchEngine:
    """Test cases for ElasticsearchEngine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.search_engine = ElasticsearchEngine("http://localhost:9200", "test_index")
    
    @patch('src.search_engine.AsyncElasticsearch')
    async def test_create_index_new(self, mock_es_class):
        """Test creating a new index."""
        mock_es = AsyncMock()
        mock_es.indices.get.side_effect = Exception("Index not found")
        mock_es.indices.create.return_value = {"acknowledged": True}
        mock_es_class.return_value = mock_es
        
        engine = ElasticsearchEngine("http://localhost:9200", "test_index")
        await engine.create_index()
        
        mock_es.indices.get.assert_called_once_with(index="test_index")
        mock_es.indices.create.assert_called_once()
    
    @patch('src.search_engine.AsyncElasticsearch')
    async def test_create_index_existing(self, mock_es_class):
        """Test creating index when one already exists."""
        mock_es = AsyncMock()
        mock_es.indices.get.return_value = {"test_index": {}}
        mock_es.indices.delete.return_value = {"acknowledged": True}
        mock_es.indices.create.return_value = {"acknowledged": True}
        mock_es_class.return_value = mock_es
        
        engine = ElasticsearchEngine("http://localhost:9200", "test_index")
        await engine.create_index()
        
        mock_es.indices.get.assert_called_once_with(index="test_index")
        mock_es.indices.delete.assert_called_once_with(index="test_index")
        mock_es.indices.create.assert_called_once()
    
    @patch('src.search_engine.AsyncElasticsearch')
    @patch('src.search_engine.async_bulk')
    async def test_index_documents(self, mock_bulk, mock_es_class, sample_document_chunk):
        """Test indexing documents."""
        mock_es = AsyncMock()
        mock_es_class.return_value = mock_es
        mock_bulk.return_value = (1, [])
        
        engine = ElasticsearchEngine("http://localhost:9200", "test_index")
        await engine.index_documents([sample_document_chunk])
        
        mock_bulk.assert_called_once()
        args, kwargs = mock_bulk.call_args
        assert len(args[1]) == 1  # One document
        assert args[1][0]["_id"] == "test-doc-1"
    
    @patch('src.search_engine.AsyncElasticsearch')
    async def test_search_documents(self, mock_es_class):
        """Test searching documents."""
        mock_es = AsyncMock()
        mock_es.search.return_value = {
            "hits": {
                "hits": [
                    {
                        "_source": {"id": "test-1", "title": "Test", "content": "Content"},
                        "_score": 1.0,
                        "highlight": {"content": ["Test <em>content</em>"]}
                    }
                ]
            }
        }
        mock_es_class.return_value = mock_es
        
        engine = ElasticsearchEngine("http://localhost:9200", "test_index")
        results = await engine.search_documents("test query")
        
        assert len(results) == 1
        assert results[0]["_source"]["id"] == "test-1"
        mock_es.search.assert_called_once()
    
    @patch('src.search_engine.AsyncElasticsearch')
    async def test_search_documents_with_tags(self, mock_es_class):
        """Test searching documents with tag filters."""
        mock_es = AsyncMock()
        mock_es.search.return_value = {"hits": {"hits": []}}
        mock_es_class.return_value = mock_es
        
        engine = ElasticsearchEngine("http://localhost:9200", "test_index")
        await engine.search_documents("test query", tags=["api", "pydantic"])
        
        mock_es.search.assert_called_once()
        call_args = mock_es.search.call_args[1]
        assert "filter" in call_args["body"]["query"]["bool"]
    
    @patch('src.search_engine.AsyncElasticsearch')
    async def test_get_document_by_id(self, mock_es_class):
        """Test getting document by ID."""
        mock_es = AsyncMock()
        mock_es.get.return_value = {
            "_source": {"id": "test-1", "title": "Test Document"}
        }
        mock_es_class.return_value = mock_es
        
        engine = ElasticsearchEngine("http://localhost:9200", "test_index")
        result = await engine.get_document_by_id("test-1")
        
        assert result["id"] == "test-1"
        assert result["title"] == "Test Document"
        mock_es.get.assert_called_once_with(index="test_index", id="test-1")
    
    @patch('src.search_engine.AsyncElasticsearch')
    async def test_get_document_by_id_not_found(self, mock_es_class):
        """Test getting document by ID when not found."""
        mock_es = AsyncMock()
        mock_es.get.side_effect = Exception("Document not found")
        mock_es_class.return_value = mock_es
        
        engine = ElasticsearchEngine("http://localhost:9200", "test_index")
        result = await engine.get_document_by_id("nonexistent")
        
        assert result is None
