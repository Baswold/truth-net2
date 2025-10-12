"""Dual layer fact checking helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


POSITIVE_KEYWORDS = {
    "confirmed",
    "official",
    "according to",
    "evidence",
    "verified",
    "data shows",
    "study",
    "report",
}

NEGATIVE_KEYWORDS = {
    "debunked",
    "false",
    "misleading",
    "unverified",
    "uncorroborated",
    "rumour",
    "speculation",
    "unknown",
}


@dataclass(slots=True)
class CheckerResult:
    verdict: str
    confidence: float
    reasons: list[str]
    supporting_evidence: list[str]

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict,
            "confidence": round(self.confidence, 3),
            "reasons": self.reasons,
            "supporting_evidence": self.supporting_evidence,
        }


@dataclass(slots=True)
class FactCheckOutcome:
    primary: CheckerResult
    auditor: CheckerResult
    agreement_score: float
    final_verdict: str
    escalated: bool

    def to_dict(self) -> dict:
        return {
            "primary": self.primary.to_dict(),
            "auditor": self.auditor.to_dict(),
            "agreement_score": round(self.agreement_score, 3),
            "final_verdict": self.final_verdict,
            "escalated": self.escalated,
        }


class HeuristicChecker:
    """Very small deterministic checker used for tests."""

    def evaluate(
        self,
        claim: str,
        evidence_snippets: Sequence[str],
        *,
        context: str | None = None,
        prior: CheckerResult | None = None,
    ) -> CheckerResult:
        text_blobs = [claim]
        if context:
            text_blobs.append(context)
        text_blobs.extend(evidence_snippets)
        score = 0
        for blob in text_blobs:
            lower = blob.lower()
            if any(keyword in lower for keyword in POSITIVE_KEYWORDS):
                score += 1
            if any(keyword in lower for keyword in NEGATIVE_KEYWORDS):
                score -= 1

        if prior:
            if prior.verdict == "verified":
                score += int(prior.confidence * 2)
            elif prior.verdict == "refuted":
                score -= int(prior.confidence * 2)

        if score > 0:
            verdict = "verified"
        elif score < 0:
            verdict = "refuted"
        else:
            verdict = "inconclusive"

        confidence = min(0.95, max(0.05, abs(score) / max(len(evidence_snippets), 1)))

        reasons = []
        if score > 0:
            reasons.append("Multiple supporting snippets mention confirmation language.")
        elif score < 0:
            reasons.append("Contradicting phrases were identified in the supplied evidence.")
        else:
            reasons.append("Evidence pool lacked enough signal to decide deterministically.")

        if prior and verdict != prior.verdict:
            reasons.append("Diverges from the paired checker and flags for curator review.")

        return CheckerResult(
            verdict=verdict,
            confidence=confidence,
            reasons=reasons,
            supporting_evidence=list(evidence_snippets),
        )


class DualLayerFactChecker:
    """Runs two heuristic checkers that audit each other."""

    def __init__(self) -> None:
        self.primary_checker = HeuristicChecker()
        self.auditor_checker = HeuristicChecker()

    def run_fact_check(
        self,
        claim: str,
        evidence_snippets: Sequence[str],
        *,
        context: str | None = None,
    ) -> FactCheckOutcome:
        primary = self.primary_checker.evaluate(
            claim,
            evidence_snippets,
            context=context,
        )

        auditor = self.auditor_checker.evaluate(
            claim,
            evidence_snippets,
            context=context,
            prior=primary,
        )

        agreement = 1.0 - abs(primary.confidence - auditor.confidence)
        if primary.verdict != auditor.verdict:
            agreement -= 0.4

        agreement = max(0.0, min(1.0, agreement))

        if primary.verdict == auditor.verdict and agreement >= 0.6:
            final_verdict = primary.verdict
            escalated = False
        else:
            final_verdict = "needs_review"
            escalated = True

        return FactCheckOutcome(
            primary=primary,
            auditor=auditor,
            agreement_score=agreement,
            final_verdict=final_verdict,
            escalated=escalated,
        )
