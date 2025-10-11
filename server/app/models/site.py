from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class SiteStatus(str, Enum):  # type: ignore[type-arg]
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Site(Base, TimestampMixin):
    __tablename__ = "site"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    theme: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    status: Mapped[str] = mapped_column(String(32), default=SiteStatus.DRAFT.value)
    feature_flags: Mapped[dict] = mapped_column(JSON, default=dict)

    owner_id: Mapped[int] = mapped_column(ForeignKey("member.id", ondelete="SET NULL"), nullable=True)
    owner: Mapped[Optional["Member"]] = relationship("Member", back_populates="sites")

    primary_language: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    pages: Mapped[List["Page"]] = relationship("Page", back_populates="site", cascade="all, delete-orphan")
    memberships: Mapped[List["SiteMembership"]] = relationship(
        "SiteMembership", back_populates="site", cascade="all, delete-orphan"
    )
