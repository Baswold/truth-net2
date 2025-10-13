"""MeiliSearch integration for full-text search."""
from __future__ import annotations

import logging
from typing import List, Literal

from meilisearch import Client
from meilisearch.errors import MeilisearchApiError

from ..config import settings

logger = logging.getLogger(__name__)


class SearchService:
    """Wrapper for MeiliSearch operations with fallback to DB search."""
    
    def __init__(self):
        self.client: Client | None = None
        try:
            self.client = Client(settings.search_url, settings.search_api_key)
            logger.info(f"Connected to MeiliSearch at {settings.search_url}")
        except Exception as e:
            logger.warning(f"Could not connect to MeiliSearch: {e}. Will use database fallback.")
    
    def is_available(self) -> bool:
        """Check if MeiliSearch is available."""
        if not self.client:
            return False
        try:
            self.client.health()
            return True
        except Exception:
            return False
    
    def index_site(self, site_id: int, slug: str, title: str, description: str | None, tags: dict):
        """Index a site for search."""
        if not self.is_available():
            return
        
        try:
            index = self.client.index("sites")
            index.add_documents([{
                "id": site_id,
                "slug": slug,
                "title": title,
                "description": description or "",
                "tags": list(tags.keys()) if tags else [],
                "type": "site"
            }])
        except MeilisearchApiError as e:
            logger.error(f"Failed to index site {site_id}: {e}")
    
    def index_page(self, page_id: int, site_slug: str, path: str, title: str, metadata: dict):
        """Index a page for search."""
        if not self.is_available():
            return
        
        try:
            index = self.client.index("pages")
            index.add_documents([{
                "id": page_id,
                "site_slug": site_slug,
                "path": path,
                "title": title,
                "description": metadata.get("description", ""),
                "keywords": metadata.get("keywords", []),
                "type": "page"
            }])
        except MeilisearchApiError as e:
            logger.error(f"Failed to index page {page_id}: {e}")
    
    def search_sites(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[dict]:
        """Search sites using MeiliSearch."""
        if not self.is_available():
            return []
        
        try:
            index = self.client.index("sites")
            results = index.search(query, {
                "limit": limit,
                "offset": offset,
                "attributesToHighlight": ["title", "description"],
                "attributesToRetrieve": ["id", "slug", "title", "description"]
            })
            return results.get("hits", [])
        except Exception as e:
            logger.error(f"MeiliSearch site search failed: {e}")
            return []
    
    def search_pages(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[dict]:
        """Search pages using MeiliSearch."""
        if not self.is_available():
            return []
        
        try:
            index = self.client.index("pages")
            results = index.search(query, {
                "limit": limit,
                "offset": offset,
                "attributesToHighlight": ["title", "description"],
                "attributesToRetrieve": ["id", "site_slug", "path", "title", "description"]
            })
            return results.get("hits", [])
        except Exception as e:
            logger.error(f"MeiliSearch page search failed: {e}")
            return []
    
    def setup_indexes(self):
        """Setup MeiliSearch indexes with proper configuration."""
        if not self.is_available():
            logger.warning("MeiliSearch not available. Skipping index setup.")
            return
        
        try:
            # Create sites index
            self.client.create_index("sites", {"primaryKey": "id"})
            sites_index = self.client.index("sites")
            sites_index.update_searchable_attributes(["title", "description", "tags"])
            sites_index.update_filterable_attributes(["type"])
            
            # Create pages index
            self.client.create_index("pages", {"primaryKey": "id"})
            pages_index = self.client.index("pages")
            pages_index.update_searchable_attributes(["title", "description", "keywords"])
            pages_index.update_filterable_attributes(["type", "site_slug"])
            
            logger.info("MeiliSearch indexes configured successfully")
        except MeilisearchApiError as e:
            if "already exists" not in str(e):
                logger.error(f"Failed to setup MeiliSearch indexes: {e}")


# Global search service instance
search_service = SearchService()
