from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Connection
from sqlalchemy.exc import OperationalError

from immo_paris.api.app import create_app
from immo_paris.db.session import get_connection


def test_health_does_not_need_the_database() -> None:
    with TestClient(create_app()) as client:
        resp = client.get("/health")

    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_openapi_operation_ids_are_function_names() -> None:
    with TestClient(create_app()) as client:
        paths = client.get("/openapi.json").json()["paths"]

    assert paths["/api/v1/sales"]["get"]["operationId"] == "list_sales"
    assert paths["/api/v1/sales/{sale_id}"]["get"]["operationId"] == "get_sale"


def database_down() -> Iterator[Connection]:
    """What get_connection raises when PostgreSQL cannot be reached."""
    raise OperationalError("SELECT 1", {}, ConnectionRefusedError("Connection refused"))
    yield  # pragma: no cover  (makes this function a generator, like get_connection)


@pytest.mark.parametrize("path", ["/api/v1/sales", "/api/v1/stats/communes"])
def test_database_down_returns_503_with_cors_headers(path: str) -> None:
    app = create_app()
    app.dependency_overrides[get_connection] = database_down

    with TestClient(app) as client:
        resp = client.get(path, headers={"Origin": "http://localhost:4200"})

    # 503 (temporary) instead of 500, with CORS headers so that browsers show this error
    # instead of a misleading CORS one
    assert resp.status_code == 503
    assert resp.json() == {"detail": "The database is temporarily unavailable"}
    assert resp.headers["retry-after"] == "30"
    assert "access-control-allow-origin" in resp.headers
