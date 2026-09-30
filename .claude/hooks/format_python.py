"""PostToolUse hook: format the Python file Claude just edited and report lint errors.

Claude Code sends the tool call as JSON on stdin. Exit code 2 feeds stderr back to Claude
so it fixes the reported problems. Runs with any Python 3 (no project dependencies), including
an old system python3: keep the syntax compatible with Python 3.8.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def find_python_project(file_path: Path) -> Path | None:
    """Closest parent directory with a pyproject.toml and an installed ruff (e.g. api/)."""
    for directory in file_path.parents:
        if (directory / "pyproject.toml").exists() and (directory / ".venv/bin/ruff").exists():
            return directory
    return None


def main() -> int:
    payload = json.load(sys.stdin)
    file_path = payload.get("tool_input", {}).get("file_path", "")
    if not file_path.endswith(".py"):
        return 0

    project = find_python_project(Path(file_path).resolve())
    if project is None:
        # Not in a Python project, or dependencies not installed yet (uv sync)
        return 0

    ruff = str(project / ".venv/bin/ruff")
    subprocess.run([ruff, "format", "--quiet", file_path], cwd=project, check=False)
    lint = subprocess.run(
        [ruff, "check", "--quiet", file_path],
        cwd=project,
        capture_output=True,
        text=True,
        check=False,
    )
    if lint.returncode != 0:
        print(lint.stdout + lint.stderr, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
