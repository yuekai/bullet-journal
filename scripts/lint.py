"""Lint the bullet journal: monthly logs, agent entries, and notes.

Every error names the fix and the doc that specifies the rule, so an agent can
repair the journal from the error output alone.
"""

import argparse
import calendar
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FORMAT_DOC = "docs/journal-format.md"
AGENT_DOC = "docs/agent-entries.md"

MONTH_NAMES = list(calendar.month_name)[1:]
MONTH_ABBREVS = list(calendar.month_abbr)[1:]
CAL_DAY_ABBREVS = ["M", "Tu", "W", "Th", "F", "Sa", "Su"]
HEADER_DAY_ABBREVS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

MONTH_DIR_RE = re.compile(r"^\d{4}-\d{2}$")
TITLE_RE = re.compile(r"^# (?P<month>[A-Z][a-z]+) (?P<year>\d{4})$")
CAL_LINE_RE = re.compile(r"^(?P<day>\d{1,2}) (?P<dow>[A-Z][a-z]?)(?: *: (?P<events>\S.*))?$")
DAILY_HEADER_RE = re.compile(
    r"^## (?P<dow>[A-Z][a-z]{2}), (?P<mon>[A-Z][a-z]{2}) (?P<day>[1-9]\d?), (?P<year>\d{4})$"
)
TASK_RE = re.compile(r"^\s*- \[(?P<marker>[^\]]{0,2})\](?!\()")  # not a markdown link
VALID_MARKERS = {" ", "x", ">"}
AGENT_START_RE = re.compile(r"^(?P<indent>\t*)- \[x\] \*\*")
AGENT_FIRST_RE = re.compile(
    r"^\t*- \[x\] \*\*(?P<subject>[^*]+)\*\*"
    r"(?: \(`(?P<repo>[^`]+)`(?: @ `(?P<commit>[0-9a-f]{7,40})`)?\))?$"
)
TRAILER_RE = re.compile(r"^[A-Z][A-Za-z]*(?:-[A-Z][A-Za-z]*)*-session: \S+$")
TRAILER_LIKE_RE = re.compile(r"^\s*[A-Za-z-]+-session:")
NOTE_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.md$")


class Linter:
    def __init__(self, root: Path):
        self.root = root
        self.errors: list[str] = []

    def error(self, path: Path, line: int | None, msg: str, doc: str) -> None:
        rel = path.relative_to(self.root) if path.is_relative_to(self.root) else path
        loc = f"{rel}:{line}" if line else f"{rel}"
        self.errors.append(f"{loc}: {msg} (see {doc})")

    # ---- monthly logs -------------------------------------------------

    def lint_log(self, path: Path) -> None:
        dirname = path.parent.name
        if not MONTH_DIR_RE.match(dirname):
            self.error(path, None, f"monthly log folder '{dirname}' must be named YYYY-MM (e.g., 2026-09)", FORMAT_DOC)
            return
        year, month = int(dirname[:4]), int(dirname[5:])
        if not 1 <= month <= 12:
            self.error(path, None, f"folder '{dirname}' has an invalid month", FORMAT_DOC)
            return

        lines = path.read_text().split("\n")
        expected_title = f"# {MONTH_NAMES[month - 1]} {year}"
        if not lines or lines[0] != expected_title:
            self.error(path, 1, f"first line must be the title '{expected_title}'", FORMAT_DOC)

        try:
            cal_start = lines.index("**Calendar:**")
        except ValueError:
            self.error(path, None, "missing '**Calendar:**' line; recreate the skeleton with "
                       "`pixi run init-monthly-log` in a scratch dir and copy its calendar", FORMAT_DOC)
            return
        try:
            tasks_start = lines.index("**Tasks:**")
        except ValueError:
            self.error(path, None, "missing '**Tasks:**' line after the calendar; add it", FORMAT_DOC)
            return
        if tasks_start < cal_start:
            self.error(path, tasks_start + 1, "'**Tasks:**' must come after the calendar", FORMAT_DOC)
            return

        self.lint_calendar(path, lines, cal_start, tasks_start, year, month)
        self.lint_body(path, lines, tasks_start, year, month)

    def lint_calendar(self, path, lines, cal_start, tasks_start, year, month) -> None:
        num_days = calendar.monthrange(year, month)[1]
        expected_day = 1
        for i in range(cal_start + 1, tasks_start):
            line = lines[i]
            if not line.strip():
                continue
            m = CAL_LINE_RE.match(line)
            if not m:
                self.error(path, i + 1, f"malformed calendar line '{line}'; use 'D Abbrev' or "
                           "'D Abbrev : event; event' (no empty ' :')", FORMAT_DOC)
                expected_day += 1
                continue
            day = int(m["day"])
            if day != expected_day:
                self.error(path, i + 1, f"calendar day {day} out of place; expected day {expected_day} "
                           f"(one line per day, 1..{num_days}, in order)", FORMAT_DOC)
                expected_day = day
            if 1 <= day <= num_days:
                dow = CAL_DAY_ABBREVS[calendar.weekday(year, month, day)]
                if m["dow"] != dow:
                    self.error(path, i + 1, f"day {day} is a '{dow}', not '{m['dow']}'", FORMAT_DOC)
            expected_day += 1
        if expected_day != num_days + 1:
            self.error(path, cal_start + 1, f"calendar must list days 1..{num_days} exactly once", FORMAT_DOC)

    def lint_body(self, path, lines, tasks_start, year, month) -> None:
        prev_date: date | None = None
        i = tasks_start + 1
        while i < len(lines):
            line = lines[i]
            if line.startswith("#"):
                self.lint_header(path, i, line, year, month)
                m = DAILY_HEADER_RE.match(line)
                if m:
                    d = self.header_date(m)
                    if d and prev_date and d <= prev_date:
                        self.error(path, i + 1, f"daily header '{line}' is out of order or duplicated; "
                                   "daily sections must be unique and in ascending date order", FORMAT_DOC)
                    prev_date = d or prev_date
                i += 1
                continue

            t = TASK_RE.match(line)
            if t and t["marker"] not in VALID_MARKERS:
                self.error(path, i + 1, f"invalid task marker '[{t['marker']}]'; use '[ ]' (open), '[x]' (done), "
                           "'[>]' (migrated), or '[ ] ~~text~~' (dropped)", FORMAT_DOC)

            a = AGENT_START_RE.match(line)
            if a:
                i = self.lint_agent_entry(path, lines, i, len(a["indent"]))
                continue
            if TRAILER_LIKE_RE.match(line):
                self.error(path, i + 1, "session trailer outside an agent entry; it must be the last "
                           "tab-indented line under a '- [x] **Subject**' bullet, with no blank line before it", AGENT_DOC)
            i += 1

    def header_date(self, m: re.Match) -> date | None:
        if m["mon"] not in MONTH_ABBREVS:
            return None
        try:
            return date(int(m["year"]), MONTH_ABBREVS.index(m["mon"]) + 1, int(m["day"]))
        except ValueError:
            return None

    def lint_header(self, path, i, line, year, month) -> None:
        m = DAILY_HEADER_RE.match(line)
        if not m:
            self.error(path, i + 1, f"heading '{line}' is not a daily header; daily headers look like "
                       "'## Mon, Sep 28, 2026' (no zero-padding), and no other headings are allowed "
                       "after '**Tasks:**'", FORMAT_DOC)
            return
        d = self.header_date(m)
        if d is None:
            self.error(path, i + 1, f"'{line}' is not a real date", FORMAT_DOC)
            return
        if (d.year, d.month) != (year, month):
            self.error(path, i + 1, f"'{line}' belongs in {d:%Y-%m}/LOG.md, not this month's log", FORMAT_DOC)
        dow = HEADER_DAY_ABBREVS[d.weekday()]
        if m["dow"] != dow:
            self.error(path, i + 1, f"{d:%b} {d.day}, {d.year} is a {dow}, not a {m['dow']}", FORMAT_DOC)

    # ---- agent entries ------------------------------------------------

    def lint_agent_entry(self, path, lines, start, indent) -> int:
        """Lint the agent entry starting at `start`; return the index after it."""
        first = lines[start]
        m = AGENT_FIRST_RE.match(first)
        if not m:
            self.error(path, start + 1, "malformed agent entry first line; use "
                       "'- [x] **Subject**' optionally followed by \" (`~/repo` @ `abc1234`)\" or \" (`~/repo`)\"",
                       AGENT_DOC)
        else:
            subject = m["subject"]
            if len(subject) > 50:
                self.error(path, start + 1, f"subject is {len(subject)} chars; shorten it to 50 or fewer", AGENT_DOC)
            if not subject[:1].isupper():
                self.error(path, start + 1, "subject must start with a capital letter", AGENT_DOC)
            if subject.endswith("."):
                self.error(path, start + 1, "subject must not end with a period", AGENT_DOC)
            if subject != subject.strip():
                self.error(path, start + 1, "subject must not have leading/trailing spaces inside '**'", AGENT_DOC)

        cont_prefix = "\t" * (indent + 1)
        body: list[tuple[int, str]] = []
        i = start + 1
        while i < len(lines):
            line = lines[i]
            if not line.strip() or line.startswith("#"):
                break
            leading = len(line) - len(line.lstrip(" \t"))
            if leading == 0 or (line[:leading].count("\t") <= indent and " " not in line[:leading]):
                break
            if not line.startswith(cont_prefix) or line[len(cont_prefix):][:1] in ("\t", " "):
                self.error(path, i + 1, f"agent entry continuation lines must be indented with exactly "
                           f"{indent + 1} tab(s), no spaces", AGENT_DOC)
            elif line[len(cont_prefix):].startswith("- "):
                self.error(path, i + 1, "no nested bullets inside an agent entry; write body paragraphs as "
                           "plain tab-indented lines", AGENT_DOC)
            body.append((i, line.strip()))
            i += 1

        if not body or not TRAILER_RE.match(body[-1][1]):
            self.error(path, start + 1, "agent entry must end with a session trailer line, e.g. "
                       "'\\tClaude-session: <session-uuid>', using the trailer your harness's user-global "
                       "AGENTS.md/CLAUDE.md prescribes for git commits; no blank line before it", AGENT_DOC)
        for j, text in body[:-1]:
            if TRAILER_LIKE_RE.match(text):
                self.error(path, j + 1, "only one session trailer per entry, and it must be the last line", AGENT_DOC)
        return i

    # ---- notes --------------------------------------------------------

    def lint_note(self, path: Path) -> None:
        if not NOTE_NAME_RE.match(path.name):
            self.error(path, None, "note filenames must be lowercase kebab-case slugs of the title "
                       "(e.g., 'llama-serving-stack.md')", FORMAT_DOC)
        lines = path.read_text().split("\n")
        if not lines or lines[0] != "---":
            self.error(path, 1, "note must start with '---' YAML frontmatter containing title and description",
                       FORMAT_DOC)
            return
        try:
            end = lines.index("---", 1)
        except ValueError:
            self.error(path, 1, "note frontmatter is not closed with '---'", FORMAT_DOC)
            return
        fields = dict(l.split(":", 1) for l in lines[1:end] if ":" in l)
        for key in ("title", "description"):
            if not fields.get(key, "").strip():
                self.error(path, 1, f"note frontmatter needs a non-empty '{key}:'", FORMAT_DOC)

    # ---- driver -------------------------------------------------------

    def run(self) -> list[str]:
        for log in sorted(self.root.glob("*/LOG.md")):
            self.lint_log(log)
        notes = self.root / "notes"
        if notes.is_dir():
            for note in sorted(notes.glob("*.md")):
                self.lint_note(note)
        return self.errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint the bullet journal.")
    parser.add_argument("--root", type=Path, default=ROOT, help="journal root (default: this repo)")
    args = parser.parse_args()
    errors = Linter(args.root.resolve()).run()
    for e in errors:
        print(e, file=sys.stderr)
    if errors:
        print(f"\n{len(errors)} lint error(s). Fix them with the Edit tool (never rewrite a LOG.md "
              "with Write), then rerun `pixi run lint`.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
