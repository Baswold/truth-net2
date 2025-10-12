from __future__ import annotations

from app.models import Member, Site, SiteStatus


def test_site_blueprint_preview(client, session):
    member = Member(
        email="owner@example.com",
        username="owner",
        display_name="Owner",
        password_hash="hashed",
    )
    site = Site(
        slug="truth-lab",
        title="Truth Lab",
        description="Lab for testing blueprints",
        status=SiteStatus.PUBLISHED.value,
        owner=member,
    )
    session.add(site)
    session.commit()

    response = client.get("/v1/sites/blueprints")
    assert response.status_code == 200
    blueprints = response.json()
    assert any(bp["key"] == "authority_article" for bp in blueprints)

    preview_payload = {
        "blueprint_key": "authority_article",
        "content_outline": [
            {"heading": "Mission", "summary": "Aims", "callouts": ["Key insight"]},
            {"heading": "Background", "summary": "History"},
        ],
        "seo_keywords": ["truth", "verification"],
        "audience": "investigators",
        "enable_flags": {"interactive_faq": True, "glossary_support": True},
    }
    preview_resp = client.post(
        "/v1/sites/truth-lab/pages/preview",
        json=preview_payload,
    )
    assert preview_resp.status_code == 200
    payload = preview_resp.json()
    assert payload["layout_json"]["blueprint"] == "authority_article"
    assert any(section["id"] == "glossary" for section in payload["layout_json"]["sections"])
    assert "recommendations" in payload and len(payload["recommendations"]) >= 1
