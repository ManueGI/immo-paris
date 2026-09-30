from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def raw_dvf_csv() -> Path:
    return FIXTURES_DIR / "dvf_raw.csv"
