from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routes import auth_router, sites_router, social_router, search_router, moderation_router


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(auth_router, prefix=settings.api_v1_prefix)
    app.include_router(sites_router, prefix=settings.api_v1_prefix)
    app.include_router(social_router, prefix=settings.api_v1_prefix)
    app.include_router(search_router, prefix=settings.api_v1_prefix)
    app.include_router(moderation_router, prefix=settings.api_v1_prefix)

    @app.get("/")
    def read_root():
        return {"status": "ok", "message": "Truth Net server online"}

    @app.get("/health")
    def health_check():
        return {"status": "healthy", "version": "0.1.0"}

    return app


app = create_app()
