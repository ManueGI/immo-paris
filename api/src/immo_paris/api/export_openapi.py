"""Export the API contract to openapi.json, the file the TypeScript clients are generated from.

The file is committed: contract changes show up in pull requests, and CI fails when it is
out of date or when a pull request breaks it.
"""

import json
import sys
from pathlib import Path
from typing import Any

from immo_paris.api.app import create_app

OPENAPI_FILE = Path("openapi.json")


def render_openapi() -> str:
    spec: dict[str, Any] = create_app().openapi()
    # Stable output (indentation, final newline) so that diffs only show real changes
    return json.dumps(spec, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    OPENAPI_FILE.write_text(render_openapi(), encoding="utf-8")
    print(f"API contract written to {OPENAPI_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
