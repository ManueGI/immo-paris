"""Opaque cursors for keyset pagination on (sale_date, id).

Clients get `next_cursor` from a page and send it back unchanged: the format can evolve
without breaking them.
"""

import base64
import binascii
from dataclasses import dataclass
from datetime import date


class InvalidCursorError(ValueError):
    pass


@dataclass(frozen=True)
class SaleCursor:
    """Position of the last sale of a page, in (sale_date DESC, id DESC) order."""

    sale_date: date
    id: int

    def encode(self) -> str:
        raw = f"{self.sale_date.isoformat()}:{self.id}".encode()
        return base64.urlsafe_b64encode(raw).decode()

    @classmethod
    def decode(cls, cursor: str) -> "SaleCursor":
        try:
            sale_date, sale_id = base64.urlsafe_b64decode(cursor).decode().split(":")
            return cls(sale_date=date.fromisoformat(sale_date), id=int(sale_id))
        except (binascii.Error, UnicodeDecodeError, ValueError) as error:
            raise InvalidCursorError(f"Invalid cursor: {cursor!r}") from error
