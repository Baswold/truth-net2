from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_session
from ..models import Page, Site

router = APIRouter(prefix="/sites", tags=["sites"])


class SiteResponse(BaseModel):
    id: int
    slug: str
    title: str
    description: str | None
    theme: str | None
    tags: dict
    status: str

    class Config:
        from_attributes = True


class PageResponse(BaseModel):
    id: int
    site_id: int
    path: str
    title: str
    status: str
    layout_json: dict
    metadata: dict

    class Config:
        from_attributes = True


@router.get("/", response_model=List[SiteResponse])
def list_sites(db: Session = Depends(get_session)):
    """Get all published sites."""
    sites = db.query(Site).filter(Site.status == "published").all()
    return sites


@router.get("/{slug}", response_model=SiteResponse)
def get_site(slug: str, db: Session = Depends(get_session)):
    """Get a site by slug."""
    site = db.query(Site).filter(Site.slug == slug).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site


@router.get("/{slug}/pages", response_model=List[PageResponse])
def get_site_pages(slug: str, db: Session = Depends(get_session)):
    """Get all pages for a site."""
    site = db.query(Site).filter(Site.slug == slug).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    
    pages = db.query(Page).filter(Page.site_id == site.id).all()
    return pages


@router.get("/{slug}/pages/{path:path}", response_model=PageResponse)
def get_page(slug: str, path: str, db: Session = Depends(get_session)):
    """Get a specific page."""
    site = db.query(Site).filter(Site.slug == slug).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    
    # Normalize path
    if not path.startswith("/"):
        path = "/" + path
    
    page = db.query(Page).filter(Page.site_id == site.id, Page.path == path).first()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    
    return page
