from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, blogs, generate
from .core.config import settings
from .db.base import init_db

# PUBLIC_INTERFACE
def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application with routes and middleware.
    """
    app = FastAPI(
        title="ContentCraft AI Backend",
        description=(
            "Backend API for an AI-powered platform that enables users to generate, "
            "edit, and manage blog posts.\n\n"
            "Features:\n"
            "- User authentication (JWT)\n"
            "- Prompt input for blog generation\n"
            "- Blog CRUD operations\n"
            "- Blog history management\n"
            "- WebSocket docs note: (none in this version)"
        ),
        version="1.0.0",
        contact={"name": "ContentCraft AI", "url": "https://example.com"},
        license_info={"name": "MIT"},
        swagger_ui_parameters={"defaultModelsExpandDepth": -1},
        openapi_tags=[
            {"name": "Health", "description": "Health and meta endpoints"},
            {"name": "Auth", "description": "User authentication and profile"},
            {"name": "Generate", "description": "Prompt-based AI blog generation"},
            {"name": "Blogs", "description": "Blog CRUD and history management"},
        ],
    )

    # CORS
    allow_origins = settings.CORS_ALLOW_ORIGINS if settings.CORS_ALLOW_ORIGINS else ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(auth.router, prefix="/auth", tags=["Auth"])
    app.include_router(generate.router, prefix="/generate", tags=["Generate"])
    app.include_router(blogs.router, prefix="/blogs", tags=["Blogs"])

    @app.get("/", summary="Health Check", tags=["Health"])
    # PUBLIC_INTERFACE
    def health_check():
        """Health check endpoint.

        Returns:
            dict: Basic information indicating service is healthy.
        """
        return {"message": "Healthy", "version": app.version}

    return app


app = create_app()

# Ensure DB initialized on import for script usage
init_db()
