# Bullet Journal

A Markdown bullet journal the user reads, and agents mostly maintain. It also serves as long-term memory for the user's coding and computer-use agents: when an agent finishes a task anywhere on this machine, it logs the work here as a commit-message-style entry.

## Map

| Path | What it is | Spec |
|---|---|---|
| `YYYY-MM/LOG.md` | Monthly log: calendar, monthly tasks, daily log sections | [docs/journal-format.md](docs/journal-format.md) |
| `YYYY-MM/assets/` | Optional files the month's log links to | [docs/journal-format.md](docs/journal-format.md) |
| `notes/<slug>.md` | Long-form notes with `title`/`description` frontmatter | [docs/journal-format.md](docs/journal-format.md#notes-notesslugmd) |
| `skills/bullet-journaling/` | Skill that tells agents in other dirs how to log their work | [docs/agent-entries.md](docs/agent-entries.md) |
| `scripts/init_monthly_log.py` | Creates a blank `YYYY-MM/LOG.md` | — |
| `scripts/lint.py` | Enforces the formats above; its errors say how to fix them | — |
| `scripts/check_commit_msg.py` | commit-msg hook: journal-entry commits need a `Log: ` subject and a session trailer | [docs/agent-entries.md](docs/agent-entries.md#committing) |
| `scripts/install.sh` | Enables `.githooks/` and links the skill into each harness | [docs/design.md](docs/design.md) |
| `docs/design.md` | Core beliefs and why things are the way they are | — |
| `docs/plans/` | Execution plans for non-trivial changes to this repo | — |

## Commands

```bash
pixi run init-monthly-log YYYY-MM   # the only way to create a monthly log
pixi run lint                       # also runs as the pre-commit hook
pixi run check                      # lint + tests; run before every commit that touches scripts/ or docs/
pixi run install                    # once per machine: git hooks + skill symlinks
```

## Rules

- **Editing `LOG.md`:** use the Edit tool. Never rewrite a `LOG.md` with `Write`, shell redirection, or a script. Other agent sessions may be appending to it at the same time. See [editing rules](docs/agent-entries.md#editing-rules).
- **Logging your own work:** when you finish a task in this repo, log it like any other agent. Follow `skills/bullet-journaling/SKILL.md`.
- **Changing a format:** update the spec in `docs/`, `scripts/lint.py` and `tests/` in the same commit. If a lint rule and a doc disagree, fix whichever one is wrong. Don't work around it.
- **Plans:** write a plan in `docs/plans/YYYY-MM-DD-<slug>.md` for any change beyond a single-file tweak, and keep its status current.
- **Commits:** follow the user-global commit-message guidelines, including your harness's session trailer. Commit only the paths you changed (`git commit -- <paths>`). Journal-entry commits, which touch only `YYYY-MM/LOG.md`, use a `Log: ` subject; a commit-msg hook enforces this.
- **Package management:** use pixi, not pip, conda or uv.
