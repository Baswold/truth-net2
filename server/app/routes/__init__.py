from .auth import router as auth_router
from .sites import router as sites_router
from .social import router as social_router
from .search import router as search_router
from .moderation import router as moderation_router
from .fact_check import router as fact_check_router
from .feed_preference import router as feed_preference_router

__all__ = [
    "auth_router",
    "sites_router",
    "social_router",
    "search_router",
    "moderation_router",
    "fact_check_router",
    "feed_preference_router",
]
