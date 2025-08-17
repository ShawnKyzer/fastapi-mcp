"""
Search engine implementation using Elasticsearch following SOLID principles.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from .interfaces import DocumentChunk, ISearchEngine

logger = logging.getLogger(__name__)


class ElasticsearchEngine(ISearchEngine):
    """Elasticsearch implementation of the search engine interface."""
    
    def __init__(self, url: str, index_name: str):
        self.es = AsyncElasticsearch([url])
        self.index_name = index_name
    
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
