# Agent entries

When a coding or computer-use agent finishes a task, in any directory, it logs the work as one entry in today's daily log section. The entry is written like a git commit message, so the journal reads as a single timeline of what was done across all repos and machines, and why.

The procedure agents follow lives in the skill, [`skills/bullet-journaling/SKILL.md`](../skills/bullet-journaling/SKILL.md). This page is the spec that `scripts/lint.py` enforces.

## Grammar

```markdown
- [x] **<Subject>**[ (`<repo>`[ @ `<commit>`])]
	<body paragraph>
	<body paragraph>
	<Harness>-session: <session-id>
```

Example:

```markdown
- [x] **Add retry logic to dataset uploader** (`~/HDP-lib` @ `a1b2c3d`)
	Uploads to the Hub failed outright on transient 5xx errors, so long runs lost hours of work. The uploader now retries with exponential backoff; chose backoff over a persistent queue because failures are rare and short-lived.
	Claude-session: 368d5791-4132-443f-8f46-b634c2d0d483
```

- **Marker:** always `- [x]`, because the entry records finished work. An agent entry is a new top-level bullet in today's section. It is never nested under one of the user's tasks.
- **Subject:** bold, at most 50 characters, capitalized, imperative mood ("If applied, this will ___"), no trailing period. It names the change.
- **Location (optional):** `` (`~/repo`) `` or `` (`~/repo` @ `<short hash>`) ``.
  - Abbreviate the repo path with `~`.
  - Include the hash when the work was committed. The entry then points to that repo's commit history, which holds the detailed per-repo memory.
  - Leave the location out for work that isn't in a repo, such as computer use.
- **Body (optional; leave it out only for self-explanatory work):**
  - Write one line per paragraph, indented with exactly one tab more than the bullet.
  - No blank lines and no nested bullets: a blank line would end the list item.
  - Explain how things worked before and what was wrong with that, how they work now, and why it was done this way.
  - Leave out how it was implemented; the commit and the code record that.
  - When the work produced a commit, reuse the commit body.
- **Trailer (required, last line):** `<Harness>-session: <id>`.
  - It is the same trailer, with the same session ID, that the agent's harness writes in git commits, as prescribed by that harness's user-global `AGENTS.md` or `CLAUDE.md`. For example, Claude Code writes `Claude-session: $CLAUDE_CODE_SESSION_ID`.
  - Because the two match, `git log --grep` in a repo and `grep` in this journal find the same session.
- **Content:** no secrets, credentials, tokens, private personal data, or sensitive operational details.

The linter treats any line starting `- [x] **` as an agent entry. Any line that looks like a `…-session:` trailer must be the last line of one.

## Editing rules

Several agent sessions may log to the same `LOG.md` at the same time. There is no lock, so these rules keep one session from silently erasing another session's entry:

- **Required:** use the Edit tool. Each harness has one:
  - Claude Code and Kimi Code: `Edit`
  - DeepSeek Harness: `edit`
  - Codex: `apply_patch` with `*** Update File`

  These tools replace a small span of the file *as it is on disk now*, so an entry another session appended a moment ago survives.
- **Prohibited, with no exceptions:** rewriting a `LOG.md` as a whole. That includes:
  - the `Write` or `write` tool,
  - Codex `*** Add File` or `*** Delete File`,
  - shell redirection (`>`, `tee`, `sed -i`),
  - scripts that read, modify and write the file.

  A whole-file write puts back whatever the agent read earlier and erases anything added since.
- **New months:** a monthly log that doesn't exist yet is created only by `init-monthly-log`.
- **Timing:** edit right before committing, and anchor the edit on text near the end of today's section, not on the whole section.

## Committing

Every entry is committed right away, and only the file that was touched:

```bash
git -C ~/bullet-journal add YYYY-MM/LOG.md
git -C ~/bullet-journal commit -m "<Subject>" -m "<Harness>-session: <id>" -- YYYY-MM/LOG.md
```

- **Commit message:** the subject is the entry's subject, and the trailer is the entry's trailer. The entry itself serves as the body.
- **`-- <path>`:** commits only that file, even if another session has something else staged.
- **Pre-commit hook:** runs `pixi run lint`. If it fails, fix the reported lines with the Edit tool and commit again.
