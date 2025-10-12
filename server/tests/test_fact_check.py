from __future__ import annotations

from app.models import Page, Site, SiteStatus
from app.services.fact_check import DualLayerFactChecker


def test_dual_layer_fact_checker_agreement():
    checker = DualLayerFactChecker()
    outcome = checker.run_fact_check(
        "The report was officially confirmed.",
        ["According to an official report, the claim is confirmed."],
    )
    assert outcome.final_verdict == "verified"
    assert outcome.agreement_score > 0.5
    assert outcome.escalated is False


def test_fact_check_route_persists_run(client, session):
    site = Site(
        slug="analysis-hub",
        title="Analysis Hub",
        status=SiteStatus.PUBLISHED.value,
    )
    page = Page(
        site=site,
        path="/insight",
        title="Insight",
        status="published",
        layout_json={},
        page_metadata={},
    )
    session.add(page)
    session.commit()

    request_payload = {
        "target_type": "page",
        "target_id": page.id,
        "claim_text": "Researchers confirmed the finding.",
        "evidence_snippets": ["Official data shows the finding was confirmed."],
        "context": "Research summary",
    }
    response = client.post("/v1/fact-check/runs", json=request_payload)
    assert response.status_code == 200
    body = response.json()
    assert body["run_id"] > 0
    assert body["final_verdict"] in {"verified", "needs_review"}
    assert body["primary"]["confidence"] >= 0.05

    from app.models import FactCheckRun

    run = session.query(FactCheckRun).filter(FactCheckRun.id == body["run_id"]).one()
    assert run.primary_checker_result["verdict"] == body["primary"]["verdict"]
