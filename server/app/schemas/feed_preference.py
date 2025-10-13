"""Pydantic schemas for feed preferences."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class FeedPreferenceCreate(BaseModel):
    """Schema for creating/updating feed preferences."""
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Natural language description of what you want to see in your feed",
        examples=[
            "Show me science and technology posts, but no politics",
            "I want to see posts about climate change with high trust scores",
            "Show verified posts only, exclude sports and entertainment"
        ]
    )


class FeedPreferenceUpdate(BaseModel):
    """Schema for updating feed preferences."""
    prompt: Optional[str] = Field(
        None,
        min_length=1,
        max_length=2000,
        description="Natural language description of feed preferences"
    )
    active: Optional[bool] = Field(
        None,
        description="Enable or disable personalized filtering"
    )


class ParsedFilters(BaseModel):
    """Schema for parsed filter structure."""
    interests: list[str] = Field(default_factory=list, description="Topics to include")
    exclude_topics: list[str] = Field(default_factory=list, description="Topics to exclude")
    keywords_include: list[str] = Field(default_factory=list, description="Keywords to include")
    keywords_exclude: list[str] = Field(default_factory=list, description="Keywords to exclude")
    min_trust_score: Optional[int] = Field(None, description="Minimum trust score threshold")
    require_verified: bool = Field(False, description="Show only verified posts")


class FeedPreferenceResponse(BaseModel):
    """Schema for feed preference responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    member_id: int
    prompt: str
    parsed_filters: dict
    active: bool
    last_applied_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class FeedPreferencePreview(BaseModel):
    """Preview of how a prompt would be parsed."""
    prompt: str
    parsed_filters: ParsedFilters
    explanation: str = Field(
        description="Human-readable explanation of the filters that will be applied"
    )
