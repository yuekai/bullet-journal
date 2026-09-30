# Notes in month folders, lowercase log.md, GitHub sync

Status: done (2026-09-29).

## Goal

- **Notes move into month folders:** `notes/<slug>.md` becomes `YYYY-MM/<slug>.md`, in the folder of the month the note is dated in. A log links to it as `<slug>.md`.
- **Lowercase log:** `YYYY-MM/LOG.md` becomes `YYYY-MM/log.md`.
- **Dated notes:** note frontmatter requires `date: YYYY-MM-DD`, which must fall in the folder's month.
- **GitHub sync:** the journal is kept on several machines through `origin` on GitHub. `log-task` and `log-conversation` pull (`--rebase --autostash`) before editing and push after committing.

## Steps

1. `scripts/lint.py`: lint `YYYY-MM/log.md`, and treat every other `*.md` in a month folder as a note. Require and check `date`. Resolve linked notes against the log's folder. Flag a leftover `LOG.md` or `notes/` folder. Filenames are compared exactly, because macOS is case-insensitive.
2. `scripts/init_monthly_log.py` writes `log.md`. `scripts/check_commit_msg.py` treats only `YYYY-MM/log.md` as a log path.
3. Tests for the above.
4. Update the specs in `docs/journal-format.md` and `docs/agent-entries.md`, the decisions in `docs/design.md`, and the `AGENTS.md` map and both skills.
5. Migrate: `git mv` the log and the one note, add the note's `date` (its first commit, 2026-09-28), fix the log's link to it, and remove `notes/`. Past entries that mention `notes/` or `LOG.md` stay as they are.

## Transitional risk

Agent sessions already running when this lands still have the old skill text. On the case-insensitive filesystem, their edits to `LOG.md` land in `log.md`. A `git add YYYY-MM/LOG.md` pathspec may fail, and the agent then reports it. The linter's leftover-`LOG.md` error catches a log created by a stale session on a case-sensitive machine.
