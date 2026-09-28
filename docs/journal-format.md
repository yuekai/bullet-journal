# Journal format

The format of monthly logs and notes. `scripts/lint.py` enforces every rule on this page that can be checked mechanically. If you change a rule, update this page, the linter, and `tests/test_lint.py` in the same commit.

Agent work entries have their own spec: [agent-entries.md](agent-entries.md).

## File layout

```
YYYY-MM/
├── LOG.md     # monthly log: calendar + monthly tasks + daily log sections
└── assets/    # optional: files the log links to (chat exports, images, PDFs, …)
notes/
└── <slug>.md  # long-form notes
```

This journal differs from a standard bullet journal in these ways:

- **Task syntax:** Markdown checkboxes (`- [ ]`) replace dot bullets.
- **Events:** they go in the monthly calendar, not in the daily logs.
- **No future log:** a future task goes straight into the monthly log of its target month. Create that log with `init-monthly-log` if it doesn't exist yet.
- **No index:** the file tree serves as the index.

## Monthly log (`YYYY-MM/LOG.md`)

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
	Claude-session: 368d5791-4132-443f-8f46-b634c2d0d483
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
| Agent work | `- [x] **Subject** …` plus body and trailer (see [agent-entries.md](agent-entries.md)) |

- **Nesting:** indent nested items and continuation lines with tabs. A continuation line belongs to the entry above it and ends at the next item at the same or a shallower depth, a heading, a blank line, or the end of the file.
- **Links:** `- [label](url)` is a note, not a task. Only `[ ]`, `[x]` and `[>]` count as task markers.

## Notes (`notes/<slug>.md`)

```markdown
---
title: Llama serving stack
description: How the llama serving stack is deployed
---

- …
```

- **Filename:** a lowercase kebab-case slug of the title.
- **Frontmatter:** must include a non-empty `title` and `description`.
