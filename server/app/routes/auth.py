from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    hash_password,
    verify_password,
)
from ..database import get_session
from ..models import Member
from ..schemas.auth import TokenResponse, UserLogin, UserProfile, UserSignup

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse)
def signup(user_data: UserSignup, db: Session = Depends(get_session)):
    """Register a new user."""
    # Check if email exists
    existing = db.query(Member).filter(Member.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Registration failed. Please check your information.")
    
    # Check if username exists
    existing = db.query(Member).filter(Member.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Registration failed. Please check your information.")
    
    # Create new member
    member = Member(
        email=user_data.email,
        username=user_data.username,
        display_name=user_data.display_name,
        password_hash=hash_password(user_data.password),
        roles="member",
        trust_score=0,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(member.id), "username": member.username})
    refresh_token = create_refresh_token(data={"sub": str(member.id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=60 * 60  # 1 hour in seconds
    )


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_session)):
    """Login with email or username."""
    # Try to find user by email or username
    member = (
        db.query(Member)
        .filter(
            (Member.email == credentials.email_or_username)
            | (Member.username == credentials.email_or_username)
        )
        .first()
    )
    
    if not member or not verify_password(credentials.password, member.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
        )
    
    # Update last login
    member.last_login_at = datetime.utcnow()
    db.commit()
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(member.id), "username": member.username})
    refresh_token = create_refresh_token(data={"sub": str(member.id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=60 * 60  # 1 hour in seconds
    )


@router.get("/me", response_model=UserProfile)
def get_my_profile(current_user: Annotated[Member, Depends(get_current_user)]):
    """Get current authenticated user profile."""
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        display_name=current_user.display_name,
        bio=current_user.bio,
        avatar_url=current_user.avatar_url,
        trust_score=current_user.trust_score,
        roles=current_user.roles,
        created_at=current_user.created_at.isoformat(),
    )
