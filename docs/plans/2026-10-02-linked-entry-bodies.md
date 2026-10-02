# Bodies on linked conversation entries

Status: done (2026-10-02).

## Goal

A linked conversation entry (a subject linking to a note) could have no body, so work about the note itself, such as copying it to another machine, needed a separate task entry. Let a linked entry keep a short optional body so one entry covers the note and that work.

## Steps

1. `scripts/lint.py`: drop the no-body error for linked entries; a body, when present, gets the same shape check and 500-character limit as any conversation body, and an over-limit error says to move the rest into the note.
2. `tests/test_lint.py`: a linked entry with a short body passes; an over-limit body fails.
3. Update `docs/agent-entries.md`, `docs/design.md` and `skills/log-conversation/SKILL.md` to describe the optional body.
