"""API endpoints for managing personalized feed preferences."""
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import get_current_active_user
from ..database import get_session
from ..models import FeedPreference, Member
from ..schemas.feed_preference import (
    FeedPreferenceCreate,
    FeedPreferencePreview,
    FeedPreferenceResponse,
    FeedPreferenceUpdate,
    ParsedFilters,
)
from ..services.feed_filter import feed_filter_service

router = APIRouter(prefix="/feed-preferences", tags=["feed-preferences"])


@router.post("/preview", response_model=FeedPreferencePreview)
def preview_preferences(
    preference: FeedPreferenceCreate,
    current_user: Annotated[Member, Depends(get_current_active_user)],
):
    """
    Preview how a prompt will be parsed into filters without saving.
    
    Use this to test and refine your preference prompt before applying it.
    """
    parsed = feed_filter_service.parse_prompt(preference.prompt)
    
    # Generate human-readable explanation
    explanations = []
    
    if parsed.get("interests"):
        explanations.append(f"✅ Include posts about: {', '.join(parsed['interests'])}")
    
    if parsed.get("exclude_topics"):
        explanations.append(f"❌ Exclude posts about: {', '.join(parsed['exclude_topics'])}")
    
    if parsed.get("min_trust_score") is not None:
        explanations.append(f"⭐ Minimum trust score: {parsed['min_trust_score']}")
    
    if parsed.get("require_verified"):
        explanations.append("✓ Show only verified posts")
    
    if not explanations:
        explanations.append("No filters detected. Feed will show all posts.")
    
    return FeedPreferencePreview(
        prompt=preference.prompt,
        parsed_filters=ParsedFilters(**parsed),
        explanation="\n".join(explanations)
    )


@router.get("/me", response_model=FeedPreferenceResponse | None)
def get_my_preferences(
    current_user: Annotated[Member, Depends(get_current_active_user)],
    db: Session = Depends(get_session),
):
    """Get current user's feed preferences."""
    preference = db.query(FeedPreference).filter(
        FeedPreference.member_id == current_user.id
    ).first()
    
    return preference


@router.post("/me", response_model=FeedPreferenceResponse, status_code=201)
def create_or_update_preferences(
    preference_data: FeedPreferenceCreate,
    current_user: Annotated[Member, Depends(get_current_active_user)],
    db: Session = Depends(get_session),
):
    """
    Create or update feed preferences for the current user.
    
    Describe what you want to see (or not see) in natural language.
    
    Examples:
    - "Show me science and technology posts, but no politics"
    - "I want to see posts about climate change with high trust scores"
    - "Show verified posts only, exclude sports and entertainment"
    """
    # Parse the prompt
    parsed_filters = feed_filter_service.parse_prompt(preference_data.prompt)
    
    # Check if preference already exists
    existing = db.query(FeedPreference).filter(
        FeedPreference.member_id == current_user.id
    ).first()
    
    if existing:
        # Update existing preference
        existing.prompt = preference_data.prompt
        existing.parsed_filters = parsed_filters
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Create new preference
        preference = FeedPreference(
            member_id=current_user.id,
            prompt=preference_data.prompt,
            parsed_filters=parsed_filters,
            active=True
        )
        db.add(preference)
        db.commit()
        db.refresh(preference)
        return preference


@router.patch("/me", response_model=FeedPreferenceResponse)
def update_preferences(
    preference_data: FeedPreferenceUpdate,
    current_user: Annotated[Member, Depends(get_current_active_user)],
    db: Session = Depends(get_session),
):
    """
    Update specific fields of feed preferences.
    
    Use this to enable/disable filtering or update your prompt.
    """
    preference = db.query(FeedPreference).filter(
        FeedPreference.member_id == current_user.id
    ).first()
    
    if not preference:
        raise HTTPException(
            status_code=404,
            detail="Feed preferences not found. Create them first using POST /me"
        )
    
    # Update fields if provided
    if preference_data.prompt is not None:
        preference.prompt = preference_data.prompt
        preference.parsed_filters = feed_filter_service.parse_prompt(preference_data.prompt)
    
    if preference_data.active is not None:
        preference.active = preference_data.active
    
    preference.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(preference)
    
    return preference


@router.delete("/me", status_code=204)
def delete_preferences(
    current_user: Annotated[Member, Depends(get_current_active_user)],
    db: Session = Depends(get_session),
):
    """Delete feed preferences (revert to default feed)."""
    preference = db.query(FeedPreference).filter(
        FeedPreference.member_id == current_user.id
    ).first()
    
    if preference:
        db.delete(preference)
        db.commit()
    
    return None
