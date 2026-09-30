"""Read access to sales. The only module of the API that knows how sales are stored."""

from geoalchemy2 import Geography, Geometry
from sqlalchemy import ColumnElement, Connection, Integer, Select, cast, func, select, tuple_

from immo_paris.db.models import Sale as SaleRow
from immo_paris.repositories.pagination import SaleCursor
from immo_paris.schemas.sale import NearbySale, PropertyType, Sale, SalePage

# Columns of the public Sale schema, computed by PostgreSQL
SALE_COLUMNS: tuple[ColumnElement[object], ...] = (
    SaleRow.id,
    SaleRow.mutation_id,
    SaleRow.sale_date.label("date"),
    SaleRow.commune_code,
    SaleRow.address,
    SaleRow.postal_code,
    SaleRow.property_type,
    SaleRow.surface_m2,
    SaleRow.rooms,
    cast(func.round(SaleRow.price), Integer).label("price"),
    SaleRow.price_per_m2,
    func.ST_X(cast(SaleRow.location, Geometry)).label("longitude"),
    func.ST_Y(cast(SaleRow.location, Geometry)).label("latitude"),
)


def select_sales() -> Select[tuple[object, ...]]:
    return select(*SALE_COLUMNS)


class SaleRepository:
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def list_recent(
        self,
        *,
        limit: int,
        cursor: SaleCursor | None = None,
        commune_code: str | None = None,
        property_type: PropertyType | None = None,
    ) -> SalePage:
        """Most recent sales first, paginated with a keyset cursor on (sale_date, id)."""
        query = select_sales().order_by(SaleRow.sale_date.desc(), SaleRow.id.desc())
        if cursor is not None:
            # Rows strictly after the last one of the previous page: uses ix_sales_recent
            query = query.where(
                tuple_(SaleRow.sale_date, SaleRow.id) < (cursor.sale_date, cursor.id)
            )
        if commune_code is not None:
            query = query.where(SaleRow.commune_code == commune_code)
        if property_type is not None:
            query = query.where(SaleRow.property_type == property_type)

        # Fetch one extra row to know whether another page exists, without a COUNT query
        rows = self._connection.execute(query.limit(limit + 1)).mappings().all()
        items = [Sale.model_validate(row) for row in rows[:limit]]
        has_next_page = len(rows) > limit
        next_cursor = (
            SaleCursor(sale_date=items[-1].date, id=items[-1].id).encode()
            if has_next_page
            else None
        )
        return SalePage(items=items, next_cursor=next_cursor)

    def get(self, sale_id: int) -> Sale | None:
        row = (
            self._connection.execute(select_sales().where(SaleRow.id == sale_id)).mappings().first()
        )
        return None if row is None else Sale.model_validate(row)

    def nearby(
        self, *, longitude: float, latitude: float, radius_m: int, limit: int
    ) -> list[NearbySale]:
        """Sales within `radius_m` metres of a point, nearest first."""
        # Longitude first: a point is (x, y). Casting to geography gives distances in metres.
        point = cast(func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326), Geography)
        distance = func.ST_Distance(SaleRow.location, point)
        query = (
            select(*SALE_COLUMNS, cast(func.round(distance), Integer).label("distance_m"))
            # ST_DWithin uses the GiST index ix_sales_location; ST_Distance alone would not
            .where(func.ST_DWithin(SaleRow.location, point, radius_m))
            .order_by(distance, SaleRow.id)
            .limit(limit)
        )
        rows = self._connection.execute(query).mappings().all()
        return [NearbySale.model_validate(row) for row in rows]
