import datetime

from pydantic import BaseModel


class Sale(BaseModel):
    """Vente DVF exposée aux clients web (Angular) et mobile (React Native)."""

    id_mutation: str
    date: datetime.date
    adresse: str
    code_postal: str | None
    type_bien: str
    surface: float
    nb_pieces: int | None
    prix: float
    prix_m2: float
    longitude: float | None
    latitude: float | None
