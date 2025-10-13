"""User feed preference models for personalized content curation."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class FeedPreference(Base, TimestampMixin):
    """
    User feed preferences for personalized content filtering.
    
    Allows users to describe what they want/don't want to see in natural language.
    Preferences are parsed into structured filters that affect feed ranking.
    """
    __tablename__ = "feed_preference"
    __table_args__ = (
        Index("ix_feed_preference_member_id", "member_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("member.id", ondelete="CASCADE"), unique=True)
    
    # User's natural language preferences
    prompt: Mapped[str] = mapped_column(Text)
    
    # Parsed preference structure
    # Example: {
    #   "interests": ["science", "technology", "climate"],
    #   "exclude_topics": ["politics", "sports"],
    #   "preferred_authors": [123, 456],
    #   "exclude_authors": [789],
    #   "min_trust_score": 5,
    #   "content_types": ["article", "analysis"],
    #   "keywords_include": ["research", "data"],
    #   "keywords_exclude": ["rumor", "unverified"]
    # }
    parsed_filters: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Additional metadata
    last_applied_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    active: Mapped[bool] = mapped_column(default=True)
    
    member = relationship("Member", back_populates="feed_preference")
