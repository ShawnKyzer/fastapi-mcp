#!/usr/bin/env python3
"""
Test client for the FastAPI MCP Server

This script demonstrates how to interact with the FastAPI MCP server
and test its functionality.
"""

import asyncio
import json
from fastmcp import Client


async def test_fastapi_mcp_server():
    """Test the FastAPI MCP server functionality."""
    client = Client("fastapi_mcp_server.py")
    
    try:
        async with client:
            print("🚀 Testing FastAPI MCP Server")
            print("=" * 50)
            
            # Test 1: Get available tags
            print("\n1. Getting available tags...")
            tags_result = await client.call_tool("get_available_tags", {})
            print(f"Available tags: {json.dumps(tags_result, indent=2)}")
            
            # Test 2: Search for FastAPI documentation
            print("\n2. Searching for 'create API endpoint'...")
            search_result = await client.call_tool("search_fastapi_docs", {
                "query": "create API endpoint",
                "max_results": 3
            })
            print(f"Search results: {json.dumps(search_result, indent=2)}")
            
            # Test 3: Search with tags
            print("\n3. Searching for 'pydantic models' with pydantic tag...")
            tagged_search = await client.call_tool("search_fastapi_docs", {
                "query": "pydantic models",
                "tags": ["pydantic"],
                "max_results": 2
            })
            print(f"Tagged search results: {json.dumps(tagged_search, indent=2)}")
            
            # Test 4: Get specific document (if available from previous search)
            if search_result.get("results") and len(search_result["results"]) > 0:
                doc_id = search_result["results"][0]["id"]
                print(f"\n4. Getting document by ID: {doc_id}")
                doc_result = await client.call_tool("get_fastapi_doc_by_id", {
                    "doc_id": doc_id
                })
                print(f"Document: {json.dumps(doc_result, indent=2)}")
            
            print("\n✅ All tests completed successfully!")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_fastapi_mcp_server())
