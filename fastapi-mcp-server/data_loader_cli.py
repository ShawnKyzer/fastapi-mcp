#!/usr/bin/env python3
"""
CLI utility for loading data into Elasticsearch.
"""

import asyncio
import logging
import sys
from pathlib import Path

from src.config import Config
from src.data_loader import FastAPIDataLoader
from src.document_fetcher import FastAPIDocumentFetcher
from src.document_processor import FastAPIDocumentProcessor
from src.search_engine import ElasticsearchEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def load_data():
    """Load FastAPI documentation data."""
    config = Config()
    
    try:
        # Initialize components
        processor = FastAPIDocumentProcessor(config.FASTAPI_DOCS_URL)
        fetcher = FastAPIDocumentFetcher(
            config.FASTAPI_REPO_URL,
            config.TEMP_REPO_PATH,
            processor,
            config.FASTAPI_DOCS_URL
        )
        search_engine = ElasticsearchEngine(config.ELASTICSEARCH_URL, config.INDEX_NAME)
        data_loader = FastAPIDataLoader(fetcher, search_engine)
        
        # Load data
        result = await data_loader.load_data()
        
        if "error" in result:
            logger.error(f"Data loading failed: {result['error']}")
            return False
        else:
            logger.info(f"Success: {result['message']}")
            return True
            
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False
    finally:
        # Cleanup
        try:
            await fetcher.close()
            await search_engine.close()
        except:
            pass


if __name__ == "__main__":
    success = asyncio.run(load_data())
    sys.exit(0 if success else 1)
