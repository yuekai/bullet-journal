"""Lint the bullet journal: monthly logs, their entries (user-written and agent), and notes.

Every error names the fix and the doc that specifies the rule, so an agent can
repair the journal from the error output alone.
"""

import argparse
import calendar
import re
import sys
from dataclasses import dataclass
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
DROPPED_RE = re.compile(r"^- \[ \] ~~(?P<text>.+)~~$")
OTHER_BULLET_RE = re.compile(r"^(?:[*+]|\d+[.)])\s")
TAB_WIDTH = 4  # columns a tab counts for when comparing indents
AGENT_FIRST_RE = re.compile(
    r"^- \[x\] \*\*(?P<subject>[^*]+)\*\*"
    r"(?: \(`(?P<repo>[^`]+)`(?: @ `(?P<commit>[0-9a-f]{7,40})`)?\))?$"
)
CONVO_FIRST_RE = re.compile(r"^- \*\*(?P<subject>[^*]+)\*\*(?: \(`(?P<repo>[^`]+)`\))?$")
TRAILER_RE = re.compile(r"^[A-Z][A-Za-z]*(?:-[A-Z][A-Za-z]*)*-session: \S+$")
TRAILER_LIKE_RE = re.compile(r"^\s*(?:- )?[A-Za-z-]+-session:")  # plain or bulleted
NOTE_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.md$")


@dataclass
class Line:
    """A non-blank line of an item: its index in the file, its text without indentation, and its nesting level."""

    i: int
    text: str
    level: int

    @property
    def is_bullet(self) -> bool:
        return self.text.startswith("- ")


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
        """Split everything after '**Tasks:**' into items and lint each one."""
        prev_date: date | None = None
        in_daily = False
        items: list[tuple[list[Line], bool]] = []
        item: list[Line] | None = None
        widths: list[int] = []
        for i in range(tasks_start + 1, len(lines)):
            line = lines[i]
            if not line.strip():
                item = None
                continue
            if line.startswith("#"):
                item = None
                in_daily = True
                self.lint_header(path, i, line, year, month)
                m = DAILY_HEADER_RE.match(line)
                if m:
                    d = self.header_date(m)
                    if d and prev_date and d <= prev_date:
                        self.error(path, i + 1, f"daily header '{line}' is out of order or duplicated; "
                                   "daily sections must be unique and in ascending date order", FORMAT_DOC)
                    prev_date = d or prev_date
                continue

            text = line.lstrip(" \t")
            indent = line[: len(line) - len(text)]
            if not indent:
                if TRAILER_LIKE_RE.match(text):
                    self.stray_trailer(path, i)
                    item = None
                    continue
                if not text.startswith("- "):
                    self.error(path, i + 1, self.not_a_bullet(text), FORMAT_DOC)
                    item = None
                    continue
                item = [Line(i, text, 0)]
                items.append((item, in_daily))
                widths = [0]
                continue
            if item is None:
                if TRAILER_LIKE_RE.match(text):
                    self.stray_trailer(path, i)
                else:
                    self.error(path, i + 1, "indented line is not under an item; a blank line or heading ends "
                               "an item, so delete the blank line above it or unindent it", FORMAT_DOC)
                continue
            if " " in indent and "\t" in indent:
                self.error(path, i + 1, "indentation mixes tabs and spaces; use only one of them", FORMAT_DOC)
            width = indent.count("\t") * TAB_WIDTH + indent.count(" ")
            if width not in widths and width < widths[-1]:
                self.error(path, i + 1, "inconsistent indentation: this line is indented less than the line "
                           "above but doesn't line up with any enclosing item; match the indent of the "
                           "item it belongs to", FORMAT_DOC)
            while widths[-1] > width:
                widths.pop()
            if widths[-1] < width:
                widths.append(width)
            item.append(Line(i, text, len(widths) - 1))

        for item, in_daily in items:
            self.lint_item(path, item, in_daily)

    def stray_trailer(self, path, i: int) -> None:
        self.error(path, i + 1, "session trailer outside an agent entry; it must be the last line one level "
                   "under a '- [x] **Subject**' (task) or '- **Subject**' (conversation) bullet, with no blank "
                   "line before it", AGENT_DOC)

    @staticmethod
    def not_a_bullet(text: str) -> str:
        if OTHER_BULLET_RE.match(text):
            return "bullets start with '- ', not '*', '+' or a number"
        return ("line is not an entry; every line after '**Tasks:**' is a daily header, a '- ' bullet, "
                "or a line indented under one")

    def lint_item(self, path, item: list[Line], in_daily: bool) -> None:
        """Lint one item. A session trailer one level under the bullet makes it an agent entry."""
        first = item[0]
        if not in_daily and not TASK_RE.match(first.text):
            self.error(path, first.i + 1, "top-level items under '**Tasks:**' must be tasks ('- [ ] text'); "
                       "put notes in a daily section", FORMAT_DOC)

        trailers = [line for line in item[1:] if TRAILER_LIKE_RE.match(line.text)]
        for line in trailers:
            if line.level > 1:
                self.error(path, line.i + 1, "agent entries must be top-level bullets in the daily section, "
                           "not nested under another item; unindent the entry this session trailer ends",
                           AGENT_DOC)
        agent = any(line.level == 1 for line in trailers)
        if TRAILER_LIKE_RE.match(first.text):
            self.stray_trailer(path, first.i)

        for prev, line in zip([None, *item], item):
            if line.is_bullet:
                self.lint_bullet(path, line)
            elif OTHER_BULLET_RE.match(line.text):
                self.error(path, line.i + 1, "bullets start with '- ', not '*', '+' or a number", FORMAT_DOC)
            elif not agent and line.level != prev.level + prev.is_bullet:
                self.error(path, line.i + 1, "continuation line must be indented one level deeper than the "
                           "bullet it continues", FORMAT_DOC)

        if not agent:
            return
        if not in_daily:
            self.error(path, first.i + 1, "agent entries go in a daily section, not under '**Tasks:**'", AGENT_DOC)
        if first.text.startswith("- [x] **"):
            self.lint_agent_entry(path, item)
        elif first.text.startswith("- **"):
            self.lint_convo_entry(path, item)
        else:
            self.error(path, first.i + 1, "this item has a session trailer, which marks an agent entry, but its "
                       "first line isn't '- [x] **Subject**' (task) or '- **Subject**' (conversation); fix the "
                       "first line, or remove the trailer if this isn't an agent entry", AGENT_DOC)

    def lint_bullet(self, path, line: Line) -> None:
        t = TASK_RE.match(line.text)
        if t and t["marker"] not in VALID_MARKERS:
            self.error(path, line.i + 1, f"invalid task marker '[{t['marker']}]'; use '[ ]' (open), '[x]' (done), "
                       "'[>]' (migrated), or '[ ] ~~text~~' (dropped)", FORMAT_DOC)
        if not line.text[t.end() if t else 2:].strip():
            self.error(path, line.i + 1, "empty entry; add text after the bullet or delete the line", FORMAT_DOC)
        if "~~" in line.text:
            d = DROPPED_RE.match(line.text)
            if not d or "~~" in d["text"]:
                self.error(path, line.i + 1, "strikethrough marks a dropped task only: write "
                           "'- [ ] ~~text~~', with '~~' around the whole text", FORMAT_DOC)

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

    def lint_agent_entry(self, path, item: list[Line]) -> None:
        first = item[0]
        m = AGENT_FIRST_RE.match(first.text)
        if not m:
            self.error(path, first.i + 1, "malformed agent entry first line; use "
                       "'- [x] **Subject**' optionally followed by \" (`~/repo` @ `abc1234`)\" or \" (`~/repo`)\"",
                       AGENT_DOC)
        else:
            self.lint_subject(path, first, m["subject"])

        body = item[1:]
        for line in body:
            if line.is_bullet:
                self.error(path, line.i + 1, "no nested bullets inside an agent entry; write body paragraphs as "
                           "plain indented lines", AGENT_DOC)
            elif line.level != 1:
                self.error(path, line.i + 1, "agent entry body lines must all be indented one level under the "
                           "bullet", AGENT_DOC)

        if not body or not TRAILER_RE.match(body[-1].text):
            self.error(path, first.i + 1, "agent entry must end with a session trailer line, e.g. "
                       "'\\tClaude-session: <session-uuid>', using the trailer your harness's user-global "
                       "AGENTS.md/CLAUDE.md prescribes for git commits; no blank line before it", AGENT_DOC)
        for line in body[:-1]:
            if TRAILER_LIKE_RE.match(line.text):
                self.error(path, line.i + 1, "only one session trailer per entry, and it must be the last line",
                           AGENT_DOC)

    def lint_convo_entry(self, path, item: list[Line]) -> None:
        first = item[0]
        m = CONVO_FIRST_RE.match(first.text)
        if not m:
            self.error(path, first.i + 1, "malformed conversation entry first line; use '- **Subject**' "
                       "optionally followed by \" (`~/repo`)\", with nothing else after it", AGENT_DOC)
        else:
            self.lint_subject(path, first, m["subject"])

        children = item[1:]
        for line in children:
            if not line.is_bullet:
                self.error(path, line.i + 1, "conversation entries hold only '- ' sub-bullets; turn this line "
                           "into a sub-bullet, or move long prose into a note in notes/", AGENT_DOC)
            elif line.level > 1 and not TRAILER_LIKE_RE.match(line.text):
                self.error(path, line.i + 1, "conversation entries have one level of sub-bullets; don't nest "
                           "deeper", AGENT_DOC)

        last = children[-1] if children else None
        if not last or not (last.is_bullet and TRAILER_RE.match(last.text[2:])):
            self.error(path, first.i + 1, "conversation entry must end with a session trailer sub-bullet, e.g. "
                       "'\\t- Claude-session: <session-uuid>', using the trailer your harness's user-global "
                       "AGENTS.md/CLAUDE.md prescribes for git commits", AGENT_DOC)
        for line in children[:-1]:
            if TRAILER_LIKE_RE.match(line.text):
                self.error(path, line.i + 1, "only one session trailer per entry, and it must be the last "
                           "sub-bullet", AGENT_DOC)

    def lint_subject(self, path, first: Line, subject: str) -> None:
        if len(subject) > 50:
            self.error(path, first.i + 1, f"subject is {len(subject)} chars; shorten it to 50 or fewer", AGENT_DOC)
        if not subject[:1].isupper():
            self.error(path, first.i + 1, "subject must start with a capital letter", AGENT_DOC)
        if subject.endswith("."):
            self.error(path, first.i + 1, "subject must not end with a period", AGENT_DOC)
        if subject != subject.strip():
            self.error(path, first.i + 1, "subject must not have leading/trailing spaces inside '**'", AGENT_DOC)

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
