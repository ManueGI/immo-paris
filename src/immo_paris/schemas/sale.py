import datetime
from enum import StrEnum

from pydantic import BaseModel


class PropertyType(StrEnum):
    APARTMENT = "apartment"
    HOUSE = "house"


class Sale(BaseModel):
    """Single-dwelling DVF sale, served to the web (Angular) and mobile (React Native) clients."""

    mutation_id: str
    date: datetime.date
    address: str
    postal_code: str | None
    property_type: PropertyType
    surface_m2: float
    rooms: int | None
    price: float
    price_per_m2: float
    longitude: float | None
    latitude: float | None
