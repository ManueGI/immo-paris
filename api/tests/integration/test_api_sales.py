"""Sales endpoints, against the test database loaded with the hand-built DVF fixture:

| mutation   | date       | commune | type      | surface | price     | €/m²   | lng, lat     |
| M-LAND     | 2025-06-15 | 75107   | apartment | 40      | 400,000   | 10,000 | 2.32, 48.85  |
| M-CELLAR   | 2025-03-01 | 75104   | apartment | 50      | 500,000   | 10,000 | 2.35, 48.85  |
| M-HOUSE    | 2025-01-10 | 75114   | house     | 100     | 1,500,000 | 15,000 | 2.33, 48.82  |
"""

from fastapi.testclient import TestClient


def mutation_ids(sales: list[dict[str, object]]) -> list[object]:
    return [sale["mutation_id"] for sale in sales]


def test_list_sales_returns_most_recent_first(api: TestClient) -> None:
    resp = api.get("/api/v1/sales")

    assert resp.status_code == 200
    page = resp.json()
    assert mutation_ids(page["items"]) == ["M-LAND", "M-CELLAR", "M-HOUSE"]
    assert page["next_cursor"] is None


def test_sale_json_is_light_and_typed(api: TestClient) -> None:
    sale = api.get("/api/v1/sales").json()["items"][1]

    assert sale == {
        "id": sale["id"],
        "mutation_id": "M-CELLAR",
        "date": "2025-03-01",
        "commune_code": "75104",
        "commune_label": "Paris 4e",
        "address": "12 B RUE DE RIVOLI 75004",
        "postal_code": "75004",
        "property_type": "apartment",
        "surface_m2": 50,
        "rooms": 2,
        "price": 500000,
        "price_per_m2": 10000,
        "longitude": 2.35,
        "latitude": 48.85,
    }


def test_list_sales_paginates_with_a_cursor(api: TestClient) -> None:
    first = api.get("/api/v1/sales", params={"limit": 2}).json()
    second = api.get("/api/v1/sales", params={"limit": 2, "cursor": first["next_cursor"]}).json()

    assert mutation_ids(first["items"]) == ["M-LAND", "M-CELLAR"]
    assert first["next_cursor"] is not None
    assert mutation_ids(second["items"]) == ["M-HOUSE"]
    assert second["next_cursor"] is None


def test_list_sales_filters_by_commune_and_property_type(api: TestClient) -> None:
    by_commune = api.get("/api/v1/sales", params={"commune_code": "75104"}).json()
    houses = api.get("/api/v1/sales", params={"property_type": "house"}).json()

    assert mutation_ids(by_commune["items"]) == ["M-CELLAR"]
    assert mutation_ids(houses["items"]) == ["M-HOUSE"]


def test_invalid_cursor_uses_the_standard_validation_error_body(api: TestClient) -> None:
    resp = api.get("/api/v1/sales", params={"cursor": "not-a-cursor"})

    assert resp.status_code == 422
    [error] = resp.json()["detail"]
    assert error["loc"] == ["query", "cursor"]


def test_list_sales_rejects_invalid_parameters(api: TestClient) -> None:
    assert api.get("/api/v1/sales", params={"limit": 101}).status_code == 422
    assert api.get("/api/v1/sales", params={"commune_code": "Paris"}).status_code == 422
    assert api.get("/api/v1/sales", params={"property_type": "castle"}).status_code == 422


def test_get_sale_by_id(api: TestClient) -> None:
    sale_id = api.get("/api/v1/sales").json()["items"][0]["id"]

    resp = api.get(f"/api/v1/sales/{sale_id}")

    assert resp.status_code == 200
    assert resp.json()["mutation_id"] == "M-LAND"


def test_get_unknown_sale_returns_404(api: TestClient) -> None:
    resp = api.get("/api/v1/sales/999999")

    assert resp.status_code == 404
    assert resp.json() == {"detail": "Sale 999999 not found"}


def test_nearby_returns_sales_within_radius_nearest_first(api: TestClient) -> None:
    # From M-CELLAR: M-LAND is about 2.2 km west, M-HOUSE about 3.6 km away
    resp = api.get("/api/v1/sales/nearby", params={"lat": 48.85, "lng": 2.35, "radius_m": 2500})

    assert resp.status_code == 200
    sales = resp.json()
    assert mutation_ids(sales) == ["M-CELLAR", "M-LAND"]
    assert sales[0]["distance_m"] == 0
    assert 2_100 < sales[1]["distance_m"] < 2_300


def test_nearby_is_not_mistaken_for_a_sale_id(api: TestClient) -> None:
    resp = api.get("/api/v1/sales/nearby", params={"lat": 48.85, "lng": 2.35})

    assert resp.status_code == 200


def test_nearby_validates_coordinates_and_radius(api: TestClient) -> None:
    point = {"lat": 48.85, "lng": 2.35}

    assert api.get("/api/v1/sales/nearby", params={"lng": 2.35}).status_code == 422
    assert api.get("/api/v1/sales/nearby", params={**point, "lat": 91}).status_code == 422
    assert api.get("/api/v1/sales/nearby", params={**point, "radius_m": 5001}).status_code == 422
