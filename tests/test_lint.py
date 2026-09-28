"""Tests for lint.py"""

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from init_monthly_log import generate  # noqa: E402
from lint import Linter  # noqa: E402

SESSION = "Claude-session: 368d5791-4132-443f-8f46-b634c2d0d483"
ENTRY = (
    "- [x] **Add retry logic to dataset uploader** (`~/HDP-lib` @ `a1b2c3d`)\n"
    "\tUploads failed outright on transient 5xx errors. The uploader now retries with backoff.\n"
    f"\t{SESSION}\n"
)


def make_log(root: Path, body: str = "", month: str = "2026-09") -> Path:
    year, mon = int(month[:4]), int(month[5:])
    path = root / month / "LOG.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(generate(year, mon) + body)
    return path


def lint(root: Path) -> list[str]:
    return Linter(root.resolve()).run()


def assert_one_error(root: Path, *fragments: str) -> None:
    errors = lint(root)
    assert len(errors) == 1, errors
    for fragment in fragments:
        assert fragment in errors[0], errors[0]


# ---- valid journals ---------------------------------------------------


def test_fresh_skeleton_is_clean(tmp_path):
    make_log(tmp_path)
    assert lint(tmp_path) == []


def test_full_valid_log(tmp_path):
    body = (
        "\n- [ ] discrete diffusion blog post\n"
        "- [>] migrated task\n"
        "- [ ] ~~dropped task~~\n"
        "\n## Mon, Sep 28, 2026\n\n"
        "- [x] call vet\n"
        "- a group of pugs is called a grumble\n"
        "\t- nested note\n"
        + ENTRY
        + "- [x] **Book flights to Oahu**\n"
        "\tKimi-Code-session: 4a6c613c-a29a-47ba-a59b-a1bb83306afd\n"
        "- [x] **Fix typo in README** (`~/HDP-2`)\n"
        "\tDSH-session: 0b0c305f-1f0e-42a4-bd8a-4190b40dc507\n"
        "\n## Tue, Sep 29, 2026\n\n"
        "- [x] **Tidy up notes**\n"
        "\tCodex-session: 01e7ac7b-e41f-4a97-b0db-b9523ac774df\n"
    )
    path = make_log(tmp_path, body)
    path.write_text(path.read_text().replace("8 Tu\n", "8 Tu  : dentist appt; lunch\n"))
    assert lint(tmp_path) == []


def test_valid_note(tmp_path):
    (tmp_path / "notes").mkdir()
    (tmp_path / "notes" / "llama-serving-stack.md").write_text(
        "---\ntitle: Llama serving stack\ndescription: How we serve llama\n---\n\n- text\n"
    )
    assert lint(tmp_path) == []


# ---- monthly log structure -------------------------------------------


def test_bad_folder_name(tmp_path):
    path = tmp_path / "sept" / "LOG.md"
    path.parent.mkdir()
    path.write_text(generate(2026, 9))
    assert_one_error(tmp_path, "YYYY-MM")


def test_title_mismatch(tmp_path):
    path = make_log(tmp_path)
    path.write_text(path.read_text().replace("# September 2026", "# October 2026"))
    assert_one_error(tmp_path, "# September 2026")


def test_wrong_weekday_in_calendar(tmp_path):
    path = make_log(tmp_path)
    path.write_text(path.read_text().replace("\n28 M\n", "\n28 Tu\n"))
    assert_one_error(tmp_path, "day 28 is a 'M'")


def test_missing_calendar_day(tmp_path):
    path = make_log(tmp_path)
    path.write_text(path.read_text().replace("\n15 Tu\n", "\n"))
    errors = lint(tmp_path)
    assert any("expected day 15" in e for e in errors), errors


def test_empty_calendar_event(tmp_path):
    path = make_log(tmp_path)
    path.write_text(path.read_text().replace("\n6 Su\n", "\n6 Su  :\n"))
    assert_one_error(tmp_path, "malformed calendar line")


def test_missing_tasks_section(tmp_path):
    path = make_log(tmp_path)
    path.write_text(path.read_text().replace("**Tasks:**", ""))
    assert_one_error(tmp_path, "**Tasks:**")


def test_zero_padded_header(tmp_path):
    make_log(tmp_path, "\n## Tue, Sep 08, 2026\n")
    assert_one_error(tmp_path, "no zero-padding")


def test_header_wrong_weekday(tmp_path):
    make_log(tmp_path, "\n## Tue, Sep 28, 2026\n")
    assert_one_error(tmp_path, "is a Mon, not a Tue")


def test_header_wrong_month(tmp_path):
    make_log(tmp_path, "\n## Thu, Oct 1, 2026\n")
    assert_one_error(tmp_path, "belongs in 2026-10/LOG.md")


def test_headers_out_of_order(tmp_path):
    make_log(tmp_path, "\n## Tue, Sep 29, 2026\n\n## Mon, Sep 28, 2026\n")
    assert_one_error(tmp_path, "ascending date order")


def test_duplicate_header(tmp_path):
    make_log(tmp_path, "\n## Mon, Sep 28, 2026\n\n## Mon, Sep 28, 2026\n")
    assert_one_error(tmp_path, "ascending date order")


def test_invalid_task_marker(tmp_path):
    make_log(tmp_path, "\n- [-] half done\n")
    assert_one_error(tmp_path, "invalid task marker '[-]'")


def test_links_are_not_task_markers(tmp_path):
    make_log(tmp_path, day("- [x](https://x.com) link\n- [Some blog post](https://example.com)\n- [a]()\n"))
    assert lint(tmp_path) == []


# ---- entries ----------------------------------------------------------


def day(entry: str) -> str:
    return "\n## Mon, Sep 28, 2026\n\n" + entry


def test_space_indentation(tmp_path):
    make_log(tmp_path, day("- note\n  - child\n    - grandchild\n  - child\n"))
    assert lint(tmp_path) == []


def test_continuation_lines(tmp_path):
    make_log(tmp_path, day("- note\n\tmore of the note\n\t- child\n\t\tmore of the child\n"))
    assert lint(tmp_path) == []


@pytest.mark.parametrize(
    "body, fragment",
    [
        ("* star bullet\n", "start with '- '"),
        ("+ plus bullet\n", "start with '- '"),
        ("1. numbered\n", "start with '- '"),
        ("- note\n\t* star child\n", "start with '- '"),
        ("just prose\n", "not an entry"),
        ("- note\n\n\tindented after a blank line\n", "not under an item"),
        ("- note\n\t \t- mixed indent\n", "mixes tabs and spaces"),
        ("- note\n    - child\n  - misaligned\n", "inconsistent indentation"),
        ("- note\n\t- child\n\tcontinuation at the child's level\n", "one level deeper"),
        ("- [ ]\n", "empty entry"),
        ("- \n", "empty entry"),
        ("- [x] ~~done~~\n", "dropped task only"),
        ("- ~~struck note~~\n", "dropped task only"),
        ("- [ ] ~~half~~ struck\n", "dropped task only"),
    ],
)
def test_malformed_entries(tmp_path, body, fragment):
    make_log(tmp_path, day(body))
    assert_one_error(tmp_path, fragment)


def test_monthly_tasks_must_be_tasks(tmp_path):
    make_log(tmp_path, "\n- [ ] a task\n- a note\n")
    assert_one_error(tmp_path, "must be tasks")


def test_nested_notes_under_monthly_tasks(tmp_path):
    make_log(tmp_path, "\n- [ ] a task\n\t- a note about it\n")
    assert lint(tmp_path) == []


# ---- agent entries ----------------------------------------------------


def test_missing_trailer(tmp_path):
    make_log(tmp_path, day("- [x] **Add retry logic**\n\tBody text.\n"))
    assert_one_error(tmp_path, "must end with a session trailer")


def test_trailer_after_blank_line(tmp_path):
    make_log(tmp_path, day(f"- [x] **Add retry logic**\n\n\t{SESSION}\n"))
    errors = lint(tmp_path)
    assert any("must end with a session trailer" in e for e in errors), errors
    assert any("outside an agent entry" in e for e in errors), errors


def test_trailer_not_last(tmp_path):
    make_log(tmp_path, day(f"- [x] **Add retry logic**\n\t{SESSION}\n\tBody after trailer.\n"))
    errors = lint(tmp_path)
    assert any("must end with a session trailer" in e for e in errors), errors
    assert any("only one session trailer" in e for e in errors), errors


@pytest.mark.parametrize(
    "subject, fragment",
    [
        ("A" * 51, "shorten it to 50"),
        ("add retry logic", "capital letter"),
        ("Add retry logic.", "period"),
    ],
)
def test_bad_subject(tmp_path, subject, fragment):
    make_log(tmp_path, day(f"- [x] **{subject}**\n\t{SESSION}\n"))
    assert_one_error(tmp_path, fragment)


def test_malformed_location_suffix(tmp_path):
    make_log(tmp_path, day(f"- [x] **Add retry logic** (~/HDP-lib, a1b2c3d)\n\t{SESSION}\n"))
    assert_one_error(tmp_path, "malformed agent entry first line")


def test_space_indented_continuation(tmp_path):
    make_log(tmp_path, day(f"- [x] **Add retry logic**\n    Body text.\n    {SESSION}\n"))
    assert lint(tmp_path) == []


def test_nested_bullet_in_agent_entry(tmp_path):
    make_log(tmp_path, day(f"- [x] **Add retry logic**\n\t- a sub-bullet\n\t{SESSION}\n"))
    assert_one_error(tmp_path, "no nested bullets")


def test_nested_agent_entry(tmp_path):
    make_log(tmp_path, day(f"- [ ] fix uploader\n\t- [x] **Add retry logic**\n\t\t{SESSION}\n"))
    assert_one_error(tmp_path, "must be top-level")


def test_stray_trailer(tmp_path):
    make_log(tmp_path, day(f"- a note\n\t{SESSION}\n"))
    assert_one_error(tmp_path, "outside an agent entry")


# ---- notes ------------------------------------------------------------


def test_note_bad_filename(tmp_path):
    (tmp_path / "notes").mkdir()
    (tmp_path / "notes" / "Llama Stack.md").write_text("---\ntitle: T\ndescription: D\n---\n")
    assert_one_error(tmp_path, "kebab-case")


def test_note_missing_description(tmp_path):
    (tmp_path / "notes").mkdir()
    (tmp_path / "notes" / "llama.md").write_text("---\ntitle: T\n---\n")
    assert_one_error(tmp_path, "'description:'")


def test_note_missing_frontmatter(tmp_path):
    (tmp_path / "notes").mkdir()
    (tmp_path / "notes" / "llama.md").write_text("- just text\n")
    assert_one_error(tmp_path, "frontmatter")


# ---- CLI --------------------------------------------------------------


def test_cli_exit_codes(tmp_path):
    script = Path(__file__).resolve().parent.parent / "scripts" / "lint.py"
    make_log(tmp_path)
    ok = subprocess.run([sys.executable, script, "--root", tmp_path], capture_output=True, text=True)
    assert ok.returncode == 0, ok.stderr

    make_log(tmp_path, "\n- [-] bad\n", month="2026-10")
    bad = subprocess.run([sys.executable, script, "--root", tmp_path], capture_output=True, text=True)
    assert bad.returncode == 1
    assert "2026-10/LOG.md:" in bad.stderr
    assert "docs/journal-format.md" in bad.stderr
    assert "Edit tool" in bad.stderr
