#!/usr/bin/env python3
"""
FastAPI MCP Server

A Model Context Protocol server that fetches the latest FastAPI documentation
from GitHub and indexes it in Elasticsearch for AI coding assistants.

Compatible with Amazon Q, Windsurf, and Kiro.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import aiofiles
import httpx
from bs4 import BeautifulSoup
from elasticsearch import AsyncElasticsearch
from fastmcp import FastMCP
from git import Repo
from markdown import markdown
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
FASTAPI_REPO_URL = "https://github.com/fastapi/fastapi.git"
FASTAPI_DOCS_URL = "https://fastapi.tiangolo.com"
ELASTICSEARCH_URL = "http://localhost:9200"
INDEX_NAME = "fastapi_docs"
TEMP_REPO_PATH = "/tmp/fastapi_repo"


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


class FastAPIDocsFetcher:
    """Fetches and processes FastAPI documentation."""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.repo_path = Path(TEMP_REPO_PATH)
    
    async def clone_or_update_repo(self) -> None:
        """Clone or update the FastAPI repository."""
        try:
            if self.repo_path.exists():
                logger.info("Updating existing FastAPI repository...")
                repo = Repo(self.repo_path)
                repo.remotes.origin.pull()
            else:
                logger.info("Cloning FastAPI repository...")
                Repo.clone_from(FASTAPI_REPO_URL, self.repo_path)
            logger.info("Repository updated successfully")
        except Exception as e:
            logger.error(f"Failed to clone/update repository: {e}")
            raise
    
    async def extract_docs_from_repo(self) -> List[DocumentChunk]:
        """Extract documentation from the cloned repository."""
        docs = []
        docs_path = self.repo_path / "docs" / "en"
        
        if not docs_path.exists():
            logger.warning("English docs directory not found in repository")
            return docs
        
        # Process markdown files
        for md_file in docs_path.rglob("*.md"):
            try:
                content = await self._process_markdown_file(md_file)
                if content:
                    docs.extend(content)
            except Exception as e:
                logger.error(f"Error processing {md_file}: {e}")
        
        logger.info(f"Extracted {len(docs)} documentation chunks from repository")
        return docs
    
    async def _process_markdown_file(self, file_path: Path) -> List[DocumentChunk]:
        """Process a single markdown file into document chunks."""
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
        
        # Convert markdown to HTML for better parsing
        html_content = markdown(content, extensions=['toc', 'codehilite'])
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract relative path for URL construction
        rel_path = file_path.relative_to(self.repo_path / "docs" / "en")
        base_url = f"{FASTAPI_DOCS_URL}/{rel_path.with_suffix('')}"
        
        chunks = []
        current_section = ""
        current_subsection = ""
        
        # Process headings and content
        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'pre', 'ul', 'ol']):
            if element.name.startswith('h'):
                level = int(element.name[1])
                if level <= 2:
                    current_section = element.get_text().strip()
                    current_subsection = ""
                elif level <= 4:
                    current_subsection = element.get_text().strip()
            
            elif element.name in ['p', 'pre', 'ul', 'ol']:
                text_content = element.get_text().strip()
                if len(text_content) > 50:  # Only include substantial content
                    chunk_id = f"{rel_path}#{len(chunks)}"
                    
                    # Determine tags based on content
                    tags = self._extract_tags(text_content, current_section)
                    
                    chunk = DocumentChunk(
                        id=chunk_id,
                        title=current_subsection or current_section or str(rel_path.stem),
                        content=text_content,
                        url=base_url,
                        section=current_section,
                        subsection=current_subsection,
                        tags=tags,
                        embedding_text=f"{current_section} {current_subsection} {text_content}"
                    )
                    chunks.append(chunk)
        
        return chunks
    
    def _extract_tags(self, content: str, section: str) -> List[str]:
        """Extract relevant tags from content."""
        tags = []
        content_lower = content.lower()
        section_lower = section.lower()
        
        # API-related tags
        if any(word in content_lower for word in ['@app.', 'router', 'endpoint', 'path']):
            tags.append('api')
        if any(word in content_lower for word in ['get', 'post', 'put', 'delete', 'patch']):
            tags.append('http-methods')
        if 'pydantic' in content_lower or 'basemodel' in content_lower:
            tags.append('pydantic')
        if 'async' in content_lower or 'await' in content_lower:
            tags.append('async')
        if 'dependency' in content_lower or 'depends' in content_lower:
            tags.append('dependencies')
        if 'security' in content_lower or 'auth' in content_lower:
            tags.append('security')
        if 'database' in content_lower or 'sql' in content_lower:
            tags.append('database')
        if 'test' in content_lower:
            tags.append('testing')
        if 'deploy' in content_lower or 'docker' in content_lower:
            tags.append('deployment')
        
        # Section-based tags
        if section_lower:
            tags.append(section_lower.replace(' ', '-'))
        
        return list(set(tags))  # Remove duplicates
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class ElasticsearchManager:
    """Manages Elasticsearch operations for document indexing and search."""
    
    def __init__(self, url: str = ELASTICSEARCH_URL):
        self.es = AsyncElasticsearch([url])
        self.index_name = INDEX_NAME
    
    async def create_index(self) -> None:
        """Create the Elasticsearch index with proper mapping."""
        mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "title": {"type": "text", "analyzer": "standard"},
                    "content": {"type": "text", "analyzer": "standard"},
                    "url": {"type": "keyword"},
                    "section": {"type": "text", "analyzer": "standard"},
                    "subsection": {"type": "text", "analyzer": "standard"},
                    "tags": {"type": "keyword"},
                    "embedding_text": {"type": "text", "analyzer": "standard"},
                    "indexed_at": {"type": "date"}
                }
            },
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        }
        
        try:
            if await self.es.indices.exists(index=self.index_name):
                await self.es.indices.delete(index=self.index_name)
                logger.info(f"Deleted existing index: {self.index_name}")
            
            await self.es.indices.create(index=self.index_name, body=mapping)
            logger.info(f"Created index: {self.index_name}")
        except Exception as e:
            logger.error(f"Failed to create index: {e}")
            raise
    
    async def index_documents(self, documents: List[DocumentChunk]) -> None:
        """Index documents in Elasticsearch."""
        from datetime import datetime
        
        actions = []
        for doc in documents:
            action = {
                "_index": self.index_name,
                "_id": doc.id,
                "_source": {
                    **doc.model_dump(),
                    "indexed_at": datetime.utcnow().isoformat()
                }
            }
            actions.append(action)
        
        try:
            from elasticsearch.helpers import async_bulk
            success, failed = await async_bulk(self.es, actions)
            logger.info(f"Indexed {success} documents, {len(failed)} failed")
        except Exception as e:
            logger.error(f"Failed to index documents: {e}")
            raise
    
    async def search_documents(
        self, 
        query: str, 
        tags: Optional[List[str]] = None,
        size: int = 10
    ) -> List[Dict[str, Any]]:
        """Search documents in Elasticsearch."""
        search_body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["title^2", "content", "section^1.5", "subsection^1.5"],
                                "type": "best_fields",
                                "fuzziness": "AUTO"
                            }
                        }
                    ]
                }
            },
            "highlight": {
                "fields": {
                    "content": {"fragment_size": 150, "number_of_fragments": 3},
                    "title": {},
                    "section": {},
                    "subsection": {}
                }
            },
            "size": size
        }
        
        if tags:
            search_body["query"]["bool"]["filter"] = [
                {"terms": {"tags": tags}}
            ]
        
        try:
            response = await self.es.search(index=self.index_name, body=search_body)
            return response["hits"]["hits"]
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    async def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID."""
        try:
            response = await self.es.get(index=self.index_name, id=doc_id)
            return response["_source"]
        except Exception as e:
            logger.error(f"Failed to get document {doc_id}: {e}")
            return None
    
    async def close(self):
        """Close the Elasticsearch connection."""
        await self.es.close()


# Initialize the MCP server
mcp = FastMCP(
    name="FastAPI Documentation Server",
    instructions="""
    This server provides access to the latest FastAPI documentation indexed in Elasticsearch.
    Use the available tools to search for FastAPI-related information, get specific documentation
    sections, and refresh the documentation index when needed.
    
    Available capabilities:
    - Search FastAPI documentation with semantic search
    - Get specific documentation sections by ID
    - Refresh documentation from the latest GitHub repository
    - Filter searches by tags (api, pydantic, async, dependencies, security, etc.)
    """
)

# Global instances
docs_fetcher = FastAPIDocsFetcher()
es_manager = ElasticsearchManager()


@mcp.tool
async def search_fastapi_docs(
    query: str,
    tags: Optional[List[str]] = None,
    max_results: int = 10
) -> Dict[str, Any]:
    """
    Search FastAPI documentation using semantic search.
    
    Args:
        query: Search query (e.g., "how to create API endpoints", "pydantic models", "async dependencies")
        tags: Optional list of tags to filter by (api, pydantic, async, dependencies, security, database, testing, deployment)
        max_results: Maximum number of results to return (default: 10)
    
    Returns:
        Dictionary containing search results with highlighted content
    """
    try:
        results = await es_manager.search_documents(query, tags, max_results)
        
        formatted_results = []
        for hit in results:
            source = hit["_source"]
            highlight = hit.get("highlight", {})
            
            result = {
                "id": source["id"],
                "title": source["title"],
                "section": source["section"],
                "subsection": source.get("subsection"),
                "url": source["url"],
                "tags": source["tags"],
                "score": hit["_score"],
                "content": source["content"][:500] + "..." if len(source["content"]) > 500 else source["content"]
            }
            
            if highlight:
                result["highlights"] = highlight
            
            formatted_results.append(result)
        
        return {
            "query": query,
            "total_results": len(formatted_results),
            "results": formatted_results
        }
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return {"error": f"Search failed: {str(e)}"}


@mcp.tool
async def get_fastapi_doc_by_id(doc_id: str) -> Dict[str, Any]:
    """
    Get a specific FastAPI documentation section by its ID.
    
    Args:
        doc_id: The document ID from search results
    
    Returns:
        Complete document content
    """
    try:
        doc = await es_manager.get_document_by_id(doc_id)
        if doc:
            return doc
        else:
            return {"error": f"Document with ID '{doc_id}' not found"}
    except Exception as e:
        logger.error(f"Failed to get document: {e}")
        return {"error": f"Failed to get document: {str(e)}"}


@mcp.tool
async def refresh_fastapi_docs() -> Dict[str, Any]:
    """
    Refresh the FastAPI documentation by fetching the latest version from GitHub
    and re-indexing it in Elasticsearch.
    
    Returns:
        Status of the refresh operation
    """
    try:
        logger.info("Starting FastAPI documentation refresh...")
        
        # Clone/update repository
        await docs_fetcher.clone_or_update_repo()
        
        # Extract documentation
        documents = await docs_fetcher.extract_docs_from_repo()
        
        if not documents:
            return {"error": "No documents found in repository"}
        
        # Create/recreate index
        await es_manager.create_index()
        
        # Index documents
        await es_manager.index_documents(documents)
        
        return {
            "status": "success",
            "message": f"Successfully indexed {len(documents)} documentation chunks",
            "document_count": len(documents)
        }
    except Exception as e:
        logger.error(f"Refresh failed: {e}")
        return {"error": f"Refresh failed: {str(e)}"}


@mcp.tool
async def get_available_tags() -> Dict[str, Any]:
    """
    Get all available tags that can be used for filtering searches.
    
    Returns:
        List of available tags with descriptions
    """
    return {
        "tags": {
            "api": "API endpoints and routing",
            "http-methods": "HTTP methods (GET, POST, PUT, DELETE, etc.)",
            "pydantic": "Pydantic models and validation",
            "async": "Asynchronous programming",
            "dependencies": "Dependency injection",
            "security": "Authentication and authorization",
            "database": "Database integration",
            "testing": "Testing FastAPI applications",
            "deployment": "Deployment and Docker"
        }
    }


if __name__ == "__main__":
    # Initialize on startup
    async def startup():
        """Initialize the server on startup."""
        try:
            # Check if index exists, if not, refresh docs
            if not await es_manager.es.indices.exists(index=INDEX_NAME):
                logger.info("Index doesn't exist, refreshing documentation...")
                await refresh_fastapi_docs()
        except Exception as e:
            logger.warning(f"Startup initialization failed: {e}")
    
    # Run startup and then the server
    asyncio.run(startup())
    mcp.run()
