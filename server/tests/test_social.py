from __future__ import annotations

from datetime import datetime, timedelta

from app.models import Member, ThreadComment, TruthPost, TruthThread


def test_social_insights_endpoint(client, session):
    now = datetime.utcnow()
    member = Member(
        email="poster@example.com",
        username="poster",
        display_name="Poster",
        password_hash="hashed",
    )
    session.add(member)
    session.flush()

    post = TruthPost(
        author=member,
        content="Evidence confirmed by official sources.",
        published=True,
        trust_score=9,
        tags={"news": True, "science": True},
    )
    post.created_at = now - timedelta(hours=4)
    post.published_at = now - timedelta(hours=4)

    other_post = TruthPost(
        author=member,
        content="Preliminary report awaiting verification.",
        published=True,
        trust_score=4,
        tags={"update": True},
    )
    other_post.created_at = now - timedelta(hours=1)
    other_post.published_at = now - timedelta(hours=1)

    thread = TruthThread(
        creator=member,
        title="Discussing new findings",
        topic="science",
        trust_score=5,
    )
    thread.created_at = now - timedelta(hours=2)

    comment = ThreadComment(
        thread=thread,
        author=member,
        content="Supporting data looks solid.",
        trust_score=6,
    )

    session.add_all([post, other_post, thread, comment])
    session.commit()

    response = client.get("/v1/social/insights")
    assert response.status_code == 200
    data = response.json()

    assert data["trending_posts"][0]["velocity_score"] > 0
    assert data["lively_threads"][0]["comment_count"] >= 1
    assert any(tag_stat["tag"] == "news" for tag_stat in data["top_tags"])
