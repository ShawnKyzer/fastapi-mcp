#!/usr/bin/env python3
"""
Setup Kibana dashboard for FastAPI documentation analysis.
Creates index patterns, visualizations, and a comprehensive dashboard.
"""

import requests
import json
import time
from typing import Dict, Any

KIBANA_URL = "http://localhost:5601"
HEADERS = {
    "Content-Type": "application/json",
    "kbn-xsrf": "true"
}

def wait_for_kibana():
    """Wait for Kibana to be ready."""
    print("Waiting for Kibana to be ready...")
    for i in range(30):
        try:
            response = requests.get(f"{KIBANA_URL}/api/status")
            if response.status_code == 200:
                print("✅ Kibana is ready!")
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(2)
    return False

def create_index_pattern():
    """Create index pattern for fastapi_docs."""
    print("Creating index pattern...")
    
    data = {
        "attributes": {
            "title": "fastapi_docs",
            "timeFieldName": "indexed_at"
        }
    }
    
    response = requests.post(
        f"{KIBANA_URL}/api/saved_objects/index-pattern/fastapi-docs-pattern",
        headers=HEADERS,
        json=data
    )
    
    if response.status_code in [200, 409]:  # 409 means already exists
        print("✅ Index pattern created/exists")
        return True
    else:
        print(f"❌ Failed to create index pattern: {response.text}")
        return False

def create_visualization(viz_id: str, viz_config: Dict[str, Any]):
    """Create a visualization in Kibana."""
    print(f"Creating visualization: {viz_config['attributes']['title']}")
    
    response = requests.post(
        f"{KIBANA_URL}/api/saved_objects/visualization/{viz_id}",
        headers=HEADERS,
        json=viz_config
    )
    
    if response.status_code in [200, 409]:
        print(f"✅ Visualization '{viz_config['attributes']['title']}' created/exists")
        return True
    else:
        print(f"❌ Failed to create visualization: {response.text}")
        return False

def create_dashboard():
    """Create the main dashboard."""
    print("Creating FastAPI Documentation Dashboard...")
    
    dashboard_config = {
        "attributes": {
            "title": "FastAPI Documentation Analysis",
            "description": "Comprehensive analysis of FastAPI documentation data",
            "panelsJSON": json.dumps([
                {
                    "version": "8.18.3",
                    "gridData": {"x": 0, "y": 0, "w": 24, "h": 15, "i": "1"},
                    "panelIndex": "1",
                    "embeddableConfig": {},
                    "panelRefName": "panel_1"
                },
                {
                    "version": "8.18.3", 
                    "gridData": {"x": 24, "y": 0, "w": 24, "h": 15, "i": "2"},
                    "panelIndex": "2",
                    "embeddableConfig": {},
                    "panelRefName": "panel_2"
                },
                {
                    "version": "8.18.3",
                    "gridData": {"x": 0, "y": 15, "w": 48, "h": 15, "i": "3"},
                    "panelIndex": "3", 
                    "embeddableConfig": {},
                    "panelRefName": "panel_3"
                }
            ]),
            "optionsJSON": json.dumps({
                "useMargins": True,
                "syncColors": False,
                "hidePanelTitles": False
            }),
            "version": 1,
            "timeRestore": False,
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "query": {"query": "", "language": "kuery"},
                    "filter": []
                })
            }
        },
        "references": [
            {"name": "panel_1", "type": "visualization", "id": "tags-distribution"},
            {"name": "panel_2", "type": "visualization", "id": "sections-breakdown"},
            {"name": "panel_3", "type": "search", "id": "docs-table"}
        ]
    }
    
    response = requests.post(
        f"{KIBANA_URL}/api/saved_objects/dashboard/fastapi-docs-dashboard",
        headers=HEADERS,
        json=dashboard_config
    )
    
    if response.status_code in [200, 409]:
        print("✅ Dashboard created/exists")
        return True
    else:
        print(f"❌ Failed to create dashboard: {response.text}")
        return False

def setup_visualizations():
    """Setup all visualizations."""
    
    # Tags distribution pie chart
    tags_viz = {
        "attributes": {
            "title": "Documentation Tags Distribution",
            "visState": json.dumps({
                "title": "Documentation Tags Distribution",
                "type": "pie",
                "aggs": [
                    {"id": "1", "type": "count", "params": {}},
                    {
                        "id": "2", 
                        "type": "terms", 
                        "params": {
                            "field": "tags",
                            "size": 15,
                            "order": "desc",
                            "orderBy": "1"
                        }
                    }
                ]
            }),
            "uiStateJSON": "{}",
            "description": "Distribution of tags across FastAPI documentation",
            "version": 1,
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": "fastapi-docs-pattern",
                    "query": {"query": "", "language": "kuery"},
                    "filter": []
                })
            }
        },
        "references": [
            {"name": "kibanaSavedObjectMeta.searchSourceJSON.index", "type": "index-pattern", "id": "fastapi-docs-pattern"}
        ]
    }
    
    # Sections breakdown bar chart
    sections_viz = {
        "attributes": {
            "title": "Documentation Sections Breakdown",
            "visState": json.dumps({
                "title": "Documentation Sections Breakdown", 
                "type": "horizontal_bar",
                "aggs": [
                    {"id": "1", "type": "count", "params": {}},
                    {
                        "id": "2",
                        "type": "terms",
                        "params": {
                            "field": "section.keyword",
                            "size": 20,
                            "order": "desc", 
                            "orderBy": "1"
                        }
                    }
                ]
            }),
            "uiStateJSON": "{}",
            "description": "Breakdown of documentation by sections",
            "version": 1,
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": "fastapi-docs-pattern",
                    "query": {"query": "", "language": "kuery"},
                    "filter": []
                })
            }
        },
        "references": [
            {"name": "kibanaSavedObjectMeta.searchSourceJSON.index", "type": "index-pattern", "id": "fastapi-docs-pattern"}
        ]
    }
    
    # Documents table
    docs_table = {
        "attributes": {
            "title": "FastAPI Documentation Entries",
            "description": "Searchable table of all documentation entries",
            "hits": 0,
            "columns": ["title", "section", "subsection", "tags", "indexed_at"],
            "sort": [["indexed_at", "desc"]],
            "version": 1,
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": "fastapi-docs-pattern",
                    "highlightAll": True,
                    "version": True,
                    "query": {"query": "", "language": "kuery"},
                    "filter": []
                })
            }
        },
        "references": [
            {"name": "kibanaSavedObjectMeta.searchSourceJSON.index", "type": "index-pattern", "id": "fastapi-docs-pattern"}
        ]
    }
    
    # Create visualizations
    create_visualization("tags-distribution", tags_viz)
    create_visualization("sections-breakdown", sections_viz)
    
    # Create saved search
    response = requests.post(
        f"{KIBANA_URL}/api/saved_objects/search/docs-table",
        headers=HEADERS,
        json=docs_table
    )
    
    if response.status_code in [200, 409]:
        print("✅ Documentation table created/exists")
    else:
        print(f"❌ Failed to create docs table: {response.text}")

def main():
    """Main setup function."""
    print("🚀 Setting up Kibana dashboard for FastAPI documentation...")
    
    if not wait_for_kibana():
        print("❌ Kibana is not responding. Please check if it's running.")
        return
    
    # Setup components
    create_index_pattern()
    setup_visualizations()
    create_dashboard()
    
    print("\n✅ Kibana dashboard setup complete!")
    print(f"🌐 Access your dashboard at: {KIBANA_URL}/app/dashboards#/view/fastapi-docs-dashboard")
    print(f"🔍 Explore data at: {KIBANA_URL}/app/discover#/?_g=(filters:!(),refreshInterval:(pause:!t,value:0),time:(from:now-24h,to:now))&_a=(columns:!(title,section,tags),filters:!(),index:fastapi-docs-pattern)")

if __name__ == "__main__":
    main()
