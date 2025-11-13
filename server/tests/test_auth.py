from __future__ import annotations

from app.models import Member


def test_signup_creates_new_user(client, session):
    """Test that signup creates a new user and returns tokens."""
    signup_data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "display_name": "New User",
        "password": "SecurePass123!",
    }

    response = client.post("/v1/auth/signup", json=signup_data)
    assert response.status_code == 200

    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["expires_in"] == 3600

    # Verify user was created in database
    member = session.query(Member).filter(Member.email == "newuser@example.com").first()
    assert member is not None
    assert member.username == "newuser"
    assert member.display_name == "New User"
    assert member.roles == "member"
    assert member.trust_score == 0


def test_signup_duplicate_email(client, session):
    """Test that signup fails with duplicate email."""
    member = Member(
        email="existing@example.com",
        username="existing",
        display_name="Existing User",
        password_hash="hashed",
    )
    session.add(member)
    session.commit()

    signup_data = {
        "email": "existing@example.com",
        "username": "newuser",
        "display_name": "New User",
        "password": "SecurePass123!",
    }

    response = client.post("/v1/auth/signup", json=signup_data)
    assert response.status_code == 400
    assert "Registration failed" in response.json()["detail"]


def test_signup_duplicate_username(client, session):
    """Test that signup fails with duplicate username."""
    member = Member(
        email="existing@example.com",
        username="existing",
        display_name="Existing User",
        password_hash="hashed",
    )
    session.add(member)
    session.commit()

    signup_data = {
        "email": "newuser@example.com",
        "username": "existing",
        "display_name": "New User",
        "password": "SecurePass123!",
    }

    response = client.post("/v1/auth/signup", json=signup_data)
    assert response.status_code == 400
    assert "Registration failed" in response.json()["detail"]


def test_login_with_email(client, session):
    """Test login with email."""
    from app.auth import hash_password

    member = Member(
        email="user@example.com",
        username="testuser",
        display_name="Test User",
        password_hash=hash_password("MyPassword123!"),
    )
    session.add(member)
    session.commit()

    login_data = {
        "email_or_username": "user@example.com",
        "password": "MyPassword123!",
    }

    response = client.post("/v1/auth/login", json=login_data)
    assert response.status_code == 200

    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body


def test_login_with_username(client, session):
    """Test login with username."""
    from app.auth import hash_password

    member = Member(
        email="user@example.com",
        username="testuser",
        display_name="Test User",
        password_hash=hash_password("MyPassword123!"),
    )
    session.add(member)
    session.commit()

    login_data = {
        "email_or_username": "testuser",
        "password": "MyPassword123!",
    }

    response = client.post("/v1/auth/login", json=login_data)
    assert response.status_code == 200

    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body


def test_login_wrong_password(client, session):
    """Test login fails with wrong password."""
    from app.auth import hash_password

    member = Member(
        email="user@example.com",
        username="testuser",
        display_name="Test User",
        password_hash=hash_password("MyPassword123!"),
    )
    session.add(member)
    session.commit()

    login_data = {
        "email_or_username": "user@example.com",
        "password": "WrongPassword",
    }

    response = client.post("/v1/auth/login", json=login_data)
    assert response.status_code == 401
    assert "Incorrect email/username or password" in response.json()["detail"]


def test_login_nonexistent_user(client, session):
    """Test login fails for nonexistent user."""
    login_data = {
        "email_or_username": "nonexistent@example.com",
        "password": "AnyPassword",
    }

    response = client.post("/v1/auth/login", json=login_data)
    assert response.status_code == 401


def test_get_profile_authenticated(client, session):
    """Test getting profile when authenticated."""
    from app.auth import create_access_token, hash_password

    member = Member(
        email="user@example.com",
        username="testuser",
        display_name="Test User",
        password_hash=hash_password("password"),
        bio="Test bio",
        trust_score=5,
        roles="member,curator",
    )
    session.add(member)
    session.commit()

    # Create token for this user
    token = create_access_token(data={"sub": str(member.id), "username": member.username})

    response = client.get(
        "/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    body = response.json()
    assert body["id"] == member.id
    assert body["email"] == "user@example.com"
    assert body["username"] == "testuser"
    assert body["display_name"] == "Test User"
    assert body["bio"] == "Test bio"
    assert body["trust_score"] == 5
    assert body["roles"] == "member,curator"


def test_get_profile_unauthenticated(client):
    """Test getting profile without authentication fails."""
    response = client.get("/v1/auth/me")
    assert response.status_code in [401, 403]  # Either unauthorized or forbidden is acceptable


def test_get_profile_invalid_token(client):
    """Test getting profile with invalid token fails."""
    response = client.get(
        "/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
