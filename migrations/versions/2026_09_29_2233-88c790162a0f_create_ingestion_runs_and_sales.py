"""create ingestion_runs and sales

Revision ID: 88c790162a0f
Revises:
Create Date: 2026-09-29 22:33:13.289095+00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from geoalchemy2 import Geography
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "88c790162a0f"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# Median, quartiles and volume of price per m² by commune, year and property type.
# Materialized: DVF data changes twice a year, so statistics are computed once per
# ingestion (REFRESH MATERIALIZED VIEW CONCURRENTLY) instead of on every request.
CREATE_COMMUNE_YEARLY_STATS = """
CREATE MATERIALIZED VIEW commune_yearly_stats AS
SELECT
    commune_code,
    extract(year FROM sale_date)::smallint AS year,
    property_type,
    count(*)::integer AS sales_count,
    round(percentile_cont(0.25) WITHIN GROUP (ORDER BY price_per_m2))::integer
        AS p25_price_per_m2,
    round(percentile_cont(0.5) WITHIN GROUP (ORDER BY price_per_m2))::integer
        AS median_price_per_m2,
    round(percentile_cont(0.75) WITHIN GROUP (ORDER BY price_per_m2))::integer
        AS p75_price_per_m2,
    round(avg(surface_m2))::integer AS avg_surface_m2
FROM sales
GROUP BY commune_code, year, property_type
"""


def upgrade() -> None:
    """Upgrade schema."""
    # Already installed in the postgis Docker image, but not on a fresh Amazon RDS database
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.create_table(
        "ingestion_runs",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("source_sha256", sa.String(length=64), nullable=False),
        sa.Column("data_year", sa.SmallInteger(), nullable=False),
        sa.Column("row_counts", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ingestion_runs")),
    )
    op.create_table(
        "sales",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("mutation_id", sa.Text(), nullable=False),
        sa.Column("ingestion_run_id", sa.BigInteger(), nullable=False),
        sa.Column("sale_date", sa.Date(), nullable=False),
        sa.Column("commune_code", sa.String(length=5), nullable=False),
        sa.Column("postal_code", sa.String(length=5), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("property_type", sa.Text(), nullable=False),
        sa.Column("surface_m2", sa.Integer(), nullable=False),
        sa.Column("rooms", sa.SmallInteger(), nullable=True),
        sa.Column("price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column(
            "price_per_m2",
            sa.Integer(),
            sa.Computed("round(price / surface_m2)::integer", persisted=True),
            nullable=False,
        ),
        sa.Column(
            "location",
            Geography(
                geometry_type="POINT",
                srid=4326,
                dimension=2,
                spatial_index=False,
                from_text="ST_GeogFromText",
                name="geography",
            ),
            nullable=True,
        ),
        sa.CheckConstraint(
            "commune_code ~ '^[0-9][0-9AB][0-9]{3}$'", name=op.f("ck_sales_commune_code_format")
        ),
        sa.CheckConstraint("postal_code ~ '^[0-9]{5}$'", name=op.f("ck_sales_postal_code_format")),
        sa.CheckConstraint(
            "property_type IN ('apartment', 'house')", name=op.f("ck_sales_property_type")
        ),
        sa.CheckConstraint("price > 0", name=op.f("ck_sales_price_positive")),
        sa.CheckConstraint("rooms >= 0", name=op.f("ck_sales_rooms_not_negative")),
        sa.CheckConstraint("surface_m2 > 0", name=op.f("ck_sales_surface_m2_positive")),
        sa.ForeignKeyConstraint(
            ["ingestion_run_id"],
            ["ingestion_runs.id"],
            name=op.f("fk_sales_ingestion_run_id_ingestion_runs"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sales")),
        sa.UniqueConstraint("mutation_id", name=op.f("uq_sales_mutation_id")),
    )
    op.create_index("ix_sales_commune", "sales", ["commune_code", "sale_date"], unique=False)
    op.create_index(
        "ix_sales_location", "sales", ["location"], unique=False, postgresql_using="gist"
    )
    op.create_index("ix_sales_recent", "sales", ["sale_date", "id"], unique=False)

    op.execute(CREATE_COMMUNE_YEARLY_STATS)
    # A unique index is required by REFRESH MATERIALIZED VIEW CONCURRENTLY
    op.create_index(
        "uq_commune_yearly_stats",
        "commune_yearly_stats",
        ["commune_code", "year", "property_type"],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP MATERIALIZED VIEW commune_yearly_stats")
    op.drop_index("ix_sales_recent", table_name="sales")
    op.drop_index("ix_sales_location", table_name="sales", postgresql_using="gist")
    op.drop_index("ix_sales_commune", table_name="sales")
    op.drop_table("sales")
    op.drop_table("ingestion_runs")
    # The postgis extension is kept: it may be used by other schemas of the database
