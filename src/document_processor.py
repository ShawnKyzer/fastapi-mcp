"""
Document processing implementation following SOLID principles.
"""

import re
from pathlib import Path
from typing import List

import aiofiles
from bs4 import BeautifulSoup
from markdown import markdown

from .interfaces import DocumentChunk, IDocumentProcessor


class FastAPIDocumentProcessor(IDocumentProcessor):
    """Processes FastAPI documentation files."""
    
    def __init__(self, base_docs_url: str = "https://fastapi.tiangolo.com"):
        self.base_docs_url = base_docs_url
    
    async def process_markdown_file(self, file_path: str, base_url: str) -> List[DocumentChunk]:
        """Process a single markdown file into document chunks."""
        file_path_obj = Path(file_path)
        
        async with aiofiles.open(file_path_obj, 'r', encoding='utf-8') as f:
            content = await f.read()
        
        # Convert markdown to HTML for better parsing
        html_content = markdown(content, extensions=['toc', 'codehilite'])
        soup = BeautifulSoup(html_content, 'html.parser')
        
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
                    chunk_id = f"{file_path_obj.stem}#{len(chunks)}"
                    
                    # Determine tags based on content
                    tags = self.extract_tags(text_content, current_section)
                    
                    chunk = DocumentChunk(
                        id=chunk_id,
                        title=current_subsection or current_section or str(file_path_obj.stem),
                        content=text_content,
                        url=base_url,
                        section=current_section,
                        subsection=current_subsection,
                        tags=tags,
                        embedding_text=f"{current_section} {current_subsection} {text_content}"
                    )
                    chunks.append(chunk)
        
        return chunks
    
    def extract_tags(self, content: str, section: str) -> List[str]:
        """Extract relevant tags from content."""
        tags = []
        content_lower = content.lower()
        section_lower = section.lower()
        
        # API-related tags
        tag_patterns = {
            'api': [r'@app\.', r'router', r'endpoint', r'path'],
            'http-methods': [r'\b(get|post|put|delete|patch)\b'],
            'pydantic': [r'pydantic', r'basemodel'],
            'async': [r'\basync\b', r'\bawait\b'],
            'dependencies': [r'dependency', r'depends'],
            'security': [r'security', r'\bauth\b'],
            'database': [r'database', r'\bsql\b'],
            'testing': [r'\btest\b'],
            'deployment': [r'deploy', r'docker'],
            'validation': [r'validat', r'schema'],
            'middleware': [r'middleware'],
            'cors': [r'\bcors\b'],
            'websocket': [r'websocket'],
            'background-tasks': [r'background.*task'],
            'file-upload': [r'file.*upload', r'uploadfile'],
        }
        
        for tag, patterns in tag_patterns.items():
            if any(re.search(pattern, content_lower) for pattern in patterns):
                tags.append(tag)
        
        # Section-based tags
        if section_lower:
            section_tag = re.sub(r'[^\w\s-]', '', section_lower).replace(' ', '-')
            if section_tag:
                tags.append(section_tag)
        
        return list(set(tags))  # Remove duplicates
