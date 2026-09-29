---
name: log-task
description: Use after completing a task that changed something (code, config, data, or computer-use work), in any directory, to log the work to the user's bullet journal at ~/bullet-journal as a task entry. Also use when the user asks to log, record tasks/work.
---

# Bullet journaling: log your completed work

The user's bullet journal at `~/bullet-journal` is long-term memory, readable by people, shared by all of their agents. When you finish a task, add one entry to today's daily log so that future agents, and the user, can see what was done, where, and why.

## When to log tasks/work

- **Log:** once per completed task that changed state, such as code, config, data, files, or actions taken on a computer. Log after the task's git commit, if there is one, so you can cite its hash.
- **Don't log:** pure Q and A sessions, exploration sessions that made no changes, work that was abandoned or reverted, minor changes (eg, cosmetic changes, typo fixes, etc).
- **Several distinct tasks in one session:** one entry each.

## 1. Write the entry

```markdown
- [x] **Add retry logic to dataset uploader** (`~/HDP-lib` @ `a1b2c3d`)
  Uploads to the Hub failed outright on transient 5xx errors, so long runs lost hours of work. The uploader now retries with exponential backoff.
  - Chose backoff over a persistent queue because failures are rare and short-lived
```

- **Subject:** bold, 50 chars max, capitalized, imperative mood ("If applied, this will ___"), no trailing period. It names the change.
- **Location:** `` (`~/repo` @ `<short hash>`) `` for committed work, or `` (`~/repo`) `` for uncommitted work. Abbreviate the path with `~`. Leave the location out for work that isn't in a repo.
  - The location is what marks the entry as an agent's for the linter, so include it whenever the work is in a repo.
- **Body:** indent every line with 2 spaces (never tabs). No blank lines.
  - Prose first, one line per paragraph, then optional sub-bullets, one level only. A prose line after a sub-bullet would render as part of it.
  - Explain how things worked before and what was wrong with that, how they work now, and why the change was implemented in the way it was.
  - Leave out implementation details (code is generally self-explanatory in this regard).
  - Leave the body empty for self-explanatory work (eg, fixing typos).
- If you made a commit, reuse its subject and body (but omit trailers).
- **No session trailer in the entry:** the commit the location cites, and the `Log:` commit that adds the entry, both carry it.
- **Never include** secrets, credentials, tokens, private personal data, or sensitive operational details.

## 2. Add it to today's log

Let `YYYY-MM` be the current month and `## Ddd, Mon D, YYYY` be today's header (eg, `## Mon, Sep 28, 2026`); don't zero-pad the header.

1. If `~/bullet-journal/YYYY-MM/LOG.md` doesn't exist, create it:
   ```bash
   pixi run --manifest-path ~/bullet-journal/pixi.toml init-monthly-log YYYY-MM
   ```
2. Read the file. If today's header is missing, insert it in date order: after the last earlier day's section, or after the `**Tasks:**` list if there are no daily sections yet. Surround it with blank lines.
3. Append your entry as a new top-level bullet at the end of today's section.

**Never rewrite a `LOG.md` as a whole;** ie, no `Write`/`write` tool, no Codex `*** Add File`/`*** Delete File`, no `>`, `tee` or `sed -i`, and no scripts. Other sessions may have appended entries since you read the file, and a whole-file write would erase them. Instead, **always use the Edit tool** (eg, Claude Code and Kimi Code's `Edit`). Anchor each edit on a few lines near the insertion point.

## 3. Lint and commit

```bash
pixi run --manifest-path ~/bullet-journal/pixi.toml lint
git -C ~/bullet-journal add YYYY-MM/LOG.md
git -C ~/bullet-journal commit -m "Log: <Subject>" -m "<your session trailer>" -- YYYY-MM/LOG.md
```

- **Lint and hook failures:** if lint or the pre-commit hook reports errors, fix *your* entry with the Edit tool as the message says, then retry.
- **Errors in someone else's entry:** don't rewrite another session's entry. That session is probably fixing it, so wait a few seconds and retry the commit. If it still fails, tell the user.
- **`.git/index.lock` exists:** another session is committing. Wait a few seconds and retry.
- **Commit scope:** commit only the log file you edited (`-- YYYY-MM/LOG.md`).
- **Commit subject:** `Log: ` plus the entry's subject. A commit-msg hook enforces it.

Full spec: `~/bullet-journal/docs/agent-entries.md`. Journal format: `~/bullet-journal/docs/journal-format.md`.
