import pytest

from immo_paris.schemas.commune import commune_label


@pytest.mark.parametrize(
    ("commune_code", "label"),
    [
        ("75101", "Paris 1er"),
        ("75102", "Paris 2e"),
        ("75111", "Paris 11e"),
        ("75120", "Paris 20e"),
    ],
)
def test_commune_label_names_paris_arrondissements(commune_code: str, label: str) -> None:
    assert commune_label(commune_code) == label


@pytest.mark.parametrize("commune_code", ["75100", "75121", "69381", "2A004"])
def test_commune_label_falls_back_to_the_code(commune_code: str) -> None:
    assert commune_label(commune_code) == commune_code
