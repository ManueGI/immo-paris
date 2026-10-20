from typing import Annotated

from fastapi import APIRouter, Path, Query

from immo_paris.api.dependencies import StatsRepositoryDep
from immo_paris.api.errors import DATABASE_UNAVAILABLE
from immo_paris.schemas.sale import PropertyType
from immo_paris.schemas.stats import CommuneStats

router = APIRouter(prefix="/api/v1/stats", tags=["stats"], responses=DATABASE_UNAVAILABLE)


@router.get("/communes", response_model=list[CommuneStats])
def list_commune_stats(
    stats: StatsRepositoryDep,
    year: Annotated[int | None, Query(ge=2000, description="Default: latest year")] = None,
    property_type: PropertyType | None = None,
) -> list[CommuneStats]:
    """Price per m² statistics by commune (arrondissement) for one year."""
    year = year if year is not None else stats.latest_year()
    if year is None:
        return []
    return stats.commune_yearly(year=year, property_type=property_type)


@router.get("/communes/{commune_code}/history", response_model=list[CommuneStats])
def get_commune_price_history(
    stats: StatsRepositoryDep,
    commune_code: Annotated[str, Path(pattern=r"^[0-9][0-9AB][0-9]{3}$")],
    property_type: PropertyType | None = None,
) -> list[CommuneStats]:
    """Price per m² statistics of one commune for every year, oldest first."""
    return stats.commune_history(commune_code=commune_code, property_type=property_type)
