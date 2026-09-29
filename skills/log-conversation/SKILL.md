---
name: log-conversation
description: Use only when the user asks you to log, record, journal or summarize a conversation in their bullet journal (e.g. "log this conversation", "journal what we decided"). Writes the conversation's conclusions to ~/bullet-journal as a note entry with your session ID. Never use it on your own initiative.
---

# Log a conversation's conclusions

The user's bullet journal at `~/bullet-journal` is long-term memory, readable by people, shared by all of their agents. When the user asks, add one entry to today's daily log that records what this conversation concluded, so that future agents, and the user, can pick up where it left off.

**Log a conversation only when the user asks.** If they don't, don't. Finished work (code, config, data, computer use) is logged separately with the `log-task` skill.

## 1. Write the entry

```markdown
- **Pricing options for the Q4 plan** (`Claude-session: 6ccbfae8-746b-4612-af0c-95d1ed3b6fef`)
  Tiered pricing won because heavy users drive most of the support cost.
  - Go with tiered pricing; a flat fee undercharges heavy users
  - Launch the free tier after the paid tiers, once support load is known
  - Open: whether to grandfather existing customers
```

- **Subject:** bold, at most 50 characters, capitalized, no trailing period.
  - Use a noun phrase naming the topic or its conclusion, not an imperative.
- **Session:** in parentheses after the subject (eg, `` (`<trailer>`) ``), where `<trailer>` is the same session trailer your harness's user-global `AGENTS.md` or `CLAUDE.md` tells you to put in git commits, with the same session ID. Claude Code, for example, writes `` (`Claude-session: $CLAUDE_CODE_SESSION_ID`) ``.
- **Body:** indent every line with 2 spaces (never tabs). No blank lines.
  - Optional prose first, one line per paragraph, then sub-bullets, one level only. A prose line after a sub-bullet would render as part of it.
  - Record the conclusions, decisions made (with their reason when it isn't obvious), and any unresolved questions; omit the back-and-forth that led there.
  - Write each line so it makes sense without the transcript.
- **Long conversations:** if the body exceeds 500 chars (not counting indentation), write it as a note in `~/bullet-journal/notes/<slug>.md` with `title` and `description` frontmatter (see `~/bullet-journal/docs/journal-format.md`). The entry is then just the subject, linked to the note, plus the session, with no body: `` - [**<Subject>**](../notes/<slug>.md) (`<trailer>`) ``.
- **Never include** secrets, credentials, tokens, private personal data, or sensitive operational details. If the conversation touched on any, leave them out.

## 2. Add it to today's log and commit

Follow steps 2 and 3 of `~/bullet-journal/skills/log-task/SKILL.md` exactly:
- use the Edit tool, never a whole-file write;
- create a missing month with `init-monthly-log`;
- lint;
- commit only the files you touched, with subject `Log: <Subject>` and your session trailer.

If you wrote a note, commit it first, in its own commit (`git -C ~/bullet-journal commit -m "Add note on <topic>" -m "<your session trailer>" -- notes/<slug>.md`), without the `Log: ` prefix. The commit-msg hook allows `Log: ` only on commits that touch nothing but `YYYY-MM/LOG.md`.

Full spec: `~/bullet-journal/docs/agent-entries.md#conversation-entries`.
