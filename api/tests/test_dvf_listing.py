from immo_paris.ingestion.dvf import parse_available_years

# Excerpt of https://files.data.gouv.fr/geo-dvf/latest/csv/ (directory listing page)
LISTING = """
<html><body><h1>Index of /geo-dvf/latest/csv/</h1>
<a href="/geo-dvf/latest/">../</a>
<a href="/geo-dvf/latest/csv/2023/">2023/</a>
<a href="/geo-dvf/latest/csv/2021/">2021/</a>
<a href="/geo-dvf/latest/csv/2025/">2025/</a>
<a href="/geo-dvf/latest/csv/2025/">2025/</a>
<a href="/geo-dvf/latest/csv/README.md">README.md</a>
</body></html>
"""


def test_parse_available_years_returns_unique_years_oldest_first() -> None:
    assert parse_available_years(LISTING) == ["2021", "2023", "2025"]


def test_parse_available_years_ignores_pages_without_years() -> None:
    assert parse_available_years("<html><body>Not found</body></html>") == []
