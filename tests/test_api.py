from fastapi.testclient import TestClient

from immo_paris.api.app import create_app


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
