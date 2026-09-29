from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration de l'application, lue depuis les variables d'environnement et le .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Serveur API
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    # Liste séparée par des virgules : "http://localhost:4200,http://localhost:8081"
    cors_origins: Annotated[list[str], NoDecode] = ["*"]

    # Base de données
    database_url: str | None = None

    # Données DVF
    dvf_base_url: str = "https://files.data.gouv.fr/geo-dvf/latest/csv"
    dvf_departement: str = "75"
    data_dir: Path = Path("data")
    sample_csv: Path = Path("data/dvf_paris_sample.csv")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
