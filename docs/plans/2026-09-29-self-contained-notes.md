# Self-contained notes

Status: done (2026-09-29).

## Goal

- **Guidance:** notes have no length limit, but each must be mostly self-contained. A note may link to or refer to other bullet-journal artifacts (relative links) and external links retrieved in the session, but it must not refer to the session transcript.
- **Rewrite:** regenerate `notes/logging-claude-desktop-conversations.md`, which was migrated word for word from a capped log entry, as a note that follows the guidance.

## Steps

1. Add a **Content:** rule to the notes section of `docs/journal-format.md`, and the reason for it to `docs/design.md`. Point to it from the long-conversations rules in `docs/agent-entries.md` and `skills/log-conversation/SKILL.md`.
2. The rule can't be checked mechanically, so `scripts/lint.py` and `tests/` are unchanged.
3. Rewrite the note from the research in its source session. Keep its filename and title so the link in `2026-09/LOG.md` still works.
