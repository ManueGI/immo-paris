from fastapi.testclient import TestClient
from sqlalchemy import Engine

from immo_paris.repositories.stats import StatsRepository
from immo_paris.schemas.sale import PropertyType


def test_commune_stats_hide_prices_computed_on_too_few_sales(api: TestClient) -> None:
    resp = api.get("/api/v1/stats/communes", params={"property_type": "apartment"})

    assert resp.status_code == 200
    stats = resp.json()
    # The fixture has a single sale per commune: counts are published, prices are not
    assert stats[0] == {
        "commune_code": "75104",
        "commune_label": "Paris 4e",
        "year": 2025,
        "property_type": "apartment",
        "sales_count": 1,
        "p25_price_per_m2": None,
        "median_price_per_m2": None,
        "p75_price_per_m2": None,
        "avg_surface_m2": None,
    }


def test_commune_stats_default_to_the_latest_year(api: TestClient) -> None:
    stats = api.get("/api/v1/stats/communes").json()

    assert {row["year"] for row in stats} == {2025}
    assert [row["commune_code"] for row in stats] == ["75104", "75107", "75114"]


def test_commune_stats_of_a_year_without_data_are_empty(api: TestClient) -> None:
    assert api.get("/api/v1/stats/communes", params={"year": 2020}).json() == []


def test_stats_repository_publishes_prices_above_the_threshold(loaded_db: Engine) -> None:
    with loaded_db.connect() as connection:
        [stats] = StatsRepository(connection).commune_yearly(
            year=2025, property_type=PropertyType.HOUSE, min_sales=1
        )

    assert stats.commune_code == "75114"
    assert stats.median_price_per_m2 == 15_000
    assert stats.avg_surface_m2 == 100
