from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from immo_paris.api.app import create_app
from immo_paris.core.config import Settings, get_settings

FIXTURES_DIR = Path(__file__).parent / "fixtures"

SAMPLE_CSV = """\
mutation_id,date,address,postal_code,property_type,surface_m2,rooms,price,price_per_m2,longitude,latitude
2025-1,2025-12-31,13 VLA SEURAT 75014,75014,apartment,26.0,2,375000.0,14423.0,2.333091,48.826023
2025-2,2025-12-30,1 RUE X 75001,75001,house,40.0,,500000.0,12500.0,,
"""


@pytest.fixture
def raw_dvf_csv() -> Path:
    return FIXTURES_DIR / "dvf_raw.csv"


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
