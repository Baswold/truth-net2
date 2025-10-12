from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class TruthPost(Base, TimestampMixin):
    __tablename__ = "truth_post"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("member.id", ondelete="CASCADE"))
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    content_type: Mapped[str] = mapped_column(String(32), default="markdown")
    
    tags: Mapped[dict] = mapped_column(JSON, default=dict)
    citations: Mapped[dict] = mapped_column(JSON, default=dict)
    extra_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    
    published: Mapped[bool] = mapped_column(default=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    trust_score: Mapped[int] = mapped_column(Integer, default=0)

    author = relationship("Member", back_populates="posts")
    threads = relationship("TruthThread", back_populates="post", cascade="all, delete-orphan")
    reactions = relationship("Reaction", back_populates="post", cascade="all, delete-orphan")


class TruthThread(Base, TimestampMixin):
    __tablename__ = "truth_thread"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[Optional[int]] = mapped_column(ForeignKey("truth_post.id", ondelete="CASCADE"), nullable=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("member.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    topic: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    
    locked: Mapped[bool] = mapped_column(default=False)
    trust_score: Mapped[int] = mapped_column(Integer, default=0)

    post = relationship("TruthPost", back_populates="threads")
    creator = relationship("Member", back_populates="threads")
    comments = relationship("ThreadComment", back_populates="thread", cascade="all, delete-orphan")


class ThreadComment(Base, TimestampMixin):
    __tablename__ = "thread_comment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    thread_id: Mapped[int] = mapped_column(ForeignKey("truth_thread.id", ondelete="CASCADE"))
    author_id: Mapped[int] = mapped_column(ForeignKey("member.id", ondelete="CASCADE"))
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("thread_comment.id", ondelete="CASCADE"), nullable=True
    )
    
    content: Mapped[str] = mapped_column(Text)
    citations: Mapped[dict] = mapped_column(JSON, default=dict)
    trust_score: Mapped[int] = mapped_column(Integer, default=0)

    thread = relationship("TruthThread", back_populates="comments")
    author = relationship("Member")
    parent = relationship("ThreadComment", remote_side=[id])


class Reaction(Base, TimestampMixin):
    __tablename__ = "reaction"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("member.id", ondelete="CASCADE"))
    post_id: Mapped[Optional[int]] = mapped_column(ForeignKey("truth_post.id", ondelete="CASCADE"), nullable=True)
    comment_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("thread_comment.id", ondelete="CASCADE"), nullable=True
    )
    
    reaction_type: Mapped[str] = mapped_column(String(32))  # verified, helpful, needs_review, etc.
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    member = relationship("Member")
    post = relationship("TruthPost", back_populates="reactions")


class Follow(Base, TimestampMixin):
    __tablename__ = "follow"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    follower_id: Mapped[int] = mapped_column(ForeignKey("member.id", ondelete="CASCADE"))
    following_id: Mapped[int] = mapped_column(ForeignKey("member.id", ondelete="CASCADE"))
    
    follower = relationship("Member", foreign_keys=[follower_id])
    following = relationship("Member", foreign_keys=[following_id])


class CommunityVerdict(Base, TimestampMixin):
    __tablename__ = "community_verdict"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    target_type: Mapped[str] = mapped_column(String(32))  # post, comment, page
    target_id: Mapped[int] = mapped_column(Integer)
    
    verdict: Mapped[str] = mapped_column(String(64))  # verified, disputed, misleading
    vote_count: Mapped[int] = mapped_column(Integer, default=0)
    curator_approved: Mapped[bool] = mapped_column(default=False)
    evidence: Mapped[dict] = mapped_column(JSON, default=dict)
