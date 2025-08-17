"""
Pytest configuration and fixtures.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from pathlib import Path

from src.interfaces import DocumentChunk


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_document_chunk():
    """Sample document chunk for testing."""
    return DocumentChunk(
        id="test-doc-1",
        title="Test Document",
        content="This is a test document about FastAPI endpoints.",
        url="https://fastapi.tiangolo.com/test",
        section="Getting Started",
        subsection="First Steps",
        tags=["api", "testing"],
        embedding_text="Getting Started First Steps This is a test document about FastAPI endpoints."
    )


@pytest.fixture
def sample_markdown_content():
    """Sample markdown content for testing."""
    return """# Getting Started

This is an introduction to FastAPI.

## Creating Your First API

Here's how to create a simple API:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
```

This creates a basic endpoint that returns a JSON response.

## Pydantic Models

FastAPI uses Pydantic for data validation:

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float
```

Use these models to validate request and response data.
"""


@pytest.fixture
def mock_elasticsearch():
    """Mock Elasticsearch client."""
    mock_es = AsyncMock()
    mock_es.indices.exists.return_value = False
    mock_es.indices.create.return_value = {"acknowledged": True}
    mock_es.indices.delete.return_value = {"acknowledged": True}
    mock_es.search.return_value = {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "id": "test-doc-1",
                        "title": "Test Document",
                        "content": "Test content",
                        "url": "https://test.com",
                        "section": "Test Section",
                        "tags": ["test"]
                    },
                    "_score": 1.0,
                    "highlight": {"content": ["Test <em>content</em>"]}
                }
            ]
        }
    }
    mock_es.get.return_value = {
        "_source": {
            "id": "test-doc-1",
            "title": "Test Document",
            "content": "Test content"
        }
    }
    return mock_es


@pytest.fixture
def mock_git_repo():
    """Mock Git repository."""
    mock_repo = MagicMock()
    mock_repo.remotes.origin.pull.return_value = None
    return mock_repo


@pytest.fixture
def temp_test_dir(tmp_path):
    """Temporary directory for testing."""
    test_dir = tmp_path / "test_repo" / "docs" / "en"
    test_dir.mkdir(parents=True)
    
    # Create test markdown file
    test_file = test_dir / "test.md"
    test_file.write_text("""# Test Document

This is a test document for FastAPI.

## API Endpoints

Create endpoints using decorators:

```python
@app.get("/items/")
def read_items():
    return [{"item_id": "Foo"}]
```
""")
    
    return tmp_path / "test_repo"
