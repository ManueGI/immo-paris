from pydantic import BaseModel, computed_field

from immo_paris.schemas.commune import commune_label
from immo_paris.schemas.sale import PropertyType


class CommuneStats(BaseModel):
    """Price per m² statistics of one commune for one year and property type.

    Price statistics are null when `sales_count` is too low to be meaningful.
    """

    commune_code: str
    year: int
    property_type: PropertyType
    sales_count: int
    p25_price_per_m2: int | None
    median_price_per_m2: int | None
    p75_price_per_m2: int | None
    avg_surface_m2: int | None

    @computed_field
    @property
    def commune_label(self) -> str:
        return commune_label(self.commune_code)
