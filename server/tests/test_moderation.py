from __future__ import annotations

from datetime import datetime

from app.auth import create_access_token, hash_password
from app.models import Member, ReviewAction, Submission


def test_list_submissions_as_curator(client, session):
    """Test that curators can list submissions."""
    curator = Member(
        email="curator@example.com",
        username="curator1",
        display_name="Curator",
        password_hash=hash_password("password"),
        roles="curator",
    )
    session.add(curator)
    session.flush()

    # Create some submissions
    submission1 = Submission(
        submission_type="content",
        submitted_by=curator.id,
        payload={"content": "Test content 1"},
        state="pending",
        priority=5,
    )
    submission2 = Submission(
        submission_type="content",
        submitted_by=curator.id,
        payload={"content": "Test content 2"},
        state="pending",
        priority=3,
    )
    session.add_all([submission1, submission2])
    session.commit()

    # Get submissions as curator
    token = create_access_token(data={"sub": str(curator.id), "username": curator.username})
    response = client.get(
        "/v1/moderation/submissions",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    submissions = response.json()
    assert len(submissions) >= 2
    # Should be ordered by priority desc, then created_at asc
    assert submissions[0]["priority"] >= submissions[1]["priority"]


def test_list_submissions_as_admin(client, session):
    """Test that admins can list submissions."""
    admin = Member(
        email="admin@example.com",
        username="admin1",
        display_name="Admin",
        password_hash=hash_password("password"),
        roles="admin",
    )
    session.add(admin)
    session.flush()

    submission = Submission(
        submission_type="content",
        submitted_by=admin.id,
        payload={"content": "Test content"},
        state="pending",
        priority=5,
    )
    session.add(submission)
    session.commit()

    # Get submissions as admin
    token = create_access_token(data={"sub": str(admin.id), "username": admin.username})
    response = client.get(
        "/v1/moderation/submissions",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    submissions = response.json()
    assert len(submissions) >= 1


def test_list_submissions_as_member_fails(client, session):
    """Test that regular members cannot list submissions."""
    member = Member(
        email="member@example.com",
        username="member1",
        display_name="Member",
        password_hash=hash_password("password"),
        roles="member",
    )
    session.add(member)
    session.commit()

    token = create_access_token(data={"sub": str(member.id), "username": member.username})
    response = client.get(
        "/v1/moderation/submissions",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403


def test_list_submissions_filter_by_state(client, session):
    """Test filtering submissions by state."""
    curator = Member(
        email="curator@example.com",
        username="curator1",
        display_name="Curator",
        password_hash=hash_password("password"),
        roles="curator",
    )
    session.add(curator)
    session.flush()

    pending_sub = Submission(
        submission_type="content",
        submitted_by=curator.id,
        payload={"content": "Pending"},
        state="pending",
        priority=5,
    )
    approved_sub = Submission(
        submission_type="content",
        submitted_by=curator.id,
        payload={"content": "Approved"},
        state="approved",
        priority=5,
    )
    session.add_all([pending_sub, approved_sub])
    session.commit()

    token = create_access_token(data={"sub": str(curator.id), "username": curator.username})

    # Get only approved submissions
    response = client.get(
        "/v1/moderation/submissions?state=approved",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    submissions = response.json()
    assert all(s["state"] == "approved" for s in submissions)


def test_get_submission_reviews(client, session):
    """Test getting reviews for a submission."""
    curator = Member(
        email="curator@example.com",
        username="curator1",
        display_name="Curator",
        password_hash=hash_password("password"),
        roles="curator",
    )
    session.add(curator)
    session.flush()

    submission = Submission(
        submission_type="content",
        submitted_by=curator.id,
        payload={"content": "Test"},
        state="pending",
        priority=5,
    )
    session.add(submission)
    session.flush()

    review = ReviewAction(
        submission_id=submission.id,
        reviewer_id=curator.id,
        decision="approve",
        rationale="Looks good",
        reviewed_at=datetime.utcnow(),
    )
    session.add(review)
    session.commit()

    token = create_access_token(data={"sub": str(curator.id), "username": curator.username})
    response = client.get(
        f"/v1/moderation/submissions/{submission.id}/reviews",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    reviews = response.json()
    assert len(reviews) == 1
    assert reviews[0]["decision"] == "approve"
    assert reviews[0]["rationale"] == "Looks good"
    assert reviews[0]["reviewer_id"] == curator.id


def test_get_submission_reviews_unauthorized(client, session):
    """Test that non-curators cannot get reviews."""
    member = Member(
        email="member@example.com",
        username="member1",
        display_name="Member",
        password_hash=hash_password("password"),
        roles="member",
    )
    session.add(member)
    session.commit()

    token = create_access_token(data={"sub": str(member.id), "username": member.username})
    response = client.get(
        "/v1/moderation/submissions/1/reviews",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403
