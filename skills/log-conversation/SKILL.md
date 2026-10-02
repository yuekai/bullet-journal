---
name: log-conversation
description: Use when the user asks you to log or record a conversation/discussion in their bullet journal (e.g. "log this conversation", "journal what we decided"). Writes the conversation's conclusions to ~/bullet-journal as a note entry with your session ID. 
---

# Log conversations/discussions

The user's bullet journal at `~/bullet-journal` is long-term memory, readable by people, shared by all of their agents. When the user asks, add one entry to today's daily log that records what this conversation concluded, so that future agents, and the user, can pick up where it left off.

**Log a conversation only when the user asks.** Never log a conversation  on your own initiative. If the session completed tasks/work (eg, created/modified code, config, data, etc), log the tasks/work with the `log-task` skill.

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
- **Session:** in parentheses after the subject (eg, `` (`<trailer>`) ``), where `<trailer>` is the same session trailer your user-global `AGENTS.md` or `CLAUDE.md` tells you to put in git commits, with the same session ID. Claude Code, for example, writes `` (`Claude-session: $CLAUDE_CODE_SESSION_ID`) ``.
- **Body:** indent every line with 2 spaces (never tabs). No blank lines.
  - Optional prose first, one line per paragraph, then sub-bullets, one level only. A prose line after a sub-bullet would render as part of it.
  - Record the conclusions, decisions made, unresolved questions; omit the back-and-forth that led up to them. 
  - Write the entry so it makes sense without the session transcript; ie, it should be self-contained.
- **Long conversations:** if the body exceeds 500 chars (not counting indentation), write it as a note in `~/bullet-journal/YYYY-MM/<slug>.md`, next to this month's `log.md`, with `title`, `description` and `date` (today, `YYYY-MM-DD`) frontmatter (see `~/bullet-journal/docs/journal-format.md`). The note must be mostly self-contained: link to journal artifacts and to external sources you retrieved, but never refer to the session transcript. The entry is then just the subject, linked to the note, plus the session: `` - [**<Subject>**](<slug>.md) (`<trailer>`) ``. It may keep a short body (at most 500 chars, same shape) for related work, such as where a copy of the note lives, instead of a separate task entry. 
- **Never include** secrets, credentials, tokens, private personal data, or sensitive operational details. If the conversation touched on any, leave them out.

## 2. Add it to today's log and commit

Follow steps 2 and 3 of `~/bullet-journal/skills/log-task/SKILL.md` exactly:
- pull from GitHub first (before writing a note, too);
- create a missing month with `init-monthly-log`;
- use the Edit tool, never a whole-file write;
- lint;
- commit only the files you touched, with subject `Log: <Subject>` and your session trailer;
- push.

If you wrote a note, commit it first, in its own commit (`git -C ~/bullet-journal add YYYY-MM/<slug>.md && git -C ~/bullet-journal commit -m "Add note on <topic>" -m "<your session trailer>" -- YYYY-MM/<slug>.md`), without the `Log: ` prefix. The commit-msg hook allows `Log: ` only on commits that touch nothing but `YYYY-MM/log.md`.

Full spec: `~/bullet-journal/docs/agent-entries.md#conversation-entries`.
