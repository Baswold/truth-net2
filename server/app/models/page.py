from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class PageStatus(str, Enum):  # type: ignore[type-arg]
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Page(Base, TimestampMixin):
    __tablename__ = "page"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("site.id", ondelete="CASCADE"))
    path: Mapped[str] = mapped_column(String(512))
    title: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32), default=PageStatus.DRAFT.value)

    layout_json: Mapped[dict] = mapped_column(JSON, default=dict)
    page_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    
    live_version_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    site = relationship("Site", back_populates="pages")
    versions = relationship("ContentVersion", back_populates="page", cascade="all, delete-orphan")
    assertions = relationship("TruthAssertion", back_populates="page", cascade="all, delete-orphan")


class ContentVersion(Base, TimestampMixin):
    __tablename__ = "content_version"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    page_id: Mapped[int] = mapped_column(ForeignKey("page.id", ondelete="CASCADE"))
    version_number: Mapped[int] = mapped_column(Integer, default=1)
    layout_json: Mapped[dict] = mapped_column(JSON)
    editor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("member.id", ondelete="SET NULL"), nullable=True)
    
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    change_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    page = relationship("Page", back_populates="versions")
    editor = relationship("Member")


class TruthAssertion(Base, TimestampMixin):
    __tablename__ = "truth_assertion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    page_id: Mapped[int] = mapped_column(ForeignKey("page.id", ondelete="CASCADE"))
    claim_text: Mapped[str] = mapped_column(Text)
    verdict: Mapped[str] = mapped_column(String(64))
    citation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fact_check_run_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("fact_check_run.id", ondelete="SET NULL"), nullable=True
    )

    page = relationship("Page", back_populates="assertions")
    fact_check_run = relationship("FactCheckRun", back_populates="assertions")
