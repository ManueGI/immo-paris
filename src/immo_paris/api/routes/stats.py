from typing import Annotated

from fastapi import APIRouter, Query

from immo_paris.api.dependencies import StatsRepositoryDep
from immo_paris.schemas.sale import PropertyType
from immo_paris.schemas.stats import CommuneStats

router = APIRouter(prefix="/api/v1/stats", tags=["stats"])


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
