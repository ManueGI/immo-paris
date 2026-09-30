"""PostToolUse hook: format the Python file Claude just edited and report lint errors.

Claude Code sends the tool call as JSON on stdin. Exit code 2 feeds stderr back to Claude
so it fixes the reported problems. Runs with any Python 3 (no project dependencies).
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    payload = json.load(sys.stdin)
    file_path = payload.get("tool_input", {}).get("file_path", "")
    if not file_path.endswith(".py"):
        return 0

    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
    ruff = project_dir / ".venv" / "bin" / "ruff"
    if not ruff.exists():
        # Dependencies not installed yet (uv sync): nothing to run
        return 0

    subprocess.run([str(ruff), "format", "--quiet", file_path], cwd=project_dir, check=False)
    lint = subprocess.run(
        [str(ruff), "check", "--quiet", file_path],
        cwd=project_dir,
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
