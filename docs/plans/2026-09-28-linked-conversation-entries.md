# Linked conversation entries

Status: done (2026-09-28), in `37a5f76`. Supersedes the "about 7 sub-bullets + `Details:` link" rule in [conversation-summaries](2026-09-28-conversation-summaries.md).

## Goal

- **Body limit:** a conversation entry's body is at most 500 characters, not counting indentation, and the linter enforces it.
- **Long conversations:** the body goes in `notes/<slug>.md`, and the entry is only its subject, linked to the note: ``- [**Subject**](../notes/<slug>.md) (`Claude-session: <id>`)``.
  - The session stays on the entry, because the note has no other link to it.
  - A linked entry has no body, so each long conversation reads as a single line in the log.
- **Migration:** the one over-long entry, "Logging Claude Desktop conversations", moves to `notes/logging-claude-desktop-conversations.md`.

## Steps

1. `scripts/lint.py`: recognize the linked form, check that its note exists and that it has no body, and cap plain bodies at 500 chars. Add tests.
2. Update `docs/agent-entries.md`, `docs/journal-format.md`, `docs/design.md` and `skills/log-conversation/SKILL.md`.
3. Migrate the entry. It goes in the same commit, because lint has to pass at every commit.
