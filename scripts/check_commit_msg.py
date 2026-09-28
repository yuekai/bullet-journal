"""commit-msg hook: journal-entry commits need a `Log: ` subject and a session trailer.

Keeps `git log --oneline` readable: a change and the journal entry logging it
would otherwise share a subject.
"""

import re
import subprocess
import sys
from pathlib import Path

LOG_PATH_RE = re.compile(r"^\d{4}-\d{2}/LOG\.md$")
TRAILER_RE = re.compile(r"^[A-Z][A-Za-z]*(?:-[A-Z][A-Za-z]*)*-session: \S+$", re.MULTILINE)
PREFIX = "Log: "
DOC = "docs/agent-entries.md#committing"


def check(message: str, files: list[str]) -> list[str]:
    """Return errors for a commit `message` that changes `files`."""
    lines = [l for l in message.split("\n") if not l.startswith("#")]
    subject = next((l for l in lines if l.strip()), "")
    body = "\n".join(lines)
    if not files:
        return []
    only_logs = all(LOG_PATH_RE.match(f) for f in files)
    errors = []
    if only_logs:
        if not subject.startswith(PREFIX):
            errors.append(f"journal-entry commits need a '{PREFIX}' subject prefix, "
                          f"e.g. '{PREFIX}{subject.strip() or '<entry subject>'}'")
        if not TRAILER_RE.search(body):
            errors.append("journal-entry commits need your session trailer, e.g. -m 'Claude-session: <uuid>'")
    elif subject.startswith(PREFIX):
        others = [f for f in files if not LOG_PATH_RE.match(f)]
        errors.append(f"'{PREFIX}' is only for commits that touch nothing but YYYY-MM/LOG.md files; "
                      f"commit {', '.join(others)} separately without the prefix")
    return [f"{e} (see {DOC})" for e in errors]


def main() -> int:
    message = Path(sys.argv[1]).read_text()
    files = subprocess.run(
        ["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, check=True
    ).stdout.split()
    errors = check(message, files)
    for e in errors:
        print(f"commit-msg: {e}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
