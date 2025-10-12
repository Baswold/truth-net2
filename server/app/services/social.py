"""High-level social feed intelligence helpers."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Sequence

from ..models import TruthPost, TruthThread


@dataclass(slots=True)
class PostInsight:
    post_id: int
    title: str | None
    trust_score: int
    velocity_score: float
    top_tags: list[str]

    def to_dict(self) -> dict:
        return {
            "post_id": self.post_id,
            "title": self.title,
            "trust_score": self.trust_score,
            "velocity_score": self.velocity_score,
            "top_tags": self.top_tags,
        }


@dataclass(slots=True)
class ConversationInsight:
    thread_id: int
    title: str
    comment_count: int
    trust_balance: float

    def to_dict(self) -> dict:
        return {
            "thread_id": self.thread_id,
            "title": self.title,
            "comment_count": self.comment_count,
            "trust_balance": self.trust_balance,
        }


def _tag_list(tags: dict | None) -> list[str]:
    if not tags:
        return []
    return [tag for tag in tags.keys() if isinstance(tag, str)]


def build_post_insights(posts: Sequence[TruthPost], *, now: datetime | None = None) -> list[PostInsight]:
    now = now or datetime.utcnow()
    insights: list[PostInsight] = []

    for post in posts:
        published_at = post.published_at or post.created_at
        hours_old = max((now - published_at).total_seconds() / 3600.0, 1.0)
        velocity = (post.trust_score + 1) / hours_old
        top_tags = _tag_list(post.tags)[:5]

        insights.append(
            PostInsight(
                post_id=post.id,
                title=post.title,
                trust_score=post.trust_score,
                velocity_score=round(velocity, 3),
                top_tags=top_tags,
            )
        )

    return sorted(
        insights,
        key=lambda item: (item.trust_score, item.velocity_score),
        reverse=True,
    )


def build_thread_health(threads: Iterable[TruthThread]) -> list[ConversationInsight]:
    insights: list[ConversationInsight] = []

    for thread in threads:
        comment_count = len(thread.comments)
        if comment_count:
            trust_values = [comment.trust_score for comment in thread.comments]
            balance = sum(trust_values) / (comment_count * 10)
        else:
            balance = 0.0

        insights.append(
            ConversationInsight(
                thread_id=thread.id,
                title=thread.title,
                comment_count=comment_count,
                trust_balance=round(balance, 3),
            )
        )

    return sorted(
        insights,
        key=lambda insight: (insight.trust_balance, insight.comment_count),
        reverse=True,
    )


def aggregate_hashtags(posts: Iterable[TruthPost]) -> list[tuple[str, int]]:
    counter: Counter[str] = Counter()
    for post in posts:
        for tag in _tag_list(post.tags):
            counter[tag] += 1
    return counter.most_common(10)
