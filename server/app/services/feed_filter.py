"""Feed filtering and personalization service."""
import re
from typing import List, Optional

from sqlalchemy import or_, and_
from sqlalchemy.orm import Query, Session

from ..models import TruthPost, FeedPreference


class FeedFilterService:
    """
    Service for applying personalized feed preferences.
    
    Parses natural language preferences and applies filters to social feed queries.
    """
    
    def parse_prompt(self, prompt: str) -> dict:
        """
        Parse natural language prompt into structured filters.
        
        Example prompts:
        - "Show me science and technology posts, but no politics"
        - "I want to see posts about climate change with high trust scores"
        - "Show verified posts only, exclude sports and entertainment"
        """
        filters = {
            "interests": [],
            "exclude_topics": [],
            "keywords_include": [],
            "keywords_exclude": [],
            "min_trust_score": None,
            "require_verified": False,
        }
        
        prompt_lower = prompt.lower()
        
        # Extract interests/topics to include
        include_patterns = [
            r"(?:show|include|want|like|interested in)\s+(?:me\s+)?(?:posts?\s+)?(?:about\s+)?([^,\.]+?)(?:\s+(?:but|and|with|posts?|content)|\.|$)",
            r"topics?:\s*([^,\.]+)",
            r"interests?:\s*([^,\.]+)",
        ]
        
        for pattern in include_patterns:
            matches = re.finditer(pattern, prompt_lower)
            for match in matches:
                topics = match.group(1).strip()
                # Split on "and" or commas
                topic_list = re.split(r'\s+and\s+|,\s*', topics)
                filters["interests"].extend([t.strip() for t in topic_list if t.strip()])
        
        # Extract topics to exclude
        exclude_patterns = [
            r"(?:but\s+)?(?:no|not|exclude|don't want|avoid|hide)\s+(?:posts?\s+)?(?:about\s+)?([^,\.]+?)(?:\.|$|,)",
            r"exclude:\s*([^,\.]+)",
        ]
        
        for pattern in exclude_patterns:
            matches = re.finditer(pattern, prompt_lower)
            for match in matches:
                topics = match.group(1).strip()
                topic_list = re.split(r'\s+and\s+|,\s*', topics)
                filters["exclude_topics"].extend([t.strip() for t in topic_list if t.strip()])
        
        # Extract trust score requirements
        trust_patterns = [
            r"(?:trust\s+score|score)\s+(?:above|over|at least|minimum|min)\s+(\d+)",
            r"(?:high|good)\s+trust",
        ]
        
        for pattern in trust_patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                if match.groups():
                    filters["min_trust_score"] = int(match.group(1))
                else:
                    filters["min_trust_score"] = 5  # Default "high" threshold
                break
        
        # Check for verified/verified-only requirements
        if re.search(r"(?:verified|verified only|only verified)", prompt_lower):
            filters["require_verified"] = True
        
        # Remove common stopwords from interests/exclude lists
        stopwords = {"posts", "post", "content", "topics", "topic", "about", "the", "a", "an"}
        filters["interests"] = [t for t in filters["interests"] if t not in stopwords]
        filters["exclude_topics"] = [t for t in filters["exclude_topics"] if t not in stopwords]
        
        return filters
    
    def apply_filters(
        self,
        query: Query,
        filters: dict,
        db: Session
    ) -> Query:
        """
        Apply parsed filters to a TruthPost query.
        
        Args:
            query: Base SQLAlchemy query for TruthPost
            filters: Parsed filter dictionary
            db: Database session
            
        Returns:
            Modified query with filters applied
        """
        # Apply trust score filter
        if filters.get("min_trust_score") is not None:
            query = query.filter(TruthPost.trust_score >= filters["min_trust_score"])
        
        # Apply verified requirement (using trust_score as proxy)
        if filters.get("require_verified"):
            query = query.filter(TruthPost.trust_score >= 10)
        
        # Apply interest filters (include topics)
        if filters.get("interests"):
            # Search in tags, title, and content
            interest_conditions = []
            for interest in filters["interests"]:
                # Search in JSON tags field
                interest_conditions.append(
                    TruthPost.tags.cast(db.bind.dialect.JSON()).contains({interest: True})
                )
                # Search in title
                if TruthPost.title:
                    interest_conditions.append(TruthPost.title.ilike(f"%{interest}%"))
                # Search in content
                interest_conditions.append(TruthPost.content.ilike(f"%{interest}%"))
            
            if interest_conditions:
                query = query.filter(or_(*interest_conditions))
        
        # Apply exclusion filters
        if filters.get("exclude_topics"):
            exclude_conditions = []
            for topic in filters["exclude_topics"]:
                # Exclude if found in tags, title, or content
                exclude_conditions.append(
                    TruthPost.tags.cast(db.bind.dialect.JSON()).contains({topic: True})
                )
                if TruthPost.title:
                    exclude_conditions.append(TruthPost.title.ilike(f"%{topic}%"))
                exclude_conditions.append(TruthPost.content.ilike(f"%{topic}%"))
            
            if exclude_conditions:
                # Exclude posts matching any of these conditions
                query = query.filter(~or_(*exclude_conditions))
        
        return query
    
    def get_personalized_feed(
        self,
        member_id: int,
        db: Session,
        limit: int = 20,
        offset: int = 0
    ) -> List[TruthPost]:
        """
        Get personalized feed for a user based on their preferences.
        
        Args:
            member_id: User ID
            db: Database session
            limit: Number of posts to return
            offset: Offset for pagination
            
        Returns:
            List of TruthPost objects matching user preferences
        """
        # Get user's feed preferences
        preference = db.query(FeedPreference).filter(
            FeedPreference.member_id == member_id,
            FeedPreference.active.is_(True)
        ).first()
        
        # Start with base query for published posts
        query = db.query(TruthPost).filter(TruthPost.published.is_(True))
        
        # Apply filters if preferences exist
        if preference and preference.parsed_filters:
            query = self.apply_filters(query, preference.parsed_filters, db)
        
        # Order by trust score and recency
        query = query.order_by(
            TruthPost.trust_score.desc(),
            TruthPost.created_at.desc()
        )
        
        # Apply pagination
        posts = query.offset(offset).limit(limit).all()
        
        return posts


# Singleton instance
feed_filter_service = FeedFilterService()
