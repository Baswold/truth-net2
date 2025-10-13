from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class MemberRole(str, Enum):  # type: ignore[type-arg]
    MEMBER = "member"
    CURATOR = "curator"
    ADMIN = "admin"


class Member(Base):
    __tablename__ = "member"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(120))
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    password_hash: Mapped[str] = mapped_column(String(255))
    roles: Mapped[str] = mapped_column(String(120), default=MemberRole.MEMBER.value)
    trust_score: Mapped[int] = mapped_column(Integer, default=0)
    strike_count: Mapped[int] = mapped_column(Integer, default=0)
    public_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    avatar_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    timezone: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    sites = relationship("Site", back_populates="owner")
    posts = relationship("TruthPost", back_populates="author")
    threads = relationship("TruthThread", back_populates="creator")
    feed_preference = relationship("FeedPreference", back_populates="member", uselist=False)

    __mapper_args__ = {"eager_defaults": True}
