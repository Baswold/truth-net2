from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import create_access_token, create_refresh_token, hash_password, verify_password
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
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username exists
    existing = db.query(Member).filter(Member.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    
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
    
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


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
    
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.get("/me", response_model=UserProfile)
def get_current_user(db: Session = Depends(get_session)):
    """Get current user profile. (Simplified - would need JWT middleware in production)"""
    # For now, return first user or create demo user
    member = db.query(Member).first()
    if not member:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return UserProfile(
        id=member.id,
        email=member.email,
        username=member.username,
        display_name=member.display_name,
        bio=member.bio,
        avatar_url=member.avatar_url,
        trust_score=member.trust_score,
        roles=member.roles,
        created_at=member.created_at.isoformat(),
    )
