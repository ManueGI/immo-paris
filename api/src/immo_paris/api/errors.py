"""Exception handlers: turn infrastructure failures into clear HTTP responses."""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

from immo_paris.schemas.errors import ErrorResponse

logger = logging.getLogger(__name__)

# Seconds a client should wait before retrying (sent as the Retry-After header)
RETRY_AFTER_SECONDS = 30

DATABASE_UNAVAILABLE = {
    503: {
        "model": ErrorResponse,
        "description": "The database is temporarily unavailable",
        "headers": {
            "Retry-After": {
                "description": "Seconds to wait before retrying",
                "schema": {"type": "integer"},
            }
        },
    }
}


async def database_unavailable(request: Request, exc: Exception) -> JSONResponse:
    # Logged for operators; clients get a stable message without connection details
    logger.error("Database unavailable on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=503,
        content=ErrorResponse(detail="The database is temporarily unavailable").model_dump(),
        headers={"Retry-After": str(RETRY_AFTER_SECONDS)},
    )


def register_error_handlers(app: FastAPI) -> None:
    # Handlers run inside the middleware stack, so their responses get CORS headers;
    # an unhandled exception becomes a bare 500 that browsers report as a CORS error
    app.add_exception_handler(OperationalError, database_unavailable)
