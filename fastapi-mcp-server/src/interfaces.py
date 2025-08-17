"""
Interfaces and abstract base classes following SOLID principles.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class DocumentChunk(BaseModel):
    """Represents a chunk of documentation."""
    id: str
    title: str
    content: str
    url: str
    section: str
    subsection: Optional[str] = None
    tags: List[str] = []
    embedding_text: str


class IDocumentFetcher(ABC):
    """Interface for document fetching operations."""
    
    @abstractmethod
    async def clone_or_update_repo(self) -> None:
        """Clone or update the repository."""
        pass
    
    @abstractmethod
    async def extract_documents(self) -> List[DocumentChunk]:
        """Extract documents from the repository."""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Clean up resources."""
        pass


class ISearchEngine(ABC):
    """Interface for search engine operations."""
    
    @abstractmethod
    async def create_index(self) -> None:
        """Create the search index."""
        pass
    
    @abstractmethod
    async def index_documents(self, documents: List[DocumentChunk]) -> None:
        """Index documents in the search engine."""
        pass
    
    @abstractmethod
    async def search_documents(
        self, 
        query: str, 
        tags: Optional[List[str]] = None,
        size: int = 10
    ) -> List[Dict[str, Any]]:
        """Search documents."""
        pass
    
    @abstractmethod
    async def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID."""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close the search engine connection."""
        pass


class IDocumentProcessor(ABC):
    """Interface for document processing operations."""
    
    @abstractmethod
    async def process_markdown_file(self, file_path: str, base_url: str) -> List[DocumentChunk]:
        """Process a markdown file into document chunks."""
        pass
    
    @abstractmethod
    def extract_tags(self, content: str, section: str) -> List[str]:
        """Extract relevant tags from content."""
        pass


class IDataLoader(ABC):
    """Interface for data loading operations."""
    
    @abstractmethod
    async def load_data(self) -> Dict[str, Any]:
        """Load data into the system."""
        pass
    
    @abstractmethod
    async def refresh_data(self) -> Dict[str, Any]:
        """Refresh existing data."""
        pass
