from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Connection, Engine, create_engine

from immo_paris.core.config import get_settings


@lru_cache
def get_engine() -> Engine:
    """Return the application's engine: one connection pool shared by the whole process."""
    url = get_settings().database_url
    if url is None:
        raise RuntimeError("DATABASE_URL is not set (see .env.example).")
    # pre_ping checks a pooled connection is still alive before using it
    return create_engine(url, pool_pre_ping=True)


def get_connection() -> Iterator[Connection]:
    """One connection per API request, returned to the pool when the request ends."""
    with get_engine().connect() as connection:
        yield connection
