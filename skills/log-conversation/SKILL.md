---
name: log-conversation
description: Use only when the user asks you to log, record, journal or summarize a conversation in their bullet journal (e.g. "log this conversation", "journal what we decided"). Writes the conversation's conclusions to ~/bullet-journal as a note entry with your session ID. Never use it on your own initiative.
---

# Log a conversation's conclusions

The user's bullet journal at `~/bullet-journal` is long-term memory, readable by people, shared by all of their agents. When the user asks, add one entry to today's daily log that records what this conversation concluded, so that future agents, and the user, can pick up where it left off.

**Log a conversation only when the user asks.** If they don't, don't. Finished work (code, config, data, computer use) is logged separately with the `log-task` skill.

## 1. Write the entry

```markdown
- **Pricing options for the Q4 plan**
	- Go with tiered pricing; a flat fee undercharges heavy users
	- Launch the free tier after the paid tiers, once support load is known
	- Open: whether to grandfather existing customers
	- Claude-session: 6ccbfae8-746b-4612-af0c-95d1ed3b6fef
```

- **Subject:** bold, at most 50 characters, capitalized, no trailing period.
  - Use a noun phrase naming the topic or its conclusion, not an imperative.
  - Add `` (`~/repo`) `` after it when the conversation was about a repo. Abbreviate the path with `~`.
- **Sub-bullets:** one level only, each indented with a single tab. No deeper nesting and no prose lines.
  - One point per sub-bullet: a conclusion, a decision (with its reason when it isn't obvious), or an open question (prefix `Open: `).
  - Record what was concluded, not the back-and-forth that led there.
  - Write each one so it makes sense without the transcript.
- **Long conversations:**
  - If you need more than about 7 sub-bullets, or prose to make sense, write the details as a note in `~/bullet-journal/notes/<slug>.md`, with `title` and `description` frontmatter; see `~/bullet-journal/docs/journal-format.md`.
  - Link it with a sub-bullet such as `- Details: [<slug>](../notes/<slug>.md)`.
- **Trailer (last sub-bullet):** `- ` followed by the same session trailer your harness's user-global `AGENTS.md` or `CLAUDE.md` tells you to put in git commits, with the same session ID. Claude Code, for example, writes `- Claude-session: $CLAUDE_CODE_SESSION_ID`.
- **Never include** secrets, credentials, tokens, private personal data, or sensitive operational details. If the conversation touched on any, leave them out.
- **Summarizing a pasted chat:** if the user pastes a summary or transcript from another app, such as a Claude Desktop chat, write the entry from it with your own trailer. Add a `- Source: <link or app name>` sub-bullet before the trailer.

Weak entry:

```markdown
- **Discussed pricing.**
	- We talked about a lot of options and the user asked about tiers, then I explained flat fees
		- flat fees are simpler
```

This has a trailing period. It narrates the conversation instead of stating conclusions, nests a second level, and has no trailer.

## 2. Add it to today's log and commit

Follow steps 2 and 3 of `~/bullet-journal/skills/log-task/SKILL.md` exactly:
- use the Edit tool, never a whole-file write;
- create a missing month with `init-monthly-log`;
- lint;
- commit only the files you touched, with subject `Log: <Subject>` and your session trailer.

If you wrote a note, commit it first, in its own commit (`git -C ~/bullet-journal commit -m "Add note on <topic>" -m "<your session trailer>" -- notes/<slug>.md`), without the `Log: ` prefix. The commit-msg hook allows `Log: ` only on commits that touch nothing but `YYYY-MM/LOG.md`.

Full spec: `~/bullet-journal/docs/agent-entries.md#conversation-entries`.
