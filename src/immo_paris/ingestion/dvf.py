"""Téléchargement et nettoyage des fichiers DVF (Demandes de Valeurs Foncières).

Source : https://files.data.gouv.fr/geo-dvf/latest/csv/<année>/departements/<dep>.csv.gz
"""

import re
from pathlib import Path

import pandas as pd
import requests

# Colonnes source DVF -> colonnes de sortie
COLUMNS = {
    "id_mutation": "id_mutation",
    "date_mutation": "date",
    "nature_mutation": "nature_mutation",
    "valeur_fonciere": "prix",
    "adresse_numero": "adresse_numero",
    "adresse_suffixe": "adresse_suffixe",
    "adresse_nom_voie": "adresse_voie",
    "code_postal": "code_postal",
    "type_local": "type_bien",
    "surface_reelle_bati": "surface",
    "nombre_pieces_principales": "nb_pieces",
    "longitude": "longitude",
    "latitude": "latitude",
}

TIMEOUT = 60


def latest_year(base_url: str) -> str:
    """Retourne la dernière année disponible dans le listing geo-dvf."""
    resp = requests.get(f"{base_url}/", timeout=TIMEOUT)
    resp.raise_for_status()
    years = re.findall(r'href="[^"]*/(\d{4})/"', resp.text)
    if not years:
        raise RuntimeError("Impossible de déterminer la dernière année DVF disponible.")
    return max(years)


def download(base_url: str, departement: str, year: str, data_dir: Path) -> Path:
    url = f"{base_url}/{year}/departements/{departement}.csv.gz"
    dest = data_dir / f"dvf_{departement}_{year}.csv.gz"
    data_dir.mkdir(parents=True, exist_ok=True)

    print(f"Téléchargement de {url}")
    with requests.get(url, stream=True, timeout=TIMEOUT) as resp:
        resp.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1 << 20):
                f.write(chunk)
    print(f"Fichier brut sauvegardé : {dest} ({dest.stat().st_size / 1e6:.1f} Mo)")
    return dest


def clean(raw_path: Path, limit: int) -> pd.DataFrame:
    df = pd.read_csv(
        raw_path,
        usecols=list(COLUMNS),
        dtype={"code_postal": "string", "adresse_numero": "string", "adresse_suffixe": "string"},
        low_memory=False,
    ).rename(columns=COLUMNS)

    # On garde uniquement les ventes de logements avec prix et surface renseignés
    df = df[
        (df["nature_mutation"] == "Vente")
        & df["type_bien"].isin(["Appartement", "Maison"])
        & df["prix"].notna()
        & (df["surface"] > 0)
    ]

    # Adresse lisible : "12 B RUE DE RIVOLI 75004"
    df["adresse"] = (
        df[["adresse_numero", "adresse_suffixe", "adresse_voie", "code_postal"]]
        .fillna("")
        .astype(str)
        .agg(" ".join, axis=1)
        .str.split()
        .str.join(" ")
    )
    df["prix_m2"] = (df["prix"] / df["surface"]).round(0)
    df["nb_pieces"] = df["nb_pieces"].astype("Int64")

    df = df[
        [
            "id_mutation",
            "date",
            "adresse",
            "code_postal",
            "type_bien",
            "surface",
            "nb_pieces",
            "prix",
            "prix_m2",
            "longitude",
            "latitude",
        ]
    ].sort_values("date", ascending=False)

    return df.head(limit) if limit else df
