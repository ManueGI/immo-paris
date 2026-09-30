import json
from pathlib import Path

from immo_paris.api.export_openapi import render_openapi

OPENAPI_FILE = Path(__file__).parents[1] / "openapi.json"


def test_committed_contract_is_up_to_date() -> None:
    committed = OPENAPI_FILE.read_text(encoding="utf-8") if OPENAPI_FILE.exists() else ""

    assert committed == render_openapi(), (
        "openapi.json is out of date with the API code: run `uv run immo-openapi` and commit it"
    )


def test_not_found_response_is_documented() -> None:
    get_sale = json.loads(render_openapi())["paths"]["/api/v1/sales/{sale_id}"]["get"]

    assert get_sale["responses"]["404"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/ErrorResponse"
    }
