from pathlib import Path

import pandas as pd
import pytest

from immo_paris.ingestion.dvf import (
    OUTPUT_COLUMNS,
    clean,
    dataset_year,
    keep_sales,
    keep_single_dwelling_mutations,
    load_raw,
    remove_price_outliers,
)


@pytest.fixture
def raw(raw_dvf_csv: Path) -> pd.DataFrame:
    return load_raw(raw_dvf_csv)


@pytest.fixture
def sales(raw: pd.DataFrame) -> pd.DataFrame:
    return clean(raw).sales.set_index("mutation_id")


def test_keeps_only_valid_single_dwelling_sales(sales: pd.DataFrame) -> None:
    assert set(sales.index) == {"M-CELLAR", "M-LAND", "M-HOUSE"}


def test_output_has_one_row_per_mutation_with_public_columns(raw: pd.DataFrame) -> None:
    df = clean(raw).sales

    assert list(df.columns) == OUTPUT_COLUMNS
    assert df["mutation_id"].is_unique


def test_outbuilding_does_not_affect_price_per_m2(sales: pd.DataFrame) -> None:
    flat = sales.loc["M-CELLAR"]

    assert flat["surface_m2"] == 50
    assert flat["price"] == 500_000
    assert flat["price_per_m2"] == 10_000


def test_builds_address_and_maps_property_type(sales: pd.DataFrame) -> None:
    assert sales.loc["M-CELLAR", "address"] == "12 B RUE DE RIVOLI 75004"
    assert sales.loc["M-LAND", "address"] == "5 RUE DU BAC 75007"
    assert sales.loc["M-CELLAR", "property_type"] == "apartment"
    assert sales.loc["M-HOUSE", "property_type"] == "house"


def test_keeps_insee_commune_code(sales: pd.DataFrame) -> None:
    assert sales.loc["M-CELLAR", "commune_code"] == "75104"


def test_keep_sales_drops_other_mutation_types(raw: pd.DataFrame) -> None:
    mutation_ids = set(keep_sales(raw)["mutation_id"])

    assert "M-EXCHANGE" not in mutation_ids
    assert "M-OFF-PLAN" not in mutation_ids


@pytest.mark.parametrize(
    "mutation_id",
    [
        "M-TWO-FLATS",  # two dwellings sharing one total price
        "M-BUILDING",  # identical rows are distinct unnumbered flats, not duplicates
        "M-SHOP",  # commercial premises included in the price
        "M-PARKING-ONLY",  # no dwelling at all
    ],
)
def test_single_dwelling_filter_excludes_mixed_mutations(
    raw: pd.DataFrame, mutation_id: str
) -> None:
    kept = keep_single_dwelling_mutations(keep_sales(raw))

    assert mutation_id not in set(kept["mutation_id"])


def test_single_dwelling_filter_keeps_only_the_dwelling_row(raw: pd.DataFrame) -> None:
    kept = keep_single_dwelling_mutations(keep_sales(raw))

    assert len(kept[kept["mutation_id"] == "M-CELLAR"]) == 1
    assert kept.loc[kept["mutation_id"] == "M-CELLAR", "premises_type"].item() == "Appartement"


@pytest.mark.parametrize("mutation_id", ["M-NO-SURFACE", "M-NO-PRICE"])
def test_drops_sales_without_price_or_surface(sales: pd.DataFrame, mutation_id: str) -> None:
    assert mutation_id not in sales.index


def test_remove_price_outliers_keeps_bounds_inclusive() -> None:
    df = pd.DataFrame({"price_per_m2": [2_999, 3_000, 15_000, 30_000, 30_001]})

    kept = remove_price_outliers(df, min_price_per_m2=3_000, max_price_per_m2=30_000)

    assert kept["price_per_m2"].tolist() == [3_000, 15_000, 30_000]


@pytest.mark.parametrize("mutation_id", ["M-TOO-CHEAP", "M-TOO-EXPENSIVE"])
def test_clean_drops_price_outliers(sales: pd.DataFrame, mutation_id: str) -> None:
    assert mutation_id not in sales.index


def test_clean_records_row_count_after_each_step(raw: pd.DataFrame) -> None:
    row_counts = clean(raw).row_counts

    assert row_counts == {
        "raw": 18,
        "keep_sales": 16,  # minus exchange and off-plan sale
        "keep_single_dwelling_mutations": 7,  # one row per single-dwelling mutation
        "to_sales": 5,  # minus missing surface and missing price
        "remove_price_outliers": 3,  # minus too cheap and too expensive
    }


def test_dataset_year_returns_the_single_year(raw: pd.DataFrame) -> None:
    assert dataset_year(raw) == 2025


def test_dataset_year_rejects_a_file_spanning_several_years() -> None:
    raw = pd.DataFrame({"date": ["2024-12-31", "2025-01-01"]})

    with pytest.raises(ValueError, match="single year"):
        dataset_year(raw)
