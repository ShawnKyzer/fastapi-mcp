"""
Data loader implementation following SOLID principles.
"""

import logging
from typing import Any, Dict

from .interfaces import IDataLoader, IDocumentFetcher, ISearchEngine

logger = logging.getLogger(__name__)


class FastAPIDataLoader(IDataLoader):
    """Loads FastAPI documentation data into the search engine."""
    
    def __init__(self, fetcher: IDocumentFetcher, search_engine: ISearchEngine):
        self.fetcher = fetcher
        self.search_engine = search_engine
    
    async def load_data(self) -> Dict[str, Any]:
        """Load data into the system."""
        try:
            logger.info("Starting data loading process...")
            
            # Clone/update repository
            await self.fetcher.clone_or_update_repo()
            
            # Extract documentation
            documents = await self.fetcher.extract_documents()
            
            if not documents:
                return {"error": "No documents found in repository"}
            
            # Create/recreate index
            await self.search_engine.create_index()
            
            # Index documents
            await self.search_engine.index_documents(documents)
            
            return {
                "status": "success",
                "message": f"Successfully loaded {len(documents)} documentation chunks",
                "document_count": len(documents)
            }
        except Exception as e:
            logger.error(f"Data loading failed: {e}")
            return {"error": f"Data loading failed: {str(e)}"}
    
    async def refresh_data(self) -> Dict[str, Any]:
        """Refresh existing data."""
        return await self.load_data()  # Same process for refresh
