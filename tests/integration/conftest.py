"""Fixtures for tests running against a real PostgreSQL + PostGIS database.

A dedicated `<database>_test` database is recreated from scratch at each test session and
built by running the Alembic migrations, so migrations are tested too. It requires the
database container: `docker compose up -d --wait`.
"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Connection, Engine, create_engine, make_url, text

from immo_paris.api.app import create_app
from immo_paris.core.config import get_settings
from immo_paris.db.session import get_connection
from immo_paris.ingestion.dvf import clean, load_raw
from immo_paris.ingestion.loader import DataSource, replace_year

PROJECT_ROOT = Path(__file__).parents[2]


@pytest.fixture(scope="session")
def db_engine() -> Iterator[Engine]:
    database_url = get_settings().database_url
    if database_url is None:
        pytest.fail("DATABASE_URL is not set: integration tests need the database container")
    url = make_url(database_url)
    test_url = url.set(database=f"{url.database}_test")

    # CREATE / DROP DATABASE cannot run inside a transaction: use an autocommit connection
    admin = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        conn.execute(text(f'DROP DATABASE IF EXISTS "{test_url.database}" WITH (FORCE)'))
        conn.execute(text(f'CREATE DATABASE "{test_url.database}"'))
    admin.dispose()

    engine = create_engine(test_url)
    config = Config(PROJECT_ROOT / "alembic.ini", toml_file=PROJECT_ROOT / "pyproject.toml")
    with engine.begin() as conn:
        config.attributes["connection"] = conn
        command.upgrade(config, "head")

    yield engine
    engine.dispose()


@pytest.fixture
def db(db_engine: Engine) -> Engine:
    """The test database, emptied before each test."""
    with db_engine.begin() as conn:
        conn.execute(text("TRUNCATE sales, ingestion_runs RESTART IDENTITY"))
        conn.execute(text("REFRESH MATERIALIZED VIEW commune_yearly_stats"))
    return db_engine


@pytest.fixture
def loaded_db(db: Engine, raw_dvf_csv: Path) -> Engine:
    """The test database loaded with the 3 clean sales of the hand-built DVF fixture."""
    result = clean(load_raw(raw_dvf_csv))
    source = DataSource(url="file:///tests/fixtures/dvf_raw.csv", sha256="0" * 64, year=2025)
    replace_year(db, result.sales, source, result.row_counts)
    return db


@pytest.fixture
def api(loaded_db: Engine) -> Iterator[TestClient]:
    """An API client whose requests read the loaded test database."""

    def connect_to_test_db() -> Iterator[Connection]:
        with loaded_db.connect() as connection:
            yield connection

    app = create_app()
    app.dependency_overrides[get_connection] = connect_to_test_db
    with TestClient(app) as client:
        yield client
