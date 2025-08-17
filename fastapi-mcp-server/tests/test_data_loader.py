"""
Tests for data loader.
"""

import pytest
from unittest.mock import AsyncMock

from src.data_loader import FastAPIDataLoader


@pytest.mark.asyncio
class TestFastAPIDataLoader:
    """Test cases for FastAPIDataLoader."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_fetcher = AsyncMock()
        self.mock_search_engine = AsyncMock()
        self.data_loader = FastAPIDataLoader(self.mock_fetcher, self.mock_search_engine)
    
    async def test_load_data_success(self, sample_document_chunk):
        """Test successful data loading."""
        self.mock_fetcher.clone_or_update_repo.return_value = None
        self.mock_fetcher.extract_documents.return_value = [sample_document_chunk]
        self.mock_search_engine.create_index.return_value = None
        self.mock_search_engine.index_documents.return_value = None
        
        result = await self.data_loader.load_data()
        
        assert result["status"] == "success"
        assert result["document_count"] == 1
        assert "Successfully loaded 1 documentation chunks" in result["message"]
        
        self.mock_fetcher.clone_or_update_repo.assert_called_once()
        self.mock_fetcher.extract_documents.assert_called_once()
        self.mock_search_engine.create_index.assert_called_once()
        self.mock_search_engine.index_documents.assert_called_once()
    
    async def test_load_data_no_documents(self):
        """Test data loading when no documents are found."""
        self.mock_fetcher.clone_or_update_repo.return_value = None
        self.mock_fetcher.extract_documents.return_value = []
        
        result = await self.data_loader.load_data()
        
        assert "error" in result
        assert result["error"] == "No documents found in repository"
    
    async def test_load_data_fetcher_error(self):
        """Test data loading when fetcher fails."""
        self.mock_fetcher.clone_or_update_repo.side_effect = Exception("Git error")
        
        result = await self.data_loader.load_data()
        
        assert "error" in result
        assert "Data loading failed: Git error" in result["error"]
    
    async def test_load_data_search_engine_error(self, sample_document_chunk):
        """Test data loading when search engine fails."""
        self.mock_fetcher.clone_or_update_repo.return_value = None
        self.mock_fetcher.extract_documents.return_value = [sample_document_chunk]
        self.mock_search_engine.create_index.side_effect = Exception("ES error")
        
        result = await self.data_loader.load_data()
        
        assert "error" in result
        assert "Data loading failed: ES error" in result["error"]
    
    async def test_refresh_data(self, sample_document_chunk):
        """Test data refresh (should be same as load_data)."""
        self.mock_fetcher.clone_or_update_repo.return_value = None
        self.mock_fetcher.extract_documents.return_value = [sample_document_chunk]
        self.mock_search_engine.create_index.return_value = None
        self.mock_search_engine.index_documents.return_value = None
        
        result = await self.data_loader.refresh_data()
        
        assert result["status"] == "success"
        assert result["document_count"] == 1
