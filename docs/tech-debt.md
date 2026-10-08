# Tech debt

Known compromises and gaps, so that cleanup passes have a list to work from. Each item says what's wrong, why it hasn't been fixed, and what fixing it would take. Remove an item in the commit that pays it off, and add one when you knowingly accept a shortcut. Decisions that are settled, not owed, belong in [design.md](design.md).

- **Same-instant edits to `log.md` can still collide.** Two sessions editing the same few lines at once can lose an entry, and so can a `pull --autostash` that runs while another session has uncommitted edits.
  - Why it stays: the Edit tool, `init-monthly-log` and an immediate commit make the window small. A locked write script was judged more machinery than a journal needs (see [design.md](design.md#decisions)).
  - Fix: a single append command that takes a file lock, if lost entries are ever observed.
- **Computer-use entries look like the user's own tasks.** An agent's entry with no repo location gets only the general entry rules, not the agent-entry checks such as the 50-character subject limit.
  - Why it stays: the linter recognises an agent entry by its location (see [design.md](design.md#decisions)), and task entries no longer carry a session trailer to mark them.
  - Fix: a lightweight marker for agent entries outside a repo, with matching changes to [agent-entries.md](agent-entries.md), `scripts/lint.py` and `tests/`.
- **Checks only run where the hooks are installed.** The pre-commit and commit-msg hooks exist only on machines where `pixi run install` has been run. A machine without them can push a malformed log, and nothing on GitHub catches it.
  - Why it stays: every agent writes through the same skills and hooks, so far without a gap.
  - Fix: a GitHub Actions job that runs `pixi run check` on push.
- **Completed plans link to paths that have since moved.** Plans in [plans/](plans/) are historical records. Some still point at the old top-level `notes/` folder, so the doc link check (`tests/test_links.py`) skips them.
  - Why it stays: rewriting history to match today's layout would misstate what each plan said at the time.
  - Fix: none needed unless plans start being read as current docs; [2026-09-29-notes-in-month-folders.md](plans/2026-09-29-notes-in-month-folders.md) records the move.
