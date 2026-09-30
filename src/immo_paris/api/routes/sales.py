from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from immo_paris.api.dependencies import SaleRepositoryDep
from immo_paris.repositories.pagination import InvalidCursorError, SaleCursor
from immo_paris.schemas.sale import NearbySale, PropertyType, Sale, SalePage

router = APIRouter(prefix="/api/v1/sales", tags=["sales"])

CommuneCode = Annotated[
    str, Query(pattern=r"^[0-9][0-9AB][0-9]{3}$", description="INSEE code, e.g. 75111")
]


@router.get("", response_model=SalePage)
def list_sales(
    sales: SaleRepositoryDep,
    commune_code: CommuneCode | None = None,
    property_type: PropertyType | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    cursor: Annotated[str | None, Query(description="next_cursor of the previous page")] = None,
) -> SalePage:
    """Most recent sales first, one page at a time."""
    try:
        position = SaleCursor.decode(cursor) if cursor is not None else None
    except InvalidCursorError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return sales.list_recent(
        limit=limit, cursor=position, commune_code=commune_code, property_type=property_type
    )


# Declared before /{sale_id}: fixed paths must come first
@router.get("/nearby", response_model=list[NearbySale])
def list_nearby_sales(
    sales: SaleRepositoryDep,
    lat: Annotated[float, Query(ge=-90, le=90, description="Latitude (WGS 84)")],
    lng: Annotated[float, Query(ge=-180, le=180, description="Longitude (WGS 84)")],
    radius_m: Annotated[int, Query(ge=1, le=5_000, description="Search radius in metres")] = 500,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[NearbySale]:
    """Sales around a point, nearest first."""
    return sales.nearby(longitude=lng, latitude=lat, radius_m=radius_m, limit=limit)


@router.get("/{sale_id}", response_model=Sale)
def get_sale(sale_id: int, sales: SaleRepositoryDep) -> Sale:
    sale = sales.get(sale_id)
    if sale is None:
        raise HTTPException(status_code=404, detail=f"Sale {sale_id} not found")
    return sale
