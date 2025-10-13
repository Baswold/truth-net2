from typing import Annotated, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from ..auth import require_role
from ..database import get_session
from ..models import Member, Submission, ReviewAction

router = APIRouter(prefix="/moderation", tags=["moderation"])


class SubmissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    submission_type: str
    submitted_by: int
    payload: dict
    state: str
    priority: int
    created_at: str


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    submission_id: int
    reviewer_id: int
    decision: str
    rationale: str | None
    reviewed_at: str


@router.get("/submissions", response_model=List[SubmissionResponse])
def list_submissions(
    state: str | None = None,
    limit: int = 50,
    current_user: Annotated[Member, Depends(require_role("curator", "admin"))],
    db: Session = Depends(get_session)
):
    """Get pending submissions for review. Requires curator or admin role."""
    query = db.query(Submission)
    
    if state:
        query = query.filter(Submission.state == state)
    else:
        query = query.filter(Submission.state == "pending")
    
    submissions = query.order_by(Submission.priority.desc(), Submission.created_at.asc()).limit(limit).all()
    
    return [
        SubmissionResponse(
            id=s.id,
            submission_type=s.submission_type,
            submitted_by=s.submitted_by,
            payload=s.payload,
            state=s.state,
            priority=s.priority,
            created_at=s.created_at.isoformat(),
        )
        for s in submissions
    ]


@router.get("/submissions/{submission_id}/reviews", response_model=List[ReviewResponse])
def get_submission_reviews(
    submission_id: int,
    current_user: Annotated[Member, Depends(require_role("curator", "admin"))],
    db: Session = Depends(get_session)
):
    """Get reviews for a submission. Requires curator or admin role."""
    reviews = db.query(ReviewAction).filter(ReviewAction.submission_id == submission_id).all()
    
    return [
        ReviewResponse(
            id=r.id,
            submission_id=r.submission_id,
            reviewer_id=r.reviewer_id,
            decision=r.decision,
            rationale=r.rationale,
            reviewed_at=r.reviewed_at.isoformat(),
        )
        for r in reviews
    ]
