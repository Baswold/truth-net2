from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import get_session
from ..models import Page, Site
from ..services import site_builder

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
    metadata: dict = Field(alias="page_metadata")

    class Config:
        from_attributes = True
        populate_by_name = True


class BlueprintResponse(BaseModel):
    key: str
    title: str
    description: str
    sections: List[str]
    recommended_blocks: List[str]


class ContentSection(BaseModel):
    heading: str
    summary: str
    callouts: List[str] = Field(default_factory=list)


class PagePreviewRequest(BaseModel):
    blueprint_key: str
    content_outline: List[ContentSection] = Field(default_factory=list)
    seo_keywords: List[str] = Field(default_factory=list)
    audience: str | None = None
    enable_flags: dict[str, bool] = Field(default_factory=dict)


class PagePreviewResponse(BaseModel):
    layout_json: dict
    metadata: dict
    recommendations: List[str]


@router.get("/", response_model=List[SiteResponse])
def list_sites(db: Session = Depends(get_session)):
    """Get all published sites."""
    sites = db.query(Site).filter(Site.status == "published").all()
    return sites


@router.get("/blueprints", response_model=List[BlueprintResponse])
def available_blueprints():
    """Return the available page blueprints for the WYSIWYG builder."""

    return [BlueprintResponse(**bp) for bp in site_builder.list_blueprints()]


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


@router.post("/{slug}/pages/preview", response_model=PagePreviewResponse)
def preview_page_blueprint(
    slug: str,
    request: PagePreviewRequest,
    db: Session = Depends(get_session),
):
    """Generate a layout preview for a page using the enhanced builder."""

    site = db.query(Site).filter(Site.slug == slug).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    preview = site_builder.create_preview(
        request.blueprint_key,
        [section.model_dump() for section in request.content_outline],
        enable_flags=request.enable_flags,
        seo_keywords=request.seo_keywords,
        audience=request.audience,
    )

    return PagePreviewResponse(
        layout_json=preview["layout"],
        metadata=preview["metadata"],
        recommendations=preview["recommendations"],
    )
