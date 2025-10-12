from typing import List

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_session
from ..models import Page, Site

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
    db: Session = Depends(get_session)
):
    """Search across sites and pages."""
    results = []
    
    # Search sites
    sites = (
        db.query(Site)
        .filter(
            (Site.title.ilike(f"%{q}%")) | (Site.description.ilike(f"%{q}%"))
        )
        .filter(Site.status == "published")
        .limit(limit // 2)
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
    
    # Search pages
    pages = (
        db.query(Page)
        .filter(Page.title.ilike(f"%{q}%"))
        .filter(Page.status == "published")
        .limit(limit // 2)
        .all()
    )
    
    for page in pages:
        site = db.query(Site).filter(Site.id == page.site_id).first()
        if site:
            results.append(
                    SearchResult(
                        type="page",
                        id=page.id,
                        title=page.title,
                        snippet=page.page_metadata.get("description", "")[:200],
                        url=f"/sites/{site.slug}/pages{page.path}",
                    )
                )
    
    return results[:limit]
