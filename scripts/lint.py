"""Lint the bullet journal: monthly logs, their entries (user-written and agent), and the notes beside them.

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
TAB_WIDTH = 2  # columns a tab counts for when comparing indents
AGENT_INDENT = "  "  # agent entries indent each level with 2 spaces
TASK_START_RE = re.compile(r"^- \[x\] \*\*[^*]+\*\* \(`")  # a bold [x] with a location is a task entry
CONVO_START_RE = re.compile(r"^- \[?\*\*.*-session:")  # a bold (or linked) note with a session is a conversation entry
TASK_FIRST_RE = re.compile(
    r"^- \[x\] \*\*(?P<subject>[^*]+)\*\* \(`(?P<repo>[^`]+)`(?: @ `(?P<commit>[0-9a-f]{7,40})`)?\)$"
)
SESSION_TRAILER = r"\(`(?P<trailer>[A-Z][A-Za-z]*(?:-[A-Z][A-Za-z]*)*-session: [^`\s]+)`\)"
CONVO_FIRST_RE = re.compile(r"^- \*\*(?P<subject>[^*]+)\*\* " + SESSION_TRAILER + "$")
LINKED_CONVO_FIRST_RE = re.compile(
    r"^- \[\*\*(?P<subject>[^*]+)\*\*\]\((?P<note>[^)/]+\.md)\) " + SESSION_TRAILER + "$"
)
CONVO_BODY_MAX = 500  # chars of body text; longer conversations go in a linked note
TRAILER_LIKE_RE = re.compile(r"^\s*(?:- )?[A-Za-z-]+-session:")  # plain or bulleted
NOTE_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
NOTE_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LOG_NAME = "log.md"


@dataclass
class Line:
    """A non-blank line of an item: its index in the file, its text without indentation, its nesting level,
    and its raw indentation."""

    i: int
    text: str
    level: int
    indent: str = ""

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
            item.append(Line(i, text, len(widths) - 1, indent))

        for item, in_daily in items:
            self.lint_item(path, item, in_daily)

    def stray_trailer(self, path, i: int) -> None:
        self.error(path, i + 1, "session trailer on its own line; entries no longer end in a trailer line. A "
                   "conversation entry puts it after the subject, '- **Subject** (`Claude-session: <id>`)', and "
                   "a task entry carries none (its commit and the 'Log:' commit do); delete this line",
                   AGENT_DOC)

    @staticmethod
    def not_a_bullet(text: str) -> str:
        if OTHER_BULLET_RE.match(text):
            return "bullets start with '- ', not '*', '+' or a number"
        return ("line is not an entry; every line after '**Tasks:**' is a daily header, a '- ' bullet, "
                "or a line indented under one")

    def lint_item(self, path, item: list[Line], in_daily: bool) -> None:
        """Lint one item. Its first line decides whether it is an agent entry (see entry_kind)."""
        first = item[0]
        if not in_daily and not TASK_RE.match(first.text):
            self.error(path, first.i + 1, "top-level items under '**Tasks:**' must be tasks ('- [ ] text'); "
                       "put notes in a daily section", FORMAT_DOC)

        for line in item[1:]:
            if self.entry_kind(line.text):
                self.error(path, line.i + 1, "agent entries must be top-level bullets in the daily section, "
                           "not nested under another item; unindent this entry", AGENT_DOC)
        kind = self.entry_kind(first.text)

        for prev, line in zip([None, *item], item):
            if line.is_bullet:
                self.lint_bullet(path, line)
            elif OTHER_BULLET_RE.match(line.text):
                self.error(path, line.i + 1, "bullets start with '- ', not '*', '+' or a number", FORMAT_DOC)
            elif not kind and line.level != prev.level + prev.is_bullet:
                self.error(path, line.i + 1, "continuation line must be indented one level deeper than the "
                           "bullet it continues", FORMAT_DOC)

        if not kind:
            for line in item[1:]:
                if TRAILER_LIKE_RE.match(line.text):
                    self.stray_trailer(path, line.i)
            return
        if not in_daily:
            self.error(path, first.i + 1, "agent entries go in a daily section, not under '**Tasks:**'", AGENT_DOC)
        if kind == "task":
            self.lint_task_entry(path, item)
        else:
            self.lint_convo_entry(path, item)

    @staticmethod
    def entry_kind(text: str) -> str | None:
        """'task' for a bold [x] with a location, 'convo' for a bold note with a session, else None."""
        if TASK_START_RE.match(text):
            return "task"
        if CONVO_START_RE.match(text):
            return "convo"
        return None

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
            self.error(path, i + 1, f"'{line}' belongs in {d:%Y-%m}/log.md, not this month's log", FORMAT_DOC)
        dow = HEADER_DAY_ABBREVS[d.weekday()]
        if m["dow"] != dow:
            self.error(path, i + 1, f"{d:%b} {d.day}, {d.year} is a {dow}, not a {m['dow']}", FORMAT_DOC)

    # ---- agent entries ------------------------------------------------

    def lint_task_entry(self, path, item: list[Line]) -> None:
        first = item[0]
        m = TASK_FIRST_RE.match(first.text)
        if not m:
            self.error(path, first.i + 1, "malformed task entry first line; use "
                       "'- [x] **Subject**' followed by \" (`~/repo` @ `abc1234`)\" or \" (`~/repo`)\"",
                       AGENT_DOC)
        else:
            self.lint_subject(path, first, m["subject"])
        self.lint_entry_body(path, item[1:])

    def lint_convo_entry(self, path, item: list[Line]) -> None:
        first = item[0]
        linked = LINKED_CONVO_FIRST_RE.match(first.text)
        m = linked or CONVO_FIRST_RE.match(first.text)
        if not m:
            self.error(path, first.i + 1, "malformed conversation entry first line; use '- **Subject** "
                       "(`Claude-session: <session-uuid>`)', or '- [**Subject**](<slug>.md) "
                       "(`Claude-session: <session-uuid>`)' for a long one, linking a note in the log's folder, with the trailer your harness's "
                       "user-global AGENTS.md/CLAUDE.md prescribes for git commits, and nothing else after it",
                       AGENT_DOC)
        else:
            self.lint_subject(path, first, m["subject"])
        body = item[1:]
        if first.text.startswith("- [**"):  # the linked form, even if malformed
            if linked and (linked["note"] == LOG_NAME or not (path.parent / linked["note"]).is_file()):
                self.error(path, first.i + 1, f"linked note {path.parent.name}/{linked['note']} doesn't exist; "
                           "write it in the log's folder or fix the link", AGENT_DOC)
            if not body:  # a linked entry's body is optional
                return
        elif not body:
            self.error(path, first.i + 1, "conversation entry has no body; add its conclusions under it",
                       AGENT_DOC)
        size = sum(len(line.text) for line in body)
        if size > CONVO_BODY_MAX:
            fix = ("move the rest into the linked note" if first.text.startswith("- [**") else
                   "write it as a note in YYYY-MM/<slug>.md and link the subject to it, "
                   "'- [**Subject**](<slug>.md) (`…-session: …`)'")
            self.error(path, first.i + 1, f"conversation entry body is {size} chars; over {CONVO_BODY_MAX}, "
                       + fix, AGENT_DOC)
        self.lint_entry_body(path, body)

    def lint_entry_body(self, path, body: list[Line]) -> None:
        """Task and conversation bodies: prose lines first, then one level of sub-bullets, 2-space indents."""
        seen_bullet = False
        for line in body:
            if TRAILER_LIKE_RE.match(line.text):
                self.stray_trailer(path, line.i)
                continue
            if line.indent != AGENT_INDENT * line.level:
                self.error(path, line.i + 1, "indent agent entries with 2 spaces per level, not tabs",
                           AGENT_DOC)
            if line.is_bullet:
                seen_bullet = True
                if line.level != 1:
                    self.error(path, line.i + 1, "agent entries have one level of sub-bullets; don't nest "
                               "deeper", AGENT_DOC)
            elif line.level != 1:
                self.error(path, line.i + 1, "prose lines in an agent entry are indented one level under the "
                           "bullet", AGENT_DOC)
            elif seen_bullet:
                self.error(path, line.i + 1, "prose goes before the sub-bullets; after one, it would render "
                           "as part of that sub-bullet", AGENT_DOC)

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
            self.error(path, 1, "note must start with '---' YAML frontmatter containing title, description "
                       "and date", FORMAT_DOC)
            return
        try:
            end = lines.index("---", 1)
        except ValueError:
            self.error(path, 1, "note frontmatter is not closed with '---'", FORMAT_DOC)
            return
        fields = dict(l.split(":", 1) for l in lines[1:end] if ":" in l)
        for key in ("title", "description", "date"):
            if not fields.get(key, "").strip():
                self.error(path, 1, f"note frontmatter needs a non-empty '{key}:'", FORMAT_DOC)
        value = fields.get("date", "").strip()
        if value:
            self.lint_note_date(path, value, int(path.parent.name[:4]), int(path.parent.name[5:]))

    def lint_note_date(self, path: Path, value: str, year: int, month: int) -> None:
        try:
            d = date.fromisoformat(value) if NOTE_DATE_RE.match(value) else None
        except ValueError:
            d = None
        if d is None:
            self.error(path, 1, f"note date '{value}' is not a real YYYY-MM-DD date", FORMAT_DOC)
        elif (d.year, d.month) != (year, month):
            self.error(path, 1, f"note dated {value} belongs in {d:%Y-%m}/, not {path.parent.name}/", FORMAT_DOC)

    # ---- driver -------------------------------------------------------

    def run(self) -> list[str]:
        # Match filenames exactly: on a case-insensitive filesystem, LOG.md would also "exist" as log.md.
        for folder in sorted(p for p in self.root.iterdir() if p.is_dir() and not p.name.startswith(".")):
            names = {f.name for f in folder.iterdir()}
            if folder.name == "notes" and any(name.endswith(".md") for name in names):
                self.error(folder, None, "notes no longer live in notes/; move each note into the YYYY-MM/ "
                           "folder of its date and fix the links to it", FORMAT_DOC)
            if "LOG.md" in names:
                self.error(folder / "LOG.md", None, "the monthly log is named log.md now; rename it with "
                           "`git mv`", FORMAT_DOC)
            if LOG_NAME in names:
                self.lint_log(folder / LOG_NAME)
            if MONTH_DIR_RE.match(folder.name) and 1 <= int(folder.name[5:]) <= 12:
                for name in sorted(names):
                    if name.endswith(".md") and name not in (LOG_NAME, "LOG.md"):
                        self.lint_note(folder / name)
        return self.errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint the bullet journal.")
    parser.add_argument("--root", type=Path, default=ROOT, help="journal root (default: this repo)")
    args = parser.parse_args()
    errors = Linter(args.root.resolve()).run()
    for e in errors:
        print(e, file=sys.stderr)
    if errors:
        print(f"\n{len(errors)} lint error(s). Fix them with the Edit tool (never rewrite a log.md "
              "with Write), then rerun `pixi run lint`.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
