# Entry format v2: spaces, sub-bullets, no task trailer

Status: done (2026-09-28)

## Goal

- **Indents:** agent entries indent with 2 spaces, not tabs.
- **Bodies:** task bodies may have sub-bullets, and conversation bodies may have prose. Both share one shape: prose first, then one level of sub-bullets.
- **Session IDs:** task entries drop their session trailer, since the cited commit and the `Log:` commit carry it. Conversation entries move the session into parentheses after the subject: ``- **Subject** (`Claude-session: <id>`)``.
- **Migration:** existing `2026-09/LOG.md` entries are migrated.

## Steps

- [x] `scripts/lint.py`:
  - Recognize task entries by a backticked location and conversation entries by the session in their first line.
  - Share the body rules between the two kinds of entry, and reject tabs and old-style trailer lines in agent entries.
  - Set `TAB_WIDTH` to 2.
- [x] `tests/test_lint.py`: move to the new format and cover the new rules.
- [x] `docs/agent-entries.md`, `docs/journal-format.md`, `docs/design.md`.
- [x] `skills/log-task`, `skills/log-conversation`.
- [x] Migrate `2026-09/LOG.md` with the Edit tool.
- [x] Global Bullet Journal reminders (Claude Code, Codex, DSH, Kimi Code): stop asking for a trailer in task entries.
