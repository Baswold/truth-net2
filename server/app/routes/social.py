from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_session
from ..models import TruthPost, TruthThread

router = APIRouter(prefix="/social", tags=["social"])


class PostResponse(BaseModel):
    id: int
    author_id: int
    title: str | None
    content: str
    tags: dict
    citations: dict
    published: bool
    trust_score: int
    created_at: str

    class Config:
        from_attributes = True


class ThreadResponse(BaseModel):
    id: int
    post_id: int | None
    creator_id: int
    title: str
    topic: str | None
    locked: bool
    trust_score: int

    class Config:
        from_attributes = True


@router.get("/posts", response_model=List[PostResponse])
def list_posts(limit: int = 20, db: Session = Depends(get_session)):
    """Get recent published posts."""
    posts = (
        db.query(TruthPost)
        .filter(TruthPost.published == True)
        .order_by(TruthPost.created_at.desc())
        .limit(limit)
        .all()
    )
    
    return [
        PostResponse(
            id=p.id,
            author_id=p.author_id,
            title=p.title,
            content=p.content,
            tags=p.tags,
            citations=p.citations,
            published=p.published,
            trust_score=p.trust_score,
            created_at=p.created_at.isoformat(),
        )
        for p in posts
    ]


@router.get("/threads", response_model=List[ThreadResponse])
def list_threads(limit: int = 20, db: Session = Depends(get_session)):
    """Get recent discussion threads."""
    threads = (
        db.query(TruthThread)
        .order_by(TruthThread.created_at.desc())
        .limit(limit)
        .all()
    )
    return threads


@router.get("/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_session)):
    """Get a specific post."""
    post = db.query(TruthPost).filter(TruthPost.id == post_id).first()
    if not post:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Post not found")
    
    return PostResponse(
        id=post.id,
        author_id=post.author_id,
        title=post.title,
        content=post.content,
        tags=post.tags,
        citations=post.citations,
        published=post.published,
        trust_score=post.trust_score,
        created_at=post.created_at.isoformat(),
    )
