"""
Document fetcher implementation following SOLID principles.
"""

import logging
from pathlib import Path
from typing import List

import httpx
from git import Repo

from .interfaces import DocumentChunk, IDocumentFetcher, IDocumentProcessor

logger = logging.getLogger(__name__)


class FastAPIDocumentFetcher(IDocumentFetcher):
    """Fetches FastAPI documentation from GitHub repository."""
    
    def __init__(
        self, 
        repo_url: str,
        repo_path: str,
        processor: IDocumentProcessor,
        base_docs_url: str = "https://fastapi.tiangolo.com"
    ):
        self.repo_url = repo_url
        self.repo_path = Path(repo_path)
        self.processor = processor
        self.base_docs_url = base_docs_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def clone_or_update_repo(self) -> None:
        """Clone or update the FastAPI repository."""
        try:
            if self.repo_path.exists():
                logger.info("Updating existing FastAPI repository...")
                repo = Repo(self.repo_path)
                repo.remotes.origin.pull()
            else:
                logger.info("Cloning FastAPI repository...")
                self.repo_path.parent.mkdir(parents=True, exist_ok=True)
                Repo.clone_from(self.repo_url, self.repo_path)
            logger.info("Repository updated successfully")
        except Exception as e:
            logger.error(f"Failed to clone/update repository: {e}")
            raise
    
    async def extract_documents(self) -> List[DocumentChunk]:
        """Extract documentation from the cloned repository."""
        docs = []
        docs_path = self.repo_path / "docs" / "en"
        
        if not docs_path.exists():
            logger.warning("English docs directory not found in repository")
            return docs
        
        # Process markdown files
        for md_file in docs_path.rglob("*.md"):
            try:
                # Extract relative path for URL construction
                rel_path = md_file.relative_to(docs_path)
                base_url = f"{self.base_docs_url}/{rel_path.with_suffix('')}"
                
                content = await self.processor.process_markdown_file(str(md_file), base_url)
                if content:
                    docs.extend(content)
            except Exception as e:
                logger.error(f"Error processing {md_file}: {e}")
        
        logger.info(f"Extracted {len(docs)} documentation chunks from repository")
        return docs
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
