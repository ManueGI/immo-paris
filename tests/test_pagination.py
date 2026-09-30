from datetime import date

import pytest

from immo_paris.repositories.pagination import InvalidCursorError, SaleCursor


def test_cursor_round_trips() -> None:
    cursor = SaleCursor(sale_date=date(2025, 3, 1), id=42)

    assert SaleCursor.decode(cursor.encode()) == cursor


def test_cursor_is_url_safe() -> None:
    encoded = SaleCursor(sale_date=date(2025, 3, 1), id=42).encode()

    assert set(encoded) <= set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_=")


@pytest.mark.parametrize("cursor", ["not-base64!", "Zm9v", "MjAyNS0xMy0wMTo0Mg==", ""])
def test_invalid_cursor_is_rejected(cursor: str) -> None:
    with pytest.raises(InvalidCursorError):
        SaleCursor.decode(cursor)
