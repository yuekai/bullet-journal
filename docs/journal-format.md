# Journal format

The format of monthly logs and notes. `scripts/lint.py` enforces every rule on this page that can be checked mechanically. If you change a rule, update this page, the linter, and `tests/test_lint.py` in the same commit.

Entries written by agents (task and conversation entries) have their own spec: [agent-entries.md](agent-entries.md).

## File layout

```
YYYY-MM/
├── log.md     # monthly log: calendar + monthly tasks + daily log sections
├── <slug>.md  # optional: long-form notes dated in this month
└── assets/    # optional: files the log and notes link to (chat exports, images, PDFs, …)
```

This journal differs from a standard bullet journal in these ways:

- **Task syntax:** Markdown checkboxes (`- [ ]`) replace dot bullets.
- **Events:** they go in the monthly calendar, not in the daily logs.
- **No future log:** a future task goes straight into the monthly log of its target month. Create that log with `init-monthly-log` if it doesn't exist yet.
- **No index:** the file tree serves as the index.

## Monthly log (`YYYY-MM/log.md`)

Create a monthly log only with `pixi run init-monthly-log YYYY-MM`. From another directory, run `pixi run --manifest-path ~/bullet-journal/pixi.toml init-monthly-log YYYY-MM`. The command refuses to overwrite an existing log. After that, change the file only with the Edit tool (see [agent-entries.md](agent-entries.md#editing-rules)).

```markdown
# September 2026

**Calendar:**

1 Tu
2 W
...
8 Tu  : dentist appt; lunch with Sam
...
30 W

**Tasks:**

- [ ] discrete diffusion blog post

## Mon, Sep 28, 2026

- [ ] call vet
- a group of pugs is called a grumble
	- the term likely comes from the grumbling noises pugs make
- [x] **Add retry logic to dataset uploader** (`~/HDP-lib` @ `a1b2c3d`)
  Uploads failed outright on transient 5xx errors, so long runs lost hours of work. …
- **Pricing options for the Q4 plan** (`Claude-session: 6ccbfae8-746b-4612-af0c-95d1ed3b6fef`)
  - Go with tiered pricing; a flat fee undercharges heavy users
  - Open: whether to grandfather existing customers
```

### Title

The title is `# <Full month name> <YYYY>`, and it must match the folder name.

### Calendar

- **One line per day** of the month, in order: `<day> <weekday>`.
- **Weekday abbreviations** are `M Tu W Th F Sa Su`. They are deliberately different from the three-letter forms used in daily headers.
- **Events** follow ` : ` (you may pad with spaces before the colon to align them). Separate several events on one day with `; `. Don't leave an empty ` :`.
- **Multi-day events** are repeated on each day they span.

### Monthly tasks

Larger efforts that span days or weeks are listed under `**Tasks:**`.

### Daily log sections

- **Header:** `## <Ddd>, <Mon> <D>, <YYYY>`, for example `## Mon, Sep 28, 2026`. Use three-letter weekday and month abbreviations and don't zero-pad the day. The weekday must match the date.
- **One section per day, only in its own month's log,** in ascending date order. Days with nothing logged have no section.
- **Only these headings:** after `**Tasks:**`, daily headers are the only headings allowed.

### Entries

| Kind | Syntax |
|---|---|
| Open task | `- [ ] text` |
| Completed task | `- [x] text` |
| Migrated task | `- [>] text` |
| Dropped task | `- [ ] ~~text~~` |
| Note | `- text` |
| Agent work | ``- [x] **Subject** (`~/repo` …)`` plus an optional body (see [agent-entries.md](agent-entries.md)) |
| Agent conversation summary | ``- **Subject** (`Claude-session: <id>`)`` plus prose and sub-bullets, or ``- [**Subject**](<slug>.md) (`Claude-session: <id>`)`` alone for a long one (see [agent-entries.md](agent-entries.md#conversation-entries)) |

The linter checks every entry, whoever wrote it:

- **Every line is part of an entry.** After `**Tasks:**`, each non-blank line is one of three things: a daily header, a bullet starting with `- `, or an indented line under a bullet. `*`, `+` and numbered bullets are not allowed, and neither is unindented prose.
- **An item ends at a blank line or a heading.** An item is a top-level bullet plus the indented lines under it. An indented line after a blank line belongs to no item, which is an error.
- **Indentation:** use tabs or spaces, but don't mix them within one line's indent. A tab counts as 2 columns. Agent entries use 2 spaces per level, never tabs.
  - A line indented more than the line above it is one level deeper.
  - To step back out, match the indent of an enclosing line exactly. A width between two enclosing levels is an error.
- **Continuation lines:** a line that isn't a bullet continues the bullet above it. It sits one level deeper than that bullet, or at the same level as the continuation line above it.
- **Tasks:**
  - Markers are only `[ ]`, `[x]` and `[>]`.
  - No entry is empty.
  - `~~strikethrough~~` appears only in a dropped task, `- [ ] ~~text~~`, and covers the whole text.
- **Monthly tasks:** top-level items under `**Tasks:**` must be tasks. Notes can nest under them.
- **Links:** `- [label](url)` is a note, not a task. Only `[ ]`, `[x]` and `[>]` count as task markers.

## Notes (`YYYY-MM/<slug>.md`)

```markdown
---
title: Llama serving stack
description: How the llama serving stack is deployed
date: 2026-09-28
---

- …
```

- **Location:** every Markdown file in a month folder other than `log.md` is a note. It goes in the folder of the month it's dated in, next to the log that links to it, so a link from the log is just `<slug>.md`.
- **Filename:** a lowercase kebab-case slug of the title.
- **Frontmatter:** must include a non-empty `title`, `description` and `date`. The `date` is the day the note was written, as `YYYY-MM-DD`, and must fall in the folder's month.
- **Content:** There's no length limit, but a note must be mostly self-contained. It may link to or refer to other bullet-journal artifacts (relative links) and external links retrieved in the session, but it must not refer to the session transcript.
