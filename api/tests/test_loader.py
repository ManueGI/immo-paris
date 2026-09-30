from datetime import date
from decimal import Decimal

import pandas as pd

from immo_paris.ingestion.loader import COPY_COLUMNS, point_ewkt, to_copy_rows


def sale(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "mutation_id": "2025-1",
        "date": "2025-03-01",
        "commune_code": "75104",
        "address": "12 B RUE DE RIVOLI 75004",
        "postal_code": "75004",
        "property_type": "apartment",
        "surface_m2": 50,
        "rooms": 2,
        "price": 123456.78,
        "price_per_m2": 2469.0,
        "longitude": 2.35,
        "latitude": 48.85,
    }
    return row | overrides


def test_point_ewkt_puts_longitude_first() -> None:
    assert point_ewkt(2.35, 48.85) == "SRID=4326;POINT(2.35 48.85)"


def test_point_ewkt_is_none_without_coordinates() -> None:
    assert point_ewkt(float("nan"), 48.85) is None
    assert point_ewkt(2.35, float("nan")) is None


def test_to_copy_rows_matches_copy_columns_with_database_types() -> None:
    sales = pd.DataFrame([sale()])

    [row] = to_copy_rows(sales, ingestion_run_id=7)

    assert dict(zip(COPY_COLUMNS, row, strict=True)) == {
        "mutation_id": "2025-1",
        "ingestion_run_id": 7,
        "sale_date": date(2025, 3, 1),
        "commune_code": "75104",
        "postal_code": "75004",
        "address": "12 B RUE DE RIVOLI 75004",
        "property_type": "apartment",
        "surface_m2": 50,
        "rooms": 2,
        "price": Decimal("123456.78"),
        "location": "SRID=4326;POINT(2.35 48.85)",
    }


def test_to_copy_rows_writes_missing_values_as_none() -> None:
    sales = pd.DataFrame([sale(postal_code=pd.NA, rooms=pd.NA, longitude=float("nan"))]).astype(
        {"postal_code": "string", "rooms": "Int64"}
    )

    [row] = to_copy_rows(sales, ingestion_run_id=7)
    values = dict(zip(COPY_COLUMNS, row, strict=True))

    assert values["postal_code"] is None
    assert values["rooms"] is None
    assert values["location"] is None
