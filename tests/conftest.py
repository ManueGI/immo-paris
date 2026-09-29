from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from immo_paris.api.app import create_app
from immo_paris.core.config import Settings, get_settings

SAMPLE_CSV = """\
id_mutation,date,adresse,code_postal,type_bien,surface,nb_pieces,prix,prix_m2,longitude,latitude
2025-1,2025-12-31,13 VLA SEURAT 75014,75014,Appartement,26.0,2,375000.0,14423.0,2.333091,48.826023
2025-2,2025-12-30,1 RUE X 75001,75001,Appartement,40.0,,500000.0,12500.0,,
"""


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    path = tmp_path / "sample.csv"
    path.write_text(SAMPLE_CSV)
    return path


@pytest.fixture
def client(sample_csv: Path) -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: Settings(sample_csv=sample_csv)
    with TestClient(app) as test_client:
        yield test_client
