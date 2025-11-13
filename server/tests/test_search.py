from __future__ import annotations

from app.models import Member, Page, Site, SiteStatus


def test_search_sites_db_fallback(client, session):
    """Test searching sites using database fallback."""
    member = Member(
        email="owner@example.com",
        username="siteowner",
        display_name="Site Owner",
        password_hash="hashed",
    )
    session.add(member)
    session.flush()

    site1 = Site(
        slug="climate-facts",
        title="Climate Science Facts",
        description="Verified climate science information",
        status=SiteStatus.PUBLISHED.value,
        owner=member,
    )
    site2 = Site(
        slug="health-hub",
        title="Health Information Hub",
        description="Trusted health advice and research",
        status=SiteStatus.PUBLISHED.value,
        owner=member,
    )
    site3 = Site(
        slug="tech-news",
        title="Technology News",
        description="Latest tech developments",
        status=SiteStatus.PUBLISHED.value,
        owner=member,
    )
    session.add_all([site1, site2, site3])
    session.commit()

    # Search for "climate" should return climate-facts
    response = client.get("/v1/search/?q=climate&use_db_fallback=true")
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 1
    assert any(r["title"] == "Climate Science Facts" for r in results)
    assert any(r["type"] == "site" for r in results)


def test_search_pages_db_fallback(client, session):
    """Test searching pages using database fallback."""
    member = Member(
        email="owner@example.com",
        username="siteowner",
        display_name="Site Owner",
        password_hash="hashed",
    )
    site = Site(
        slug="knowledge-base",
        title="Knowledge Base",
        description="Verified knowledge",
        status=SiteStatus.PUBLISHED.value,
        owner=member,
    )
    session.add(site)
    session.flush()

    page1 = Page(
        site=site,
        path="/vaccine-facts",
        title="Vaccine Facts",
        status="published",
        layout_json={},
        page_metadata={"description": "Facts about vaccines"},
    )
    page2 = Page(
        site=site,
        path="/nutrition",
        title="Nutrition Guidelines",
        status="published",
        layout_json={},
        page_metadata={"description": "Evidence-based nutrition"},
    )
    session.add_all([page1, page2])
    session.commit()

    # Search for "vaccine" should return vaccine page
    response = client.get("/v1/search/?q=vaccine&use_db_fallback=true")
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 1
    page_results = [r for r in results if r["type"] == "page"]
    assert any(r["title"] == "Vaccine Facts" for r in page_results)


def test_search_with_type_filter_site(client, session):
    """Test searching with type filter for sites only."""
    member = Member(
        email="owner@example.com",
        username="siteowner",
        display_name="Site Owner",
        password_hash="hashed",
    )
    site = Site(
        slug="science-hub",
        title="Science Hub",
        description="Scientific research",
        status=SiteStatus.PUBLISHED.value,
        owner=member,
    )
    session.add(site)
    session.flush()

    page = Page(
        site=site,
        path="/research",
        title="Research Methods",
        status="published",
        layout_json={},
        page_metadata={},
    )
    session.add(page)
    session.commit()

    # Search with type_filter=site should only return sites
    response = client.get("/v1/search/?q=science&type_filter=site&use_db_fallback=true")
    assert response.status_code == 200
    results = response.json()
    assert all(r["type"] == "site" for r in results)


def test_search_with_type_filter_page(client, session):
    """Test searching with type filter for pages only."""
    member = Member(
        email="owner@example.com",
        username="siteowner",
        display_name="Site Owner",
        password_hash="hashed",
    )
    site = Site(
        slug="docs-site",
        title="Documentation Site",
        description="Technical documentation",
        status=SiteStatus.PUBLISHED.value,
        owner=member,
    )
    session.add(site)
    session.flush()

    page = Page(
        site=site,
        path="/api-docs",
        title="API Documentation",
        status="published",
        layout_json={},
        page_metadata={"description": "API reference"},
    )
    session.add(page)
    session.commit()

    # Search with type_filter=page should only return pages
    response = client.get("/v1/search/?q=api&type_filter=page&use_db_fallback=true")
    assert response.status_code == 200
    results = response.json()
    assert all(r["type"] == "page" for r in results)


def test_search_pagination(client, session):
    """Test search pagination with limit and offset."""
    member = Member(
        email="owner@example.com",
        username="siteowner",
        display_name="Site Owner",
        password_hash="hashed",
    )
    session.add(member)
    session.flush()

    # Create multiple sites with "test" in the title
    for i in range(5):
        site = Site(
            slug=f"test-site-{i}",
            title=f"Test Site {i}",
            description=f"Test description {i}",
            status=SiteStatus.PUBLISHED.value,
            owner=member,
        )
        session.add(site)
    session.commit()

    # Get first 2 results (filter by type=site to avoid limit splitting)
    response1 = client.get("/v1/search/?q=test&limit=2&type_filter=site&use_db_fallback=true")
    assert response1.status_code == 200
    results1 = response1.json()
    assert len(results1) == 2

    # Get next 2 results with offset
    response2 = client.get("/v1/search/?q=test&limit=2&offset=2&type_filter=site&use_db_fallback=true")
    assert response2.status_code == 200
    results2 = response2.json()
    assert len(results2) == 2

    # Results should be different
    ids1 = {r["id"] for r in results1}
    ids2 = {r["id"] for r in results2}
    assert ids1.isdisjoint(ids2)


def test_search_empty_query(client):
    """Test that search requires a query parameter."""
    response = client.get("/v1/search/")
    assert response.status_code == 422  # Validation error


def test_search_no_results(client, session):
    """Test search with no matching results."""
    response = client.get("/v1/search/?q=nonexistentquery123456&use_db_fallback=true")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 0


def test_search_case_insensitive(client, session):
    """Test that search is case-insensitive."""
    member = Member(
        email="owner@example.com",
        username="siteowner",
        display_name="Site Owner",
        password_hash="hashed",
    )
    site = Site(
        slug="quantum-physics",
        title="Quantum Physics Research",
        description="Advanced quantum mechanics",
        status=SiteStatus.PUBLISHED.value,
        owner=member,
    )
    session.add(site)
    session.commit()

    # Search with different cases should all return results
    for query in ["quantum", "QUANTUM", "QuAnTuM"]:
        response = client.get(f"/v1/search/?q={query}&use_db_fallback=true")
        assert response.status_code == 200
        results = response.json()
        assert len(results) >= 1
        assert any("Quantum" in r["title"] for r in results)


def test_search_only_published_content(client, session):
    """Test that search only returns published content."""
    member = Member(
        email="owner@example.com",
        username="siteowner",
        display_name="Site Owner",
        password_hash="hashed",
    )
    published_site = Site(
        slug="published-site",
        title="Published Site",
        description="Visible to search",
        status=SiteStatus.PUBLISHED.value,
        owner=member,
    )
    draft_site = Site(
        slug="draft-site",
        title="Draft Site",
        description="Not visible to search",
        status=SiteStatus.DRAFT.value,
        owner=member,
    )
    session.add_all([published_site, draft_site])
    session.commit()

    response = client.get("/v1/search/?q=site&use_db_fallback=true")
    assert response.status_code == 200
    results = response.json()

    # Should find published site
    assert any(r["title"] == "Published Site" for r in results)
    # Should NOT find draft site
    assert not any(r["title"] == "Draft Site" for r in results)
