from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from immo_paris.api.routes import health, sales
from immo_paris.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Immo Paris API", version="0.1.0")

    # Front-ends Angular (web) et React Native (mobile)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(sales.router)
    return app


app = create_app()
