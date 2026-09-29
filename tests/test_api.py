from pathlib import Path

from fastapi.testclient import TestClient

from immo_paris.core.config import Settings, get_settings


def test_health(client: TestClient) -> None:
    resp = client.get("/health")

    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_sales_sample_returns_typed_records(client: TestClient) -> None:
    resp = client.get("/api/v1/sales/sample")

    assert resp.status_code == 200
    sales = resp.json()
    assert len(sales) == 2
    assert sales[0]["code_postal"] == "75014"
    assert sales[0]["nb_pieces"] == 2
    # Valeurs manquantes sérialisées en null, pas en NaN
    assert sales[1]["nb_pieces"] is None
    assert sales[1]["latitude"] is None


def test_sales_sample_missing_data_returns_503(client: TestClient, tmp_path: Path) -> None:
    missing = tmp_path / "absent.csv"
    client.app.dependency_overrides[get_settings] = lambda: Settings(sample_csv=missing)

    resp = client.get("/api/v1/sales/sample")

    assert resp.status_code == 503


def test_cors_origins_parsed_from_comma_separated_string() -> None:
    settings = Settings(cors_origins="http://localhost:4200, http://localhost:8081")

    assert settings.cors_origins == ["http://localhost:4200", "http://localhost:8081"]
