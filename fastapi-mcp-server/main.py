#!/usr/bin/env python3
"""
Main entry point for the FastAPI MCP Server.
"""

import asyncio
import logging

from src.config import Config
from src.data_loader import FastAPIDataLoader
from src.document_fetcher import FastAPIDocumentFetcher
from src.document_processor import FastAPIDocumentProcessor
from src.mcp_server import FastAPIMCPServer
from src.search_engine import ElasticsearchEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def initialize_server() -> FastAPIMCPServer:
    """Initialize the MCP server with all dependencies."""
    config = Config()
    
    # Create components following dependency injection
    processor = FastAPIDocumentProcessor(config.FASTAPI_DOCS_URL)
    fetcher = FastAPIDocumentFetcher(
        config.FASTAPI_REPO_URL,
        config.TEMP_REPO_PATH,
        processor,
        config.FASTAPI_DOCS_URL
    )
    search_engine = ElasticsearchEngine(config.ELASTICSEARCH_URL, config.INDEX_NAME)
    data_loader = FastAPIDataLoader(fetcher, search_engine)
    
    # Create MCP server
    mcp_server = FastAPIMCPServer(data_loader, search_engine)
    
    return mcp_server


async def startup_initialization(mcp_server: FastAPIMCPServer):
    """Initialize the server on startup."""
    try:
        # Check if index exists, if not, load data
        config = Config()
        es = ElasticsearchEngine(config.ELASTICSEARCH_URL, config.INDEX_NAME)
        
        if not await es.es.indices.exists(index=config.INDEX_NAME):
            logger.info("Index doesn't exist, loading documentation...")
            result = await mcp_server.data_loader.load_data()
            if "error" in result:
                logger.error(f"Failed to load data: {result['error']}")
            else:
                logger.info(result["message"])
        else:
            logger.info("Index exists, server ready")
        
        await es.close()
    except Exception as e:
        logger.warning(f"Startup initialization failed: {e}")


def main():
    """Main function."""
    async def run_server():
        mcp_server = await initialize_server()
        await startup_initialization(mcp_server)
        return mcp_server
    
    # Initialize and run
    mcp_server = asyncio.run(run_server())
    
    try:
        mcp_server.run()
    finally:
        # Cleanup
        asyncio.run(mcp_server.close())


if __name__ == "__main__":
    main()
