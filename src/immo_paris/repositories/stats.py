"""Read access to the pre-computed statistics (commune_yearly_stats materialized view)."""

from sqlalchemy import ColumnClause, Connection, Label, case, column, func, select, table

from immo_paris.schemas.sale import PropertyType
from immo_paris.schemas.stats import CommuneStats

# Below this number of sales, a median or quartile is too noisy to be published
MIN_SALES_FOR_STATS = 10

# Materialized views are not ORM models: describe the columns we read
commune_yearly_stats = table(
    "commune_yearly_stats",
    column("commune_code"),
    column("year"),
    column("property_type"),
    column("sales_count"),
    column("p25_price_per_m2"),
    column("median_price_per_m2"),
    column("p75_price_per_m2"),
    column("avg_surface_m2"),
)


class StatsRepository:
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def latest_year(self) -> int | None:
        return self._connection.execute(select(func.max(commune_yearly_stats.c.year))).scalar()

    def commune_yearly(
        self,
        *,
        year: int,
        property_type: PropertyType | None = None,
        min_sales: int = MIN_SALES_FOR_STATS,
    ) -> list[CommuneStats]:
        stats = commune_yearly_stats.c
        reliable = stats.sales_count >= min_sales

        def published(value_column: ColumnClause[object]) -> Label[object]:
            return case((reliable, value_column), else_=None).label(value_column.name)

        query = (
            select(
                stats.commune_code,
                stats.year,
                stats.property_type,
                stats.sales_count,
                published(stats.p25_price_per_m2),
                published(stats.median_price_per_m2),
                published(stats.p75_price_per_m2),
                published(stats.avg_surface_m2),
            )
            .where(stats.year == year)
            .order_by(stats.commune_code, stats.property_type)
        )
        if property_type is not None:
            query = query.where(stats.property_type == property_type)

        rows = self._connection.execute(query).mappings().all()
        return [CommuneStats.model_validate(row) for row in rows]
