"""Tests for check_commit_msg.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from check_commit_msg import check  # noqa: E402

TRAILER = "Claude-session: 368d5791-4132-443f-8f46-b634c2d0d483"
LOG = ["2026-09/LOG.md"]


def test_valid_log_commit():
    assert check(f"Log: Add retry logic\n\n{TRAILER}\n", LOG) == []


def test_log_commit_across_months():
    assert check(f"Log: Add retry logic\n\n{TRAILER}\n", ["2026-09/LOG.md", "2026-10/LOG.md"]) == []


def test_log_commit_missing_prefix():
    errors = check(f"Add retry logic\n\n{TRAILER}\n", LOG)
    assert len(errors) == 1
    assert "'Log: Add retry logic'" in errors[0]
    assert "docs/agent-entries.md#committing" in errors[0]


def test_log_commit_missing_trailer():
    errors = check("Log: Add retry logic\n", LOG)
    assert len(errors) == 1
    assert "session trailer" in errors[0]


def test_kimi_trailer_accepted():
    assert check("Log: Add retry logic\n\nKimi-Code-session: 4a6c613c-a29a\n", LOG) == []


def test_prefix_on_non_log_commit():
    errors = check(f"Log: Add retry logic\n\n{TRAILER}\n", ["2026-09/LOG.md", "scripts/lint.py"])
    assert len(errors) == 1
    assert "scripts/lint.py" in errors[0]


def test_normal_commit_unaffected():
    assert check("Tighten lint rules\n\nBody.\n", ["scripts/lint.py"]) == []


def test_mixed_commit_without_prefix_allowed():
    assert check("Rename header format\n", ["2026-09/LOG.md", "docs/journal-format.md"]) == []


def test_comment_lines_ignored():
    assert check(f"# Please enter the commit message\nLog: Add retry logic\n\n{TRAILER}\n", LOG) == []


def test_no_files():
    assert check("Empty commit\n", []) == []
