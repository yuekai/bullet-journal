---
name: bullet-journaling
description: Use after completing a task that changed something (code, config, data, or computer-use work), in any directory, to log the work to the user's bullet journal at ~/bullet-journal as a commit-message-style entry with your session ID. Also use when the user asks to log, record, or journal work.
---

# Bullet journaling: log your completed work

The user's bullet journal at `~/bullet-journal` is long-term memory, readable by people, shared by all of their agents. When you finish a task, add one entry to today's daily log so that future agents, and the user, can see what was done, where, and why.

Every path below is absolute, so this works from any working directory.

## When to log

- **Log:** once per completed task that changed state, such as code, config, data, files, or actions taken on a computer. Log after the task's git commit, if there is one, so you can cite its hash.
- **Don't log:** pure questions and answers, exploration that changed nothing, or work that was abandoned or reverted.
- **Several distinct tasks in one session:** one entry each.

## 1. Write the entry

```markdown
- [x] **Add retry logic to dataset uploader** (`~/HDP-lib` @ `a1b2c3d`)
	Uploads to the Hub failed outright on transient 5xx errors, so long runs lost hours of work. The uploader now retries with exponential backoff; chose backoff over a persistent queue because failures are rare and short-lived.
	Claude-session: 368d5791-4132-443f-8f46-b634c2d0d483
```

- **Subject:** bold, at most 50 characters, capitalized, imperative mood ("If applied, this will ___"), no trailing period. It names the change.
- **Location:** `` (`~/repo` @ `<short hash>`) `` for committed work, or `` (`~/repo`) `` for uncommitted work. Abbreviate the path with `~`. Leave the location out for work that isn't in a repo.
- **Body:** one line per paragraph, each indented with a single tab. No blank lines and no sub-bullets.
  - Explain how things worked before and what was wrong with that, how they work now, and why you did it this way.
  - Leave out implementation details.
  - If you made a commit, reuse its body.
  - Leave the body out only for self-explanatory work.
- **Trailer (last line, tab-indented):** use the same session trailer your harness's user-global `AGENTS.md` or `CLAUDE.md` tells you to put in git commits, with the same session ID. Claude Code, for example, writes `Claude-session: $CLAUDE_CODE_SESSION_ID`.
- **Never include** secrets, credentials, tokens, private personal data, or sensitive operational details.

Weak entry:

```markdown
- [x] **Updated files.**
	Changed uploader.py to add a for-loop with try/except and time.sleep.
```

This is vague, has a trailing period, describes *how* instead of *why*, gives no location, and has no trailer.

## 2. Add it to today's log

Let `YYYY-MM` be the current month and `## Ddd, Mon D, YYYY` today's header, for example `## Mon, Sep 28, 2026`. Use no zero-padding and make sure the weekday matches the date.

1. If `~/bullet-journal/YYYY-MM/LOG.md` doesn't exist, create it:
   ```bash
   pixi run --manifest-path ~/bullet-journal/pixi.toml init-monthly-log YYYY-MM
   ```
2. Read the file. If today's header is missing, insert it in date order: after the last earlier day's section, or after the `**Tasks:**` list if there are no daily sections yet. Surround it with blank lines.
3. Append your entry as a new top-level bullet at the end of today's section.

**You must use the Edit tool** (Claude Code and Kimi Code: `Edit`; DeepSeek Harness: `edit`; Codex: `apply_patch` with `*** Update File`). Anchor each edit on a few lines near the insertion point.

**Never rewrite a `LOG.md` as a whole, with no exceptions.** That means no `Write`/`write` tool, no Codex `*** Add File`/`*** Delete File`, no `>`, `tee` or `sed -i`, and no scripts. Other sessions may have appended entries since you read the file, and a whole-file write would erase them.

## 3. Lint and commit

```bash
pixi run --manifest-path ~/bullet-journal/pixi.toml lint
git -C ~/bullet-journal add YYYY-MM/LOG.md
git -C ~/bullet-journal commit -m "<Subject>" -m "<your session trailer>" -- YYYY-MM/LOG.md
```

- **Lint and hook failures:** if lint or the pre-commit hook reports errors, fix *your* entry with the Edit tool as the message says, then retry.
- **Errors in someone else's entry:** don't rewrite another session's entry. Mention the error to the user instead.
- **Commit scope:** commit only the log file you edited (`-- YYYY-MM/LOG.md`).

Full spec: `~/bullet-journal/docs/agent-entries.md`. Journal format: `~/bullet-journal/docs/journal-format.md`.
