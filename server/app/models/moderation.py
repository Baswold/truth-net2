from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class Submission(Base, TimestampMixin):
    __tablename__ = "submission"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    submission_type: Mapped[str] = mapped_column(String(32))  # new_site, page_update, import, post
    submitted_by: Mapped[int] = mapped_column(ForeignKey("member.id", ondelete="CASCADE"))
    
    payload: Mapped[dict] = mapped_column(JSON)
    state: Mapped[str] = mapped_column(String(32), default="pending")  # pending, approved, rejected
    
    priority: Mapped[int] = mapped_column(Integer, default=0)
    submission_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict)

    submitter = relationship("Member")
    reviews = relationship("ReviewAction", back_populates="submission", cascade="all, delete-orphan")


class ReviewAction(Base, TimestampMixin):
    __tablename__ = "review_action"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("submission.id", ondelete="CASCADE"))
    reviewer_id: Mapped[int] = mapped_column(ForeignKey("member.id", ondelete="CASCADE"))
    
    decision: Mapped[str] = mapped_column(String(32))  # approve, reject, needs_revision
    rationale: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    penalties: Mapped[dict] = mapped_column(JSON, default=dict)
    
    reviewed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    submission = relationship("Submission", back_populates="reviews")
    reviewer = relationship("Member")


class PenaltyLedger(Base, TimestampMixin):
    __tablename__ = "penalty_ledger"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("member.id", ondelete="CASCADE"))
    penalty_type: Mapped[str] = mapped_column(String(64))  # strike, fine, suspension
    amount: Mapped[Optional[float]] = mapped_column(nullable=True)
    
    reason: Mapped[str] = mapped_column(Text)
    resolved: Mapped[bool] = mapped_column(default=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    issued_by: Mapped[Optional[int]] = mapped_column(ForeignKey("member.id", ondelete="SET NULL"), nullable=True)

    member = relationship("Member", foreign_keys=[member_id])
    issuer = relationship("Member", foreign_keys=[issued_by])


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("member.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str] = mapped_column(String(120))
    target_type: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    target_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    ip_address: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    actor = relationship("Member")
