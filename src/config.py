"""
Configuration settings for the FastAPI MCP Server.
"""

from dataclasses import dataclass


@dataclass
class Config:
    """Configuration settings."""
    
    # Repository settings
    FASTAPI_REPO_URL: str = "https://github.com/fastapi/fastapi.git"
    TEMP_REPO_PATH: str = "/tmp/fastapi_repo"
    
    # Elasticsearch settings
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    INDEX_NAME: str = "fastapi_docs"
    
    # Documentation settings
    FASTAPI_DOCS_URL: str = "https://fastapi.tiangolo.com"
