# Plan: log conversation summaries in the bullet journal

Status: done (2026-09-28). Landed as four commits: user-entry linting, trailer-based recognition, the log-task rename, and log-conversation. The long-summary rule is superseded by [linked-conversation-entries](2026-09-28-linked-conversation-entries.md).

## Context

Agents log only finished work, as `- [x] **Subject**` entries, so what a brainstorming or advice conversation concludes never reaches the journal. The user wants to be able to log those conclusions too.

Decisions the user made:
- **Where:** Claude Code sessions now. Claude Desktop is explained below.
- **Trigger:** only when the user asks, for example "log this conversation". Agents never log conversations on their own.
- **Shape:** a bujo *note* bullet with one level of sub-bullets, not a `[x]` task, so the log tells "discussed" apart from "done".
- **Recognition:** an agent entry is identified by its **session trailer**, not by top-level formatting such as `- [x] **`. The user can then write bold tasks and notes freely.

## Entry grammar

Conversation entry:

```markdown
- **Journal summaries for conversations**[ (`~/repo`)]
	- Conversations are logged only on request
	- They are note bullets with one level of sub-bullets
	- Details: [journal-summaries-for-conversations](../notes/journal-summaries-for-conversations.md)
	- Claude-session: 6ccbfae8-…
```

- **First line:** `- **Subject**` with an optional `` (`~/repo`) `` and nothing after it. The subject is a noun phrase naming the topic or conclusion (not imperative mood), at most 50 characters, capitalized, with no trailing period.
- **Children:** only `- ` sub-bullets at level 1 (a tab, or any consistent spaces). Nothing nests deeper, and there are no prose continuation lines.
- **Trailer:** the last sub-bullet, `\t- <Harness>-session: <id>`, exactly once.
- **Long summaries:** when a summary needs more than about 7 sub-bullets, or needs prose, write `notes/<slug>.md` (existing frontmatter rules apply) and add a link sub-bullet. Chat exports go in `YYYY-MM/assets/`.
- **Placement and content:** top-level in today's section. No secrets or private data.

**How the linter recognizes entries (it applies to both kinds):**
- A top-level item, together with its indented lines, is an **agent entry if and only if it contains a session-trailer line.** For a task entry that's a continuation line `\tX-session: id`; for a conversation entry it's a sub-bullet `\t- X-session: id`.
- An agent entry's first line must be `- [x] **Subject**…` (task entry, existing rules) or `- **Subject**…` (conversation entry, rules above). Any other first line is an error, and the message names both forms.
- A trailer-like line anywhere else is an error: deeper than level 1, not the last line of its item, or on a line of its own. The existing top-level-only rule becomes "a trailer at depth ≥2 means the entry is nested".
- **Behavior change:** a `- [x] **Bold**` task without a trailer is now an ordinary user task, where before it was a "missing trailer" error. The trade-off is that an agent that forgets its trailer is no longer caught. The user asked for this.

## Changes

There are four commits, in order. Each one changes docs, the linter and the tests together, per design belief 5. `scripts/check_commit_msg.py` needs **no change** in any of them.

**Commit 0: lint user-written entries**

- **What's wrong now:** for items the user writes, the linter checks only the task marker (`scripts/lint.py:134`). Anything else in the body is accepted: `* bullets`, space indentation, stray prose, notes under `**Tasks:**`, a malformed dropped task.
- **Change:** replace the line-by-line loop in `lint_body()` with a pass that splits the body after `**Tasks:**` into items. An item is a top-level `- ` line plus its indented lines. Commits A and C reuse this pass. Every item, whoever wrote it, is checked against the rules in `docs/journal-format.md`:
  - **Lines:** every non-blank line after `**Tasks:**` is a daily header, a `- ` bullet, or a continuation line. `*`/`+`/numbered bullets and unindented prose are errors.
  - **Indentation:** tabs or spaces are both accepted, but not mixed within one line's indent. A line's *level* comes from a stack of the indent widths seen so far in its item:
    - wider than the parent → one level deeper;
    - equal to an earlier width → that level;
    - between two earlier widths → an "inconsistent indentation" error.

    This also rules out jumping more than one level, and it applies to agent entries too. Agents still write tabs, as the skills say. `test_space_indented_continuation` flips from an error to valid.
  - **Continuation lines:** indented deeper than their item.
  - **Tasks:** the marker is `[ ]`, `[x]` or `[>]` (existing rule), and the task text isn't empty. `~~…~~` strikethrough appears only as `- [ ] ~~text~~` and wraps the whole text.
  - **Monthly tasks:** top-level items under `**Tasks:**` are tasks, not notes.
- **Docs:** state each rule explicitly in `docs/journal-format.md` ("Entries" section), where some are only implied now.
- **Tests:** one test per rule, plus a check that the valid full log still passes.
- **Scope:** `notes/<slug>.md` bodies stay free-form (long-form prose and headings). Only their filename and frontmatter are linted, as now.
- **Before committing:** run the new rules against `2026-09/LOG.md` and fix any violations with the Edit tool.

**Commit A: recognize agent entries by trailer (existing task logging)**

- **Why recognition is still needed after Commit 0:** Commit 0's rules apply to every entry. Agent entries also carry the commit-message rules that the user's own entries shouldn't have to follow:
  - a subject of at most 50 characters, capitalized, with no period;
  - the location format;
  - a body of plain lines with no sub-bullets;
  - exactly one trailer, and it comes last;
  - top-level placement in a daily section.

  Recognizing the entry is what applies those extra checks, and the trailer is the only reliable sign that an entry was written by an agent.

- **What's wrong now:** `lint_body()` (`scripts/lint.py:127`) treats every line matching `AGENT_START_RE` (`^\t*- \[x\] \*\*`) as an agent entry, so a user's own `- [x] **Bold task**` gets a "missing trailer" error.
- **`scripts/lint.py`:**
  - Using Commit 0's item pass, treat an item as an agent entry only if it contains a trailer. Agent entries are allowed only in daily sections.
  - Widen `TRAILER_LIKE_RE` to `^\s*(?:- )?[A-Za-z-]+-session:` so a bulleted trailer is detected too.
  - Send `[x]` groups to the existing `lint_agent_entry()`. Any other first line on a group that has a trailer is an error.
  - A trailer at depth ≥2 means the entry is nested, which is an error.
  - Pull the subject checks into a helper so Commit C can reuse them.
- **Tests:**
  - `test_missing_trailer` changes: a trailerless `- [x] **X**` is now valid.
  - New: `- [x] plain` + `\tClaude-session: x` and `- note` + `\t- Claude-session: x` are rejected.
  - `test_nested_agent_entry` keeps passing through the depth check.
- **Docs:** rewrite the "linter treats any line starting `- [x] **`" paragraph in `docs/agent-entries.md`. In `docs/design.md`, revise "bold subject … lets the linter recognize them" and add why the trailer is the recognizer: the user's own formatting is never mistaken for an agent entry, and an agent that forgets its trailer is no longer caught.

**Commit B: rename skill `bullet-journaling` → `log-task`**

- `git mv skills/bullet-journaling skills/log-task`, and set `name: log-task` in the frontmatter.
- `scripts/install.sh`:
  - Link every `skills/*/` directory, not one hard-coded name.
  - Remove a stale `bullet-journaling` link in each harness's skills dir, but only if it's a symlink into this repo.
  - Rerun `pixi run install`.
- Update references in `pixi.toml` (install description), `AGENTS.md` (map row and the logging rule), `docs/agent-entries.md:5` and `docs/design.md:27` ("One skill" → "Skills, installed as symlinks"). Leave the done plan `docs/plans/2026-09-28-initial-setup.md` and past `LOG.md` entries as history.

**Commit C: `log-conversation` skill and conversation entries**

1. **`scripts/lint.py`:** add `lint_convo_entry()` for groups whose first line is `- **Subject**[ (`~/repo`)]`. Its rules are only depth-1 `- ` sub-bullets, the trailer last, and the shared subject helper.
2. **`tests/test_lint.py`:**
   - Valid entries: with and without location and link. Add one to `test_full_valid_log`.
   - Errors: missing or not-last trailer, depth-2 sub-bullet, prose continuation line, bad subject.
   - `- **Idea**: text` without a trailer is a plain note.
3. **Docs**
   - `docs/agent-entries.md`: add a "Conversation entries" section.
   - `docs/journal-format.md`: add an Entries-table row and add an entry to the example log.
   - `docs/design.md`: add a Decisions bullet explaining note-shaped conversation entries, logging only on request, one level of nesting, and why there are two skills (each description is a precise trigger, so the automatic `log-task` never mentions conversations).
   - `AGENTS.md`: add a map row for `skills/log-conversation/`.
4. **`skills/log-conversation/SKILL.md`** (new)
   - `description`: "Use only when the user asks you to log, record, journal or summarize a conversation in their bullet journal."
   - Its own step 1 covers the conversation entry, with an example and a weak example.
   - For adding the entry to the log and committing it, it says to follow steps 2–3 of `~/bullet-journal/skills/log-task/SKILL.md`, so those rules stay in one place.
5. **Global reminders (outside the repo, not committed; keep the four files identical):** `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, `~/.kimi-code/AGENTS.md`, `~/.dsh/AGENTS.md`.
   - Change `bullet-journaling` to `log-task`.
   - Change "Skip pure Q&A…" to add "When I ask you to log a conversation, use the `log-conversation` skill."

**Wrap-up:** check this plan in as `docs/plans/2026-09-28-conversation-summaries.md` (in Commit C) and mark it done. Then log one `[x]` entry per commit with `log-task`.

## Claude Desktop

This is an explanation only; nothing here is built. Sources: code.claude.com/docs/en/desktop.md and skills.md, and claude.com/docs/cowork/overview.md.

- **Code tab:** this is Claude Code, so it works as soon as this plan lands. It loads `~/.claude/skills` and `~/.claude/CLAUDE.md`, has the Edit and Bash tools, and sets `CLAUDE_CODE_SESSION_ID`. Say "log this conversation" at the end.
- **Cowork tab:** it doesn't read `~/.claude/skills`, so both skills would need to be uploaded to the claude.ai account (Customize → Skills). The docs say it reads and writes local files. They don't say (unverified) whether it has targeted edits or can run `git`/`pixi`, and it exposes no session ID. A trailer like `Cowork-session: <conversation URL>` would still satisfy the hook. To check, open Cowork on `~/bullet-journal` and ask it to log a test entry.
- **Chat tab:** no skills from disk, no shell, and no session ID.
  - **Recommended:** at the end of a chat, ask it for a bullet-journal conversation entry in the grammar above. Paste that into a Claude Code session with "log this conversation", and that session commits it under its own trailer.
  - A Filesystem connector in `claude_desktop_config.json` would let Chat edit `LOG.md` directly. It still can't lint or commit, though, so that isn't worth it.

## Verification

- `pixi run check` (lint + pytest) passes.
- Live: in a scratch journal (`pixi run python scripts/lint.py --root <tmpdir>`), check that:
  - a conversation entry passes,
  - a trailerless `- [x] **Bold**` passes,
  - `- note` + `\t- Claude-session: x` fails with a fix-it message,
  - a depth-2 sub-bullet fails.
- The scratch journal also checks user entries: `* note`, a line with mixed tab and space indentation, an inconsistent indent, and `- [x] ~~done~~` each fail, and a space-indented child passes. Each failure comes with a fix-it message, while the existing `2026-09/LOG.md` passes.
- The real `LOG.md` is never touched for these checks.
- After `pixi run install`:
  - `ls -la ~/.claude/skills ~/.agents/skills ~/.kimi-code/skills` shows `log-task` and `log-conversation` links and no `bullet-journaling`.
  - `grep -rn bullet-journaling` finds only history (the old plan and past log entries).
