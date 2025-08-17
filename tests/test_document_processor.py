"""
Tests for document processor.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from src.document_processor import FastAPIDocumentProcessor


class TestFastAPIDocumentProcessor:
    """Test cases for FastAPIDocumentProcessor."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = FastAPIDocumentProcessor()
    
    def test_extract_tags_api_content(self):
        """Test tag extraction for API-related content."""
        content = "Use @app.get('/items/') to create a GET endpoint"
        section = "API Endpoints"
        
        tags = self.processor.extract_tags(content, section)
        
        assert "api" in tags
        assert "http-methods" in tags
        assert "api-endpoints" in tags
    
    def test_extract_tags_pydantic_content(self):
        """Test tag extraction for Pydantic-related content."""
        content = "Create a BaseModel class for data validation using Pydantic"
        section = "Data Models"
        
        tags = self.processor.extract_tags(content, section)
        
        assert "pydantic" in tags
        assert "data-models" in tags
    
    def test_extract_tags_async_content(self):
        """Test tag extraction for async-related content."""
        content = "Use async def and await for asynchronous operations"
        section = "Async Programming"
        
        tags = self.processor.extract_tags(content, section)
        
        assert "async" in tags
        assert "async-programming" in tags
    
    @pytest.mark.asyncio
    async def test_process_markdown_file(self, sample_markdown_content, tmp_path):
        """Test processing a markdown file."""
        # Create temporary markdown file
        test_file = tmp_path / "test.md"
        test_file.write_text(sample_markdown_content)
        
        base_url = "https://fastapi.tiangolo.com/test"
        
        chunks = await self.processor.process_markdown_file(str(test_file), base_url)
        
        assert len(chunks) > 0
        
        # Check first chunk
        first_chunk = chunks[0]
        assert first_chunk.title
        assert first_chunk.content
        assert first_chunk.url == base_url
        assert first_chunk.section
        assert len(first_chunk.tags) > 0
    
    def test_extract_tags_multiple_patterns(self):
        """Test tag extraction with multiple matching patterns."""
        content = """
        Create async endpoints with FastAPI using @app.post and Pydantic models.
        Add security middleware and database connections for testing.
        """
        section = "Advanced Features"
        
        tags = self.processor.extract_tags(content, section)
        
        # Check for some expected tags (not all, as regex matching can vary)
        assert "async" in tags
        assert "http-methods" in tags
        assert "pydantic" in tags
        assert "advanced-features" in tags
    
    def test_extract_tags_empty_content(self):
        """Test tag extraction with empty content."""
        tags = self.processor.extract_tags("", "")
        assert tags == []
    
    def test_extract_tags_no_matches(self):
        """Test tag extraction with content that doesn't match any patterns."""
        content = "This is just some random text without any specific keywords."
        section = "Random Section"
        
        tags = self.processor.extract_tags(content, section)
        
        # Should at least have the section-based tag
        assert "random-section" in tags
