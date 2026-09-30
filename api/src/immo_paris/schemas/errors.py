from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Body of 4xx/5xx errors raised by the API (except 422 validation errors)."""

    detail: str
