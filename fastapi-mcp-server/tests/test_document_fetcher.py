"""
Tests for document fetcher.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

from src.document_fetcher import FastAPIDocumentFetcher
from src.document_processor import FastAPIDocumentProcessor


@pytest.mark.asyncio
class TestFastAPIDocumentFetcher:
    """Test cases for FastAPIDocumentFetcher."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = FastAPIDocumentProcessor()
        self.fetcher = FastAPIDocumentFetcher(
            "https://github.com/fastapi/fastapi.git",
            "/tmp/test_repo",
            self.processor
        )
    
    @patch('src.document_fetcher.Repo')
    async def test_clone_or_update_repo_new(self, mock_repo_class):
        """Test cloning a new repository."""
        mock_repo_class.clone_from.return_value = MagicMock()
        
        # Mock path not existing
        with patch.object(Path, 'exists', return_value=False):
            with patch.object(Path, 'mkdir'):
                await self.fetcher.clone_or_update_repo()
        
        mock_repo_class.clone_from.assert_called_once_with(
            "https://github.com/fastapi/fastapi.git",
            Path("/tmp/test_repo")
        )
    
    @patch('src.document_fetcher.Repo')
    async def test_clone_or_update_repo_existing(self, mock_repo_class):
        """Test updating an existing repository."""
        mock_repo = MagicMock()
        mock_repo.remotes.origin.pull.return_value = None
        mock_repo_class.return_value = mock_repo
        
        # Mock path existing
        with patch.object(Path, 'exists', return_value=True):
            await self.fetcher.clone_or_update_repo()
        
        mock_repo.remotes.origin.pull.assert_called_once()
    
    async def test_extract_documents_no_docs_dir(self):
        """Test extracting documents when docs directory doesn't exist."""
        with patch.object(Path, 'exists', return_value=False):
            docs = await self.fetcher.extract_documents()
        
        assert docs == []
    
    async def test_extract_documents_success(self, temp_test_dir):
        """Test successful document extraction."""
        mock_processor = AsyncMock()
        mock_processor.process_markdown_file.return_value = [
            MagicMock(id="test-1", title="Test Doc")
        ]
        
        fetcher = FastAPIDocumentFetcher(
            "https://github.com/fastapi/fastapi.git",
            str(temp_test_dir),
            mock_processor
        )
        
        docs = await fetcher.extract_documents()
        
        assert len(docs) > 0
        mock_processor.process_markdown_file.assert_called()
    
    async def test_close(self):
        """Test closing the fetcher."""
        self.fetcher.client = AsyncMock()
        await self.fetcher.close()
        self.fetcher.client.aclose.assert_called_once()
