"""Database tables, described as Python classes (SQLAlchemy ORM).

These classes are the source of truth for the schema: Alembic compares them with the
database to generate migrations.
"""

from datetime import date, datetime
from decimal import Decimal

from geoalchemy2 import Geography, WKBElement
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Computed,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from immo_paris.db.base import Base


class IngestionRun(Base):
    """One execution of the DVF ingestion: which file produced which data."""

    __tablename__ = "ingestion_runs"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    source_url: Mapped[str] = mapped_column(Text)
    source_sha256: Mapped[str] = mapped_column(String(64))
    data_year: Mapped[int] = mapped_column(SmallInteger)
    # Row count after each cleaning step, e.g. {"raw": 84440, "keep_sales": 83447, ...}
    row_counts: Mapped[dict[str, int]] = mapped_column(JSONB)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Sale(Base):
    """A single-dwelling DVF sale (one row per mutation)."""

    __tablename__ = "sales"
    __table_args__ = (
        CheckConstraint("property_type IN ('apartment', 'house')", name="property_type"),
        CheckConstraint("surface_m2 > 0", name="surface_m2_positive"),
        CheckConstraint("rooms >= 0", name="rooms_not_negative"),
        CheckConstraint("price > 0", name="price_positive"),
        # INSEE code: 5 characters, "2A"/"2B" prefixes for Corsica
        CheckConstraint("commune_code ~ '^[0-9][0-9AB][0-9]{3}$'", name="commune_code_format"),
        CheckConstraint("postal_code ~ '^[0-9]{5}$'", name="postal_code_format"),
        # Most recent sales first, with id as tie-breaker (cursor pagination)
        Index("ix_sales_recent", "sale_date", "id"),
        # Sales of one commune, most recent first
        Index("ix_sales_commune", "commune_code", "sale_date"),
        # Spatial queries ("sales within 500 m")
        Index("ix_sales_location", "location", postgresql_using="gist"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    mutation_id: Mapped[str] = mapped_column(Text, unique=True)
    ingestion_run_id: Mapped[int] = mapped_column(ForeignKey("ingestion_runs.id"))
    sale_date: Mapped[date]
    commune_code: Mapped[str] = mapped_column(String(5))
    # Missing for a few DVF sales; commune_code is the reliable administrative area
    postal_code: Mapped[str | None] = mapped_column(String(5))
    address: Mapped[str] = mapped_column(Text)
    property_type: Mapped[str] = mapped_column(Text)
    surface_m2: Mapped[int] = mapped_column(Integer)
    rooms: Mapped[int | None] = mapped_column(SmallInteger)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    # Computed by PostgreSQL from price and surface: can never be inconsistent.
    # Generated columns are computed before CHECK constraints are evaluated, so a zero
    # surface is rejected with "division by zero" rather than by ck_sales_surface_m2_positive.
    price_per_m2: Mapped[int] = mapped_column(
        Integer, Computed("round(price / surface_m2)::integer", persisted=True)
    )
    # WGS 84 (GPS) point; nullable because some sales are not geocoded
    location: Mapped[WKBElement | None] = mapped_column(
        Geography("POINT", srid=4326, spatial_index=False)
    )
