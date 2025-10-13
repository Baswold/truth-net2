from typing import List

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session, joinedload

from ..database import get_session
from ..models import Page, Site
from ..services.search import search_service

router = APIRouter(prefix="/search", tags=["search"])


class SearchResult(BaseModel):
    type: str  # site, page, post
    id: int
    title: str
    snippet: str
    url: str
    trust_score: int | None = None


@router.get("/", response_model=List[SearchResult])
def search(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    type_filter: str | None = Query(None, description="Filter by type: site, page, or post"),
    use_db_fallback: bool = Query(False, description="Force database search instead of MeiliSearch"),
    db: Session = Depends(get_session)
):
    """Search across sites and pages using MeiliSearch with database fallback."""
    results = []
    
    # Try MeiliSearch first if available and not forcing DB
    if search_service.is_available() and not use_db_fallback:
        # Search sites via MeiliSearch
        if not type_filter or type_filter == "site":
            meili_sites = search_service.search_sites(q, limit=limit//2 if not type_filter else limit, offset=offset)
            for site_hit in meili_sites:
                results.append(
                    SearchResult(
                        type="site",
                        id=site_hit["id"],
                        title=site_hit["title"],
                        snippet=site_hit.get("description", "")[:200],
                        url=f"/sites/{site_hit['slug']}",
                    )
                )
        
        # Search pages via MeiliSearch
        if not type_filter or type_filter == "page":
            meili_pages = search_service.search_pages(q, limit=limit//2 if not type_filter else limit, offset=offset if type_filter == "page" else 0)
            for page_hit in meili_pages:
                results.append(
                    SearchResult(
                        type="page",
                        id=page_hit["id"],
                        title=page_hit["title"],
                        snippet=page_hit.get("description", "")[:200],
                        url=f"/sites/{page_hit['site_slug']}/pages{page_hit['path']}",
                    )
                )
        
        return results[:limit]
    
    # Fallback to database search
    # Search sites (if not filtered out)
    if not type_filter or type_filter == "site":
        sites = (
            db.query(Site)
            .filter(
                (Site.title.ilike(f"%{q}%")) | (Site.description.ilike(f"%{q}%"))
            )
            .filter(Site.status == "published")
            .offset(offset)
            .limit(limit // 2 if not type_filter else limit)
            .all()
        )
        
        for site in sites:
            results.append(
                SearchResult(
                    type="site",
                    id=site.id,
                    title=site.title,
                    snippet=site.description or "",
                    url=f"/sites/{site.slug}",
                )
            )
    
    # Search pages with joined Site to avoid N+1 (if not filtered out)
    if not type_filter or type_filter == "page":
        pages = (
            db.query(Page)
            .options(joinedload(Page.site))  # Eager load site to avoid N+1
            .filter(Page.title.ilike(f"%{q}%"))
            .filter(Page.status == "published")
            .offset(offset if type_filter == "page" else 0)
            .limit(limit // 2 if not type_filter else limit)
            .all()
        )
        
        for page in pages:
            if page.site:  # Site already loaded via joinedload
                results.append(
                    SearchResult(
                        type="page",
                        id=page.id,
                        title=page.title,
                        snippet=page.page_metadata.get("description", "")[:200],
                        url=f"/sites/{page.site.slug}/pages{page.path}",
                    )
                )
    
    return results[:limit]
