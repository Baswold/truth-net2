from __future__ import annotations

from app.auth import create_access_token, hash_password
from app.models import FeedPreference, Member


def test_preview_preferences(client, session):
    """Test previewing feed preferences before saving."""
    member = Member(
        email="user@example.com",
        username="user1",
        display_name="User",
        password_hash=hash_password("password"),
    )
    session.add(member)
    session.commit()

    token = create_access_token(data={"sub": str(member.id), "username": member.username})

    preview_data = {
        "prompt": "Show me science and technology posts, but no politics"
    }

    response = client.post(
        "/v1/feed-preferences/preview",
        json=preview_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["prompt"] == preview_data["prompt"]
    assert "parsed_filters" in body
    assert "explanation" in body
    assert len(body["explanation"]) > 0


def test_create_feed_preferences(client, session):
    """Test creating feed preferences."""
    member = Member(
        email="user@example.com",
        username="user1",
        display_name="User",
        password_hash=hash_password("password"),
    )
    session.add(member)
    session.commit()

    token = create_access_token(data={"sub": str(member.id), "username": member.username})

    preference_data = {
        "prompt": "Show me verified posts about climate change"
    }

    response = client.post(
        "/v1/feed-preferences/me",
        json=preference_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["prompt"] == preference_data["prompt"]
    assert body["member_id"] == member.id
    assert body["active"] is True
    assert "parsed_filters" in body

    # Verify it was saved to database
    pref = session.query(FeedPreference).filter(FeedPreference.member_id == member.id).first()
    assert pref is not None
    assert pref.prompt == preference_data["prompt"]


def test_get_feed_preferences(client, session):
    """Test getting user's feed preferences."""
    member = Member(
        email="user@example.com",
        username="user1",
        display_name="User",
        password_hash=hash_password("password"),
    )
    session.add(member)
    session.flush()

    preference = FeedPreference(
        member_id=member.id,
        prompt="Show me tech news",
        parsed_filters={"interests": ["technology"]},
        active=True,
    )
    session.add(preference)
    session.commit()

    token = create_access_token(data={"sub": str(member.id), "username": member.username})

    response = client.get(
        "/v1/feed-preferences/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["prompt"] == "Show me tech news"
    assert body["active"] is True


def test_get_feed_preferences_none(client, session):
    """Test getting preferences when none exist."""
    member = Member(
        email="user@example.com",
        username="user1",
        display_name="User",
        password_hash=hash_password("password"),
    )
    session.add(member)
    session.commit()

    token = create_access_token(data={"sub": str(member.id), "username": member.username})

    response = client.get(
        "/v1/feed-preferences/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json() is None


def test_update_feed_preferences(client, session):
    """Test updating existing feed preferences."""
    member = Member(
        email="user@example.com",
        username="user1",
        display_name="User",
        password_hash=hash_password("password"),
    )
    session.add(member)
    session.flush()

    # Create initial preference
    preference = FeedPreference(
        member_id=member.id,
        prompt="Show me tech news",
        parsed_filters={"interests": ["technology"]},
        active=True,
    )
    session.add(preference)
    session.commit()

    token = create_access_token(data={"sub": str(member.id), "username": member.username})

    # Update using POST (upsert)
    update_data = {
        "prompt": "Show me science news instead"
    }

    response = client.post(
        "/v1/feed-preferences/me",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["prompt"] == "Show me science news instead"

    # Verify database was updated
    session.refresh(preference)
    assert preference.prompt == "Show me science news instead"


def test_patch_feed_preferences(client, session):
    """Test partial update of feed preferences."""
    member = Member(
        email="user@example.com",
        username="user1",
        display_name="User",
        password_hash=hash_password("password"),
    )
    session.add(member)
    session.flush()

    preference = FeedPreference(
        member_id=member.id,
        prompt="Show me tech news",
        parsed_filters={"interests": ["technology"]},
        active=True,
    )
    session.add(preference)
    session.commit()

    token = create_access_token(data={"sub": str(member.id), "username": member.username})

    # Disable preferences without changing prompt
    update_data = {
        "active": False
    }

    response = client.patch(
        "/v1/feed-preferences/me",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["active"] is False
    assert body["prompt"] == "Show me tech news"  # Prompt unchanged


def test_patch_feed_preferences_not_found(client, session):
    """Test patching when preferences don't exist."""
    member = Member(
        email="user@example.com",
        username="user1",
        display_name="User",
        password_hash=hash_password("password"),
    )
    session.add(member)
    session.commit()

    token = create_access_token(data={"sub": str(member.id), "username": member.username})

    update_data = {
        "active": False
    }

    response = client.patch(
        "/v1/feed-preferences/me",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_delete_feed_preferences(client, session):
    """Test deleting feed preferences."""
    member = Member(
        email="user@example.com",
        username="user1",
        display_name="User",
        password_hash=hash_password("password"),
    )
    session.add(member)
    session.flush()

    preference = FeedPreference(
        member_id=member.id,
        prompt="Show me tech news",
        parsed_filters={"interests": ["technology"]},
        active=True,
    )
    session.add(preference)
    session.commit()

    token = create_access_token(data={"sub": str(member.id), "username": member.username})

    response = client.delete(
        "/v1/feed-preferences/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 204

    # Verify it was deleted
    pref = session.query(FeedPreference).filter(FeedPreference.member_id == member.id).first()
    assert pref is None


def test_delete_feed_preferences_not_found(client, session):
    """Test deleting when preferences don't exist (should succeed)."""
    member = Member(
        email="user@example.com",
        username="user1",
        display_name="User",
        password_hash=hash_password("password"),
    )
    session.add(member)
    session.commit()

    token = create_access_token(data={"sub": str(member.id), "username": member.username})

    response = client.delete(
        "/v1/feed-preferences/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    # Should succeed even if nothing to delete
    assert response.status_code == 204


def test_feed_preferences_require_authentication(client):
    """Test that all feed preference endpoints require authentication."""
    endpoints = [
        ("POST", "/v1/feed-preferences/preview", {"prompt": "test"}),
        ("GET", "/v1/feed-preferences/me", None),
        ("POST", "/v1/feed-preferences/me", {"prompt": "test"}),
        ("PATCH", "/v1/feed-preferences/me", {"active": False}),
        ("DELETE", "/v1/feed-preferences/me", None),
    ]

    for method, path, data in endpoints:
        if method == "GET":
            response = client.get(path)
        elif method == "POST":
            response = client.post(path, json=data)
        elif method == "PATCH":
            response = client.patch(path, json=data)
        elif method == "DELETE":
            response = client.delete(path)

        assert response.status_code in [401, 403], f"{method} {path} should require authentication"
