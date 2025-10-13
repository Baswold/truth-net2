from datetime import datetime
from typing import Annotated, List

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session, selectinload

from ..auth import get_current_active_user
from ..database import get_session
from ..models import Member, TruthPost, TruthThread
from ..services.social import (
    aggregate_hashtags,
    build_post_insights,
    build_thread_health,
)
from ..services.feed_filter import feed_filter_service

router = APIRouter(prefix="/social", tags=["social"])


def _velocity_score(post: TruthPost) -> float:
    now = datetime.utcnow()
    reference = post.published_at or post.created_at
    hours_old = max((now - reference).total_seconds() / 3600.0, 1.0)
    return round((post.trust_score + 1) / hours_old, 3)


class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    author_id: int
    title: str | None
    content: str
    tags: dict
    citations: dict
    published: bool
    trust_score: int
    created_at: str
    velocity_score: float


class ThreadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    post_id: int | None
    creator_id: int
    title: str
    topic: str | None
    locked: bool
    trust_score: int


class PostInsightResponse(BaseModel):
    post_id: int
    title: str | None
    trust_score: int
    velocity_score: float
    top_tags: List[str]


class ThreadInsightResponse(BaseModel):
    thread_id: int
    title: str
    comment_count: int
    trust_balance: float


class TagStat(BaseModel):
    tag: str
    count: int


class SocialInsightsResponse(BaseModel):
    trending_posts: List[PostInsightResponse]
    lively_threads: List[ThreadInsightResponse]
    top_tags: List[TagStat]


@router.get("/posts", response_model=List[PostResponse])
def list_posts(
    limit: int = Query(20, le=100, description="Number of posts to return"),
    offset: int = Query(0, ge=0, description="Number of posts to skip"),
    db: Session = Depends(get_session)
):
    """Get recent published posts with pagination."""
    posts = (
        db.query(TruthPost)
        .filter(TruthPost.published.is_(True))
        .order_by(TruthPost.created_at.desc())
        .offset(offset)
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
            velocity_score=_velocity_score(p),
        )
        for p in posts
    ]


@router.get("/threads", response_model=List[ThreadResponse])
def list_threads(
    limit: int = Query(20, le=100, description="Number of threads to return"),
    offset: int = Query(0, ge=0, description="Number of threads to skip"),
    db: Session = Depends(get_session)
):
    """Get recent discussion threads with pagination."""
    threads = (
        db.query(TruthThread)
        .order_by(TruthThread.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return threads


@router.get("/feed/personalized", response_model=List[PostResponse])
def get_personalized_feed(
    limit: int = Query(20, le=100, description="Number of posts to return"),
    offset: int = Query(0, ge=0, description="Number of posts to skip"),
    current_user: Annotated[Member, Depends(get_current_active_user)],
    db: Session = Depends(get_session)
):
    """
    Get personalized feed based on user's preferences.
    
    Returns posts filtered and ranked according to your feed preferences.
    If no preferences are set, returns the default feed (all published posts).
    
    To set preferences, use POST /v1/feed-preferences/me
    """
    posts = feed_filter_service.get_personalized_feed(
        member_id=current_user.id,
        db=db,
        limit=limit,
        offset=offset
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
            velocity_score=_velocity_score(p),
        )
        for p in posts
    ]


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
        velocity_score=_velocity_score(post),
    )


@router.get("/insights", response_model=SocialInsightsResponse)
def get_social_insights(limit: int = 20, db: Session = Depends(get_session)):
    """Expose aggregated social metrics for curation and discovery."""

    posts = (
        db.query(TruthPost)
        .filter(TruthPost.published.is_(True))
        .order_by(TruthPost.created_at.desc())
        .limit(limit)
        .all()
    )

    threads = (
        db.query(TruthThread)
        .options(selectinload(TruthThread.comments))
        .order_by(TruthThread.created_at.desc())
        .limit(limit)
        .all()
    )

    post_insights = [PostInsightResponse(**insight.to_dict()) for insight in build_post_insights(posts)]
    thread_health = [
        ThreadInsightResponse(**insight.to_dict()) for insight in build_thread_health(threads)
    ]
    tag_stats = [
        TagStat(tag=tag, count=count) for tag, count in aggregate_hashtags(posts)
    ]

    return SocialInsightsResponse(
        trending_posts=post_insights,
        lively_threads=thread_health,
        top_tags=tag_stats,
    )
