from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class FactCheckRun(Base, TimestampMixin):
    __tablename__ = "fact_check_run"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    target_type: Mapped[str] = mapped_column(String(32))  # page, post, import
    target_id: Mapped[int] = mapped_column(Integer)
    
    primary_checker_result: Mapped[dict] = mapped_column(JSON, default=dict)
    auditor_checker_result: Mapped[dict] = mapped_column(JSON, default=dict)
    
    agreement_score: Mapped[Optional[float]] = mapped_column(nullable=True)
    final_verdict: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    web_search_queries: Mapped[dict] = mapped_column(JSON, default=dict)
    web_search_results: Mapped[dict] = mapped_column(JSON, default=dict)
    
    curator_reviewed: Mapped[bool] = mapped_column(default=False)
    reviewer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("member.id", ondelete="SET NULL"), nullable=True)
    reviewer_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    reviewer = relationship("Member")
    assertions = relationship("TruthAssertion", back_populates="fact_check_run")


class ImportSource(Base, TimestampMixin):
    __tablename__ = "import_source"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    original_url: Mapped[str] = mapped_column(Text)
    snapshot_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    checksum: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    
    refresh_interval_hours: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    last_refresh_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    next_refresh_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    status: Mapped[str] = mapped_column(String(32), default="pending")
    import_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    
    submitted_by: Mapped[int] = mapped_column(ForeignKey("member.id", ondelete="SET NULL"), nullable=True)
    page_id: Mapped[Optional[int]] = mapped_column(ForeignKey("page.id", ondelete="CASCADE"), nullable=True)

    submitter = relationship("Member")
    page = relationship("Page")


class SiteMembership(Base, TimestampMixin):
    __tablename__ = "site_membership"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("site.id", ondelete="CASCADE"))
    member_id: Mapped[int] = mapped_column(ForeignKey("member.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(32), default="contributor")
    
    site = relationship("Site", back_populates="memberships")
    member = relationship("Member")


class FeatureToggle(Base, TimestampMixin):
    __tablename__ = "feature_toggle"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scope: Mapped[str] = mapped_column(String(32), default="global")  # global, site, member
    scope_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    key: Mapped[str] = mapped_column(String(120))
    value: Mapped[str] = mapped_column(Text)
    value_type: Mapped[str] = mapped_column(String(32), default="boolean")
    
    updated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("member.id", ondelete="SET NULL"), nullable=True)

    updater = relationship("Member")
