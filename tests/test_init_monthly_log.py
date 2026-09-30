"""Tests for init_monthly_log.py"""

import subprocess
import sys
import tempfile
from pathlib import Path


def run_script(
    args: list[str],
    output_root: Path | None = None,
) -> tuple[subprocess.CompletedProcess, str]:
    """Run the script and return (process result, file content or empty string)."""
    cmd = [sys.executable, "scripts/init_monthly_log.py", *args]
    if output_root is not None:
        cmd.extend(["--output-root", str(output_root)])
    result = subprocess.run(cmd, capture_output=True, text=True)
    content = ""
    if result.returncode == 0 and output_root is not None:
        out_path = Path(result.stdout.strip())
        if out_path.exists():
            content = out_path.read_text()
    return result, content


def test_april_2026():
    """April 2026 has 30 days, starts on Wednesday."""
    with tempfile.TemporaryDirectory() as td:
        result, output = run_script(["2026-04"], Path(td))
        assert result.returncode == 0
        assert output.startswith("# April 2026\n")
        assert "**Calendar:**" in output
        assert "**Tasks:**" in output
        assert "\n1 W\n" in output
        assert "\n30 Th\n" in output
        day_lines = [l for l in output.split("\n") if l and l[0].isdigit()]
        assert len(day_lines) == 30


def test_february_2028_leap_year():
    """February 2028 is a leap year — 29 days."""
    with tempfile.TemporaryDirectory() as td:
        result, output = run_script(["2028-02"], Path(td))
        assert result.returncode == 0
        assert "# February 2028" in output
        day_lines = [l for l in output.split("\n") if l and l[0].isdigit()]
        assert len(day_lines) == 29
        assert "\n29 Tu\n" in output


def test_february_2027_non_leap():
    """February 2027 is not a leap year — 28 days."""
    with tempfile.TemporaryDirectory() as td:
        result, output = run_script(["2027-02"], Path(td))
        assert result.returncode == 0
        day_lines = [l for l in output.split("\n") if l and l[0].isdigit()]
        assert len(day_lines) == 28


def test_january_2026():
    """January 2026 has 31 days, starts on Thursday."""
    with tempfile.TemporaryDirectory() as td:
        result, output = run_script(["2026-01"], Path(td))
        assert result.returncode == 0
        assert "# January 2026" in output
        assert "\n1 Th\n" in output
        assert "\n31 Sa\n" in output


def test_day_of_week_abbreviations():
    """Verify all 7 day abbreviations appear correctly."""
    with tempfile.TemporaryDirectory() as td:
        result, output = run_script(["2026-03"], Path(td))
        assert result.returncode == 0
        assert "\n1 Su\n" in output
        assert "\n2 M\n" in output
        assert "\n3 Tu\n" in output
        assert "\n4 W\n" in output
        assert "\n5 Th\n" in output
        assert "\n6 F\n" in output
        assert "\n7 Sa\n" in output


def test_output_ends_with_tasks_section():
    """Output should end with the Tasks section and a trailing newline."""
    with tempfile.TemporaryDirectory() as td:
        result, output = run_script(["2026-04"], Path(td))
        assert result.returncode == 0
        assert output.rstrip().endswith("**Tasks:**")


def test_writes_correct_filename():
    """Script should write to YYYY-MM/log.md, lowercase."""
    with tempfile.TemporaryDirectory() as td:
        result, output = run_script(["2026-04"], Path(td))
        assert result.returncode == 0
        assert [p.name for p in (Path(td) / "2026-04").iterdir()] == ["log.md"]


def test_refuses_to_overwrite_existing():
    """Script should exit non-zero if the log file already exists."""
    with tempfile.TemporaryDirectory() as td:
        existing = Path(td) / "2026-04" / "log.md"
        existing.parent.mkdir(parents=True)
        existing.write_text("existing content")
        result, _ = run_script(["2026-04"], Path(td))
        assert result.returncode != 0
        assert "already exists" in result.stderr
        assert existing.read_text() == "existing content"


def test_invalid_month():
    """Invalid month should exit non-zero with error on stderr."""
    result, _ = run_script(["2026-13"])
    assert result.returncode != 0
    assert result.stderr.strip() != ""


def test_invalid_format():
    """Non YYYY-MM format should exit non-zero with error on stderr."""
    result, _ = run_script(["foo"])
    assert result.returncode != 0
    assert result.stderr.strip() != ""


def test_no_args():
    """No arguments should exit non-zero with error on stderr."""
    result, _ = run_script([])
    assert result.returncode != 0
    assert result.stderr.strip() != ""
