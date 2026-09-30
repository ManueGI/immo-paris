import datetime
from enum import StrEnum

from pydantic import BaseModel, computed_field

from immo_paris.schemas.commune import commune_label


class PropertyType(StrEnum):
    APARTMENT = "apartment"
    HOUSE = "house"


class Sale(BaseModel):
    """Single-dwelling DVF sale, served to the web (Angular) and mobile (React Native) clients."""

    id: int
    mutation_id: str
    date: datetime.date
    commune_code: str
    address: str
    postal_code: str | None
    property_type: PropertyType
    surface_m2: int
    rooms: int | None
    # Whole euros: light for mobile clients, and exact enough for analytics
    price: int
    price_per_m2: int
    longitude: float | None
    latitude: float | None

    @computed_field
    @property
    def commune_label(self) -> str:
        return commune_label(self.commune_code)


class SalePage(BaseModel):
    """One page of sales. Pass `next_cursor` back as `cursor` to get the next page."""

    items: list[Sale]
    next_cursor: str | None


class NearbySale(Sale):
    distance_m: int
