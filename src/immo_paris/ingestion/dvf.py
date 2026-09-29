"""Download and cleaning of DVF files (Demandes de Valeurs Foncières).

Source: https://files.data.gouv.fr/geo-dvf/latest/csv/<year>/departements/<dep>.csv.gz

DVF data model pitfall: a mutation (`id_mutation`) spans one row per lot (flat, cellar,
parking, shop, land parcel...) and `valeur_fonciere` is the *total* price of the mutation,
repeated on every row. A price per m² is therefore only meaningful for mutations containing
exactly one dwelling, whose other rows (if any) are outbuildings or bare land.
"""

import logging
import re
from pathlib import Path

import pandas as pd
import requests

logger = logging.getLogger(__name__)

TIMEOUT = 60

# DVF source column -> internal column
RAW_COLUMNS = {
    "id_mutation": "mutation_id",
    "date_mutation": "date",
    "nature_mutation": "mutation_type",
    "valeur_fonciere": "price",
    "adresse_numero": "street_number",
    "adresse_suffixe": "street_suffix",
    "adresse_nom_voie": "street_name",
    "code_postal": "postal_code",
    "type_local": "premises_type",
    "surface_reelle_bati": "surface_m2",
    "nombre_pieces_principales": "rooms",
    "longitude": "longitude",
    "latitude": "latitude",
}

# DVF domain values (kept in French, as published by the DGFiP)
SALE = "Vente"
DWELLING_TYPES = {"Appartement": "apartment", "Maison": "house"}
# Rows allowed alongside the dwelling: outbuildings (cellar, parking). Rows with no premises
# type are bare land parcels and are allowed too.
OUTBUILDING = "Dépendance"

# Plausible price range for Paris housing; outside of it, the record is almost always
# a data-entry error, a non-market transaction or a mis-typed mutation.
MIN_PRICE_PER_M2 = 3_000
MAX_PRICE_PER_M2 = 30_000

OUTPUT_COLUMNS = [
    "mutation_id",
    "date",
    "address",
    "postal_code",
    "property_type",
    "surface_m2",
    "rooms",
    "price",
    "price_per_m2",
    "longitude",
    "latitude",
]


def latest_year(base_url: str) -> str:
    """Return the most recent year available in the geo-dvf listing."""
    resp = requests.get(f"{base_url}/", timeout=TIMEOUT)
    resp.raise_for_status()
    years = re.findall(r'href="[^"]*/(\d{4})/"', resp.text)
    if not years:
        raise RuntimeError("Unable to determine the latest available DVF year.")
    return max(years)


def download(base_url: str, departement: str, year: str, data_dir: Path) -> Path:
    url = f"{base_url}/{year}/departements/{departement}.csv.gz"
    dest = data_dir / f"dvf_{departement}_{year}.csv.gz"
    data_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Downloading %s", url)
    with requests.get(url, stream=True, timeout=TIMEOUT) as resp:
        resp.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1 << 20):
                f.write(chunk)
    logger.info("Raw file saved: %s (%.1f MB)", dest, dest.stat().st_size / 1e6)
    return dest


def load_raw(path: Path) -> pd.DataFrame:
    """Read a geo-dvf CSV (optionally gzipped), keeping and renaming the useful columns."""
    return pd.read_csv(
        path,
        usecols=list(RAW_COLUMNS),
        dtype={
            "id_mutation": "string",
            "code_postal": "string",
            "adresse_numero": "string",
            "adresse_suffixe": "string",
        },
        low_memory=False,
    ).rename(columns=RAW_COLUMNS)


def keep_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Keep plain sales; exchanges, auctions and off-plan sales follow other price dynamics."""
    return df[df["mutation_type"] == SALE]


def keep_single_dwelling_mutations(df: pd.DataFrame) -> pd.DataFrame:
    """Return one row per mutation, for mutations made of exactly one dwelling.

    Other rows of the mutation may only be outbuildings or bare land; any extra dwelling or
    commercial premises would make the total price meaningless for that dwelling.
    """
    is_dwelling = df["premises_type"].isin(DWELLING_TYPES.keys())
    is_allowed_extra = df["premises_type"].isna() | (df["premises_type"] == OUTBUILDING)

    counts = (
        pd.DataFrame({"dwellings": is_dwelling, "blocking": ~(is_dwelling | is_allowed_extra)})
        .groupby(df["mutation_id"])
        .sum()
    )
    valid_ids = counts.index[(counts["dwellings"] == 1) & (counts["blocking"] == 0)]

    return df[is_dwelling & df["mutation_id"].isin(valid_ids)]


def to_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Build the public sale records: address, property type and price per m²."""
    df = df[df["price"].notna() & (df["surface_m2"] > 0)]

    # Human-readable address: "12 B RUE DE RIVOLI 75004"
    address = (
        df[["street_number", "street_suffix", "street_name", "postal_code"]]
        .fillna("")
        .astype(str)
        .agg(" ".join, axis=1)
        .str.split()
        .str.join(" ")
    )

    return df.assign(
        address=address,
        property_type=df["premises_type"].map(DWELLING_TYPES),
        price_per_m2=(df["price"] / df["surface_m2"]).round(0),
        rooms=df["rooms"].astype("Int64"),
    )[OUTPUT_COLUMNS]


def remove_price_outliers(
    df: pd.DataFrame,
    min_price_per_m2: float = MIN_PRICE_PER_M2,
    max_price_per_m2: float = MAX_PRICE_PER_M2,
) -> pd.DataFrame:
    return df[df["price_per_m2"].between(min_price_per_m2, max_price_per_m2)]


def clean(raw: pd.DataFrame, limit: int = 0) -> pd.DataFrame:
    """Run the full cleaning pipeline and log the row count after each step."""
    logger.info("%-32s %7d rows", "raw", len(raw))
    df = raw
    for step in (keep_sales, keep_single_dwelling_mutations, to_sales, remove_price_outliers):
        df = step(df)
        logger.info("%-32s %7d rows", step.__name__, len(df))

    df = df.sort_values(["date", "mutation_id"], ascending=False)
    return df.head(limit) if limit else df
