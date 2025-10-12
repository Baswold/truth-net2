"""API endpoints for the dual-layer fact checker."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import get_session
from ..models import FactCheckRun
from ..services.fact_check import DualLayerFactChecker

router = APIRouter(prefix="/fact-check", tags=["fact-check"])


class FactCheckRequest(BaseModel):
    target_type: str = Field(examples=["page", "post", "comment"])
    target_id: int
    claim_text: str
    evidence_snippets: list[str] = Field(default_factory=list)
    context: str | None = None


class CheckerPayload(BaseModel):
    verdict: str
    confidence: float
    reasons: list[str]
    supporting_evidence: list[str]


class FactCheckResponse(BaseModel):
    run_id: int
    final_verdict: str
    agreement_score: float
    primary: CheckerPayload
    auditor: CheckerPayload
    escalated: bool


_fact_checker = DualLayerFactChecker()


@router.post("/runs", response_model=FactCheckResponse)
def run_fact_check(request: FactCheckRequest, db: Session = Depends(get_session)):
    """Execute a dual-layer fact check and persist the run."""

    if not request.evidence_snippets:
        raise HTTPException(status_code=400, detail="At least one evidence snippet is required")

    outcome = _fact_checker.run_fact_check(
        request.claim_text,
        request.evidence_snippets,
        context=request.context,
    )

    run = FactCheckRun(
        target_type=request.target_type,
        target_id=request.target_id,
        primary_checker_result=outcome.primary.to_dict(),
        auditor_checker_result=outcome.auditor.to_dict(),
        agreement_score=outcome.agreement_score,
        final_verdict=outcome.final_verdict,
        web_search_queries={"manual": request.evidence_snippets},
        web_search_results={},
        curator_reviewed=outcome.escalated is False,
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    return FactCheckResponse(
        run_id=run.id,
        final_verdict=run.final_verdict or "needs_review",
        agreement_score=run.agreement_score or 0.0,
        primary=CheckerPayload(**run.primary_checker_result),
        auditor=CheckerPayload(**run.auditor_checker_result),
        escalated=outcome.escalated,
    )
