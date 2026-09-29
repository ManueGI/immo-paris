"""Alembic environment: connects to the database and runs the migrations."""

from logging.config import fileConfig

from alembic import context
from geoalchemy2 import alembic_helpers
from sqlalchemy import create_engine, pool

from immo_paris.core.config import get_settings
from immo_paris.db import models  # noqa: F401  (registers the tables on Base.metadata)
from immo_paris.db.base import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def database_url() -> str:
    url = get_settings().database_url
    if url is None:
        raise RuntimeError("DATABASE_URL is not set (see .env.example).")
    return url


def include_name(name: str | None, type_: str, parent_names: dict[str, str | None]) -> bool:
    # Only compare the tables we own: PostGIS creates its own ones (e.g. spatial_ref_sys)
    # that autogenerate would otherwise propose to drop
    if type_ == "table":
        return name in target_metadata.tables
    return True


def configure(**kwargs: object) -> None:
    context.configure(
        target_metadata=target_metadata,
        include_name=include_name,
        # Render GeoAlchemy2 types correctly in generated migrations
        render_item=alembic_helpers.render_item,
        **kwargs,
    )


def run_migrations_offline() -> None:
    """Print the SQL to stdout instead of running it (alembic upgrade --sql)."""
    configure(url=database_url(), literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(database_url(), poolclass=pool.NullPool)
    with engine.connect() as connection:
        configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
