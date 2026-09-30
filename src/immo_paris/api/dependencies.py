"""FastAPI dependencies: how routes get their repositories (overridable in tests)."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy import Connection

from immo_paris.db.session import get_connection
from immo_paris.repositories.sales import SaleRepository
from immo_paris.repositories.stats import StatsRepository


def get_sale_repository(
    connection: Annotated[Connection, Depends(get_connection)],
) -> SaleRepository:
    return SaleRepository(connection)


def get_stats_repository(
    connection: Annotated[Connection, Depends(get_connection)],
) -> StatsRepository:
    return StatsRepository(connection)


SaleRepositoryDep = Annotated[SaleRepository, Depends(get_sale_repository)]
StatsRepositoryDep = Annotated[StatsRepository, Depends(get_stats_repository)]
