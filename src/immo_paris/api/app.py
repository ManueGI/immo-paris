from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from immo_paris.api.routes import health, sales, stats
from immo_paris.core.config import get_settings


def operation_id(route: APIRoute) -> str:
    # OpenAPI operationId = function name (list_sales, get_sale...): clean method names in the
    # TypeScript clients generated for Angular and React Native
    return route.name


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Immo Paris API", version="0.2.0", generate_unique_id_function=operation_id)

    # Angular (web) and React Native (mobile) front-ends
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(sales.router)
    app.include_router(stats.router)
    return app


app = create_app()
