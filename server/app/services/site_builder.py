"""Utility helpers that power the site builder endpoints."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True, slots=True)
class PageBlueprint:
    """Describes a composable layout blueprint used by the site builder."""

    key: str
    title: str
    description: str
    sections: Sequence[str]
    recommended_blocks: Sequence[str]

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "title": self.title,
            "description": self.description,
            "sections": list(self.sections),
            "recommended_blocks": list(self.recommended_blocks),
        }


BLUEPRINT_CATALOG: tuple[PageBlueprint, ...] = (
    PageBlueprint(
        key="authority_article",
        title="Authority Article",
        description=(
            "Long-form layout optimised for research-backed explainers with a "
            "strong call-to-action strip and an evidence spotlight sidebar."
        ),
        sections=(
            "hero",
            "key_takeaways",
            "body_with_sidebar",
            "evidence_showcase",
            "call_to_action",
        ),
        recommended_blocks=(
            "hero.banner",
            "content.outline",
            "evidence.cards",
            "cta.ribbon",
        ),
    ),
    PageBlueprint(
        key="rapid_update",
        title="Rapid Update",
        description=(
            "Concise newsroom-style layout that surfaces the latest changes, "
            "timeline context, and links out to primary sources."
        ),
        sections=(
            "headline",
            "update_feed",
            "timeline",
            "source_list",
        ),
        recommended_blocks=(
            "alert.badge",
            "timeline.events",
            "sources.list",
        ),
    ),
    PageBlueprint(
        key="knowledge_base",
        title="Knowledge Base Entry",
        description=(
            "Structured documentation page with collapsible FAQ segments, "
            "related topics, and glossary support for jargon-heavy subjects."
        ),
        sections=(
            "title_header",
            "in_depth_sections",
            "faq",
            "related_links",
        ),
        recommended_blocks=(
            "toc.anchor",
            "accordion.faq",
            "chips.related_topics",
        ),
    ),
)


def list_blueprints() -> list[dict]:
    """Return all available blueprints in a serialisable form."""

    return [blueprint.to_dict() for blueprint in BLUEPRINT_CATALOG]


def _build_sections(
    blueprint: PageBlueprint,
    content_outline: Iterable[dict],
    enable_flags: dict[str, bool] | None = None,
) -> list[dict]:
    enable_flags = enable_flags or {}

    outline = list(content_outline)
    sections: list[dict] = []

    for idx, section_id in enumerate(blueprint.sections):
        section_outline = outline[idx] if idx < len(outline) else None
        base_section = {
            "id": section_id,
            "component": section_id,
            "props": {},
        }

        if section_outline:
            base_section["props"].update(
                {
                    "heading": section_outline.get("heading"),
                    "summary": section_outline.get("summary"),
                    "callouts": section_outline.get("callouts", []),
                }
            )

        if section_id in {"faq", "in_depth_sections"} and enable_flags.get("interactive_faq"):
            base_section["props"]["mode"] = "accordion"

        if section_id == "evidence_showcase" and enable_flags.get("evidence_spotlight"):
            base_section["props"]["highlight"] = enable_flags["evidence_spotlight"]

        sections.append(base_section)

    if enable_flags.get("glossary_support"):
        sections.append(
            {
                "id": "glossary",
                "component": "glossary",
                "props": {
                    "autoGenerate": True,
                    "placement": "drawer",
                },
            }
        )

    if enable_flags.get("collaboration_notes"):
        sections.append(
            {
                "id": "collaboration_notes",
                "component": "collaboration-panel",
                "props": {"mode": "comment", "visibility": "editors"},
            }
        )

    return sections


def generate_layout(
    blueprint_key: str,
    content_outline: Iterable[dict],
    *,
    enable_flags: dict[str, bool] | None = None,
    seo_keywords: Iterable[str] | None = None,
    audience: str | None = None,
) -> dict:
    """Compose a layout JSON document for a page."""

    blueprint = next((b for b in BLUEPRINT_CATALOG if b.key == blueprint_key), None)
    if not blueprint:
        raise ValueError(f"Unknown blueprint '{blueprint_key}'")

    sections = _build_sections(blueprint, content_outline, enable_flags)

    layout = {
        "blueprint": blueprint.key,
        "sections": sections,
        "metadata": {
            "recommendedBlocks": list(blueprint.recommended_blocks),
            "seo": {
                "keywords": list(seo_keywords or []),
                "audience": audience,
            },
        },
    }

    return layout


def build_editor_recommendations(
    blueprint_key: str,
    outline: Iterable[dict],
) -> list[str]:
    """Suggest actionable follow-ups for human editors."""

    outline_list = list(outline)
    recs: list[str] = []

    if not outline_list:
        recs.append("Add at least one section outline to unlock automated layout helpers.")

    if blueprint_key == "authority_article":
        recs.append("Embed supporting data visualisations to strengthen the authority narrative.")
    if blueprint_key == "rapid_update":
        recs.append("Schedule refresh automation so the update feed stays real-time.")
    if blueprint_key == "knowledge_base":
        recs.append("Link two related entries to improve knowledge graph traversal.")

    with_callouts = [
        section
        for section in outline_list
        if section.get("callouts")
    ]
    if len(with_callouts) < 1:
        recs.append("Tag at least one key takeaway to surface it in list previews.")

    return recs


def create_preview(
    blueprint_key: str,
    content_outline: Iterable[dict],
    *,
    enable_flags: dict[str, bool] | None = None,
    seo_keywords: Iterable[str] | None = None,
    audience: str | None = None,
) -> dict:
    """Return a combined layout/metadata preview payload used by the API layer."""

    layout = generate_layout(
        blueprint_key,
        content_outline,
        enable_flags=enable_flags,
        seo_keywords=seo_keywords,
        audience=audience,
    )

    recommendations = build_editor_recommendations(blueprint_key, content_outline)

    return {
        "layout": layout,
        "metadata": layout.get("metadata", {}),
        "recommendations": recommendations,
    }
