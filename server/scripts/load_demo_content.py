#!/usr/bin/env python3
"""
Load demo content into the database for testing and demonstration.
"""

import json
import os
from pathlib import Path

from sqlalchemy.orm import sessionmaker

from app.database import engine
from app.models import Member, Site, Page, ContentVersion, TruthPost, TruthThread

SessionLocal = sessionmaker(bind=engine)

# Demo content paths
DEMO_DIR = Path(__file__).parent.parent.parent / "docs" / "demo-content"


def load_demo_content():
    """Load demo sites, pages, posts, and threads."""
    if not DEMO_DIR.exists():
        print(f"❌ Demo content directory not found: {DEMO_DIR}")
        return

    with SessionLocal() as session:
        # Create demo admin if not exists
        admin = session.query(Member).filter(Member.username == "truthnet-admin").first()
        if not admin:
            admin = Member(
                email="admin@truthnet.dev",
                username="truthnet-admin",
                display_name="Truth Net Admin",
                password_hash="$2b$12$dummy.hash.for.demo.only",  # In real app, use proper hashing
                roles="admin,curator,member",
                trust_score=100,
            )
            session.add(admin)
            session.commit()
            session.refresh(admin)

        # Load demo sites
        for site_file in DEMO_DIR.glob("*.json"):
            try:
                with open(site_file) as f:
                    data = json.load(f)

                site_data = data["site"]
                pages_data = data.get("pages", [])

                # Create site
                site = Site(
                    slug=site_data["slug"],
                    title=site_data["title"],
                    description=site_data["description"],
                    tags=site_data.get("tags", {}),
                    theme=site_data.get("theme"),
                    status="published",
                    owner_id=admin.id,
                )
                session.add(site)
                session.flush()  # Get site ID

                print(f"📄 Loaded site: {site.title}")

                # Create pages
                for page_data in pages_data:
                    from datetime import datetime
                    published_at = datetime.utcnow()
                    
                    page = Page(
                        site_id=site.id,
                        path=page_data["path"],
                        title=page_data["title"],
                        layout_json=page_data.get("layout", {}),
                        page_metadata=page_data.get("metadata", {}),
                        status="published",
                        published_at=published_at,
                    )
                    session.add(page)
                    session.flush()

                    # Create content version
                    version = ContentVersion(
                        page_id=page.id,
                        version_number=1,
                        layout_json=page_data.get("layout", {}),
                        editor_id=admin.id,
                        published_at=published_at,
                    )
                    session.add(version)
                    session.flush()

                    page.live_version_id = version.id
                    session.commit()

                    print(f"  └─ Page: {page.title}")

                session.commit()

            except Exception as e:
                print(f"❌ Error loading {site_file}: {e}")
                session.rollback()

        # Create demo posts and threads
        demo_posts = [
            {
                "title": "Welcome to Truth Net",
                "content": "This is a demonstration of the Truth Net platform. Here we prioritize accuracy, transparency, and community-driven verification.",
                "tags": {"category": "announcement", "topic": "platform"},
                "author_id": admin.id,
            },
            {
                "title": "How Fact Checking Works",
                "content": "Our dual-AI fact checking system ensures content accuracy through automated verification and cross-community validation.",
                "tags": {"category": "education", "topic": "fact-checking"},
                "author_id": admin.id,
            },
        ]

        for post_data in demo_posts:
            post = TruthPost(
                author_id=post_data["author_id"],
                title=post_data["title"],
                content=post_data["content"],
                tags=post_data["tags"],
                published=True,
                trust_score=50,
            )
            session.add(post)
            session.flush()

            # Create discussion thread
            thread = TruthThread(
                post_id=post.id,
                creator_id=admin.id,
                title=f"Discussion: {post_data['title']}",
                topic=post_data["tags"].get("topic"),
                trust_score=25,
            )
            session.add(thread)
            session.commit()

            print(f"💬 Created post: {post.title}")

        print("✅ Demo content loaded successfully!")
        print(f"   Sites: 3, Posts: {len(demo_posts)}, Threads: {len(demo_posts)}")


if __name__ == "__main__":
    load_demo_content()
