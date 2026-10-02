# Agent entries

Agents write two kinds of entry in today's daily log section. This page is the spec for both, and `scripts/lint.py` enforces it.

- **Task entries:** when a coding or computer-use agent finishes a task, in any directory, it logs the work as one entry. The entry is written like a git commit message, so the journal reads as a single timeline of what was done across all repos and machines, and why. Procedure: [`skills/log-task/SKILL.md`](../skills/log-task/SKILL.md).
- **Conversation entries:** when the user asks, and only then, an agent logs what a conversation concluded, such as a brainstorm's decisions and open questions. An agent may offer to log one when a session doesn't complete tasks/work but reaches conclusions worth keeping; log only if the user agrees. Procedure: [`skills/log-conversation/SKILL.md`](../skills/log-conversation/SKILL.md).

## Task entries

```markdown
- [x] **<Subject>**[ (`<repo>`[ @ `<commit>`])]
  <body paragraph>
  <body paragraph>
  - <sub-bullet>
```

Example:

```markdown
- [x] **Add retry logic to dataset uploader** (`~/HDP-lib` @ `a1b2c3d`)
  Uploads to the Hub failed outright on transient 5xx errors, so long runs lost hours of work. The uploader now retries with exponential backoff.
  - Chose backoff over a persistent queue because failures are rare and short-lived
```

- **Marker:** always `- [x]`, because the entry records finished work. An agent entry is a new top-level bullet in today's section. It is never nested under one of the user's tasks.
- **Subject:** bold, at most 50 characters, capitalized, imperative mood ("If applied, this will ___"), no trailing period. It names the change.
- **Location (whenever the work is in a repo):** `` (`~/repo`) `` or `` (`~/repo` @ `<short hash>`) ``.
  - Abbreviate the repo path with `~`.
  - Include the hash when the work was committed. The entry then points to that repo's commit history, which holds the detailed per-repo memory.
  - Leave the location out for work that isn't in a repo, such as computer use.
  - The location is also what tells the linter that the entry is an agent's (see [below](#how-the-linter-recognizes-agent-entries)).
- **Body (optional; leave it out only for self-explanatory work):** see [Body](#body).
  - Explain how things worked before and what was wrong with that, how they work now, and why it was done this way.
  - Leave out how it was implemented; the commit and the code record that.
  - When the work produced a commit, reuse the commit body.
- **No session trailer.** The session is recorded in the commit the location cites and in the `Log:` commit that adds the entry (see [Committing](#committing)), so `git log --grep` in a repo, or `git log -S '<Subject>'` here, finds it.
- **Content:** no secrets, credentials, tokens, private personal data, or sensitive operational details.

## Conversation entries

```markdown
- **<Subject>** (`<Harness>-session: <session-id>`)
  <optional prose paragraph>
  - <conclusion, decision or open question>
  - <…>
```

Conversation entries whose body exceeds 500 characters are written as notes; the entries are linked subjects, with an optional short body for anything about the note itself, such as where copies of it live:

```markdown
- [**<Subject>**](<slug>.md) (`<Harness>-session: <session-id>`)
  <optional prose paragraph or sub-bullets, at most 500 characters>
```

Examples:

```markdown
- **Journal summaries for conversations** (`Claude-session: 6ccbfae8-746b-4612-af0c-95d1ed3b6fef`)
  Conversation conclusions were lost with the transcript, so they are now logged on request.
  - Entries are note bullets, not [x] tasks, so "discussed" reads differently from "done"
  - Open: Claude Desktop chats need a paste-back step
- [**Logging Claude Desktop conversations**](logging-claude-desktop-conversations.md) (`Claude-session: 6ccbfae8-746b-4612-af0c-95d1ed3b6fef`)
```

- **When:** only when the user asks, for example "log this conversation". Never on the agent's own initiative.
- **Marker:** a note bullet (`- `), not a task, because a conversation reached conclusions rather than finishing work. Like a task entry, it is a new top-level bullet in today's section.
- **Subject:** bold, at most 50 characters, capitalized, no trailing period. It is a noun phrase naming the topic or its conclusion, such as "Pricing options for the Q4 plan", not an imperative.
- **Session:** in parentheses after the subject (eg, `` (`<trailer>`) ``), where `<trailer>` is the same session trailer your user-global `AGENTS.md` or `CLAUDE.md` tells you to put in git commits, with the same session ID. Claude Code, for example, writes `` (`Claude-session: $CLAUDE_CODE_SESSION_ID`) ``. It takes the place a task entry's location occupies. There's no repo location, and there's no commit to point to, so the ID goes in the entry itself.
- **Body (required, at most 500 characters):** see [Body](#body). The count is the body's text, without indentation.
  - One point per sub-bullet: a conclusion, a decision (with its reason when it isn't obvious), or an open question (prefix `Open: `).
  - Put chat exports in `YYYY-MM/assets/` and link them from a sub-bullet.
- **Long conversations:** if the body exceeds 500 characters, write it as a self-contained note in `YYYY-MM/<slug>.md`, in the same folder as the log (see the [notes format](journal-format.md#notes-yyyy-mmslugmd)). Make the subject a link to the note. The entry may keep a short body (same shape and 500-character limit) for related work, such as a copy of the note made elsewhere, so one entry covers it instead of a separate task entry; the conclusions themselves stay in the note, so the log stays scannable. The session stays on the entry. Chat exports are linked from the note.
- **Content:** no secrets, credentials, tokens, private personal data, or sensitive operational details.
- **Committing:** same as a task entry: `Log: <Subject>` plus the trailer. See [Committing](#committing). A note is committed first, in its own commit without the `Log: ` prefix.

## Body

Task and conversation entries share one body shape:

- Indent every line with 2 spaces, never tabs.
- Prose paragraphs come first, one line each, one level under the bullet. Sub-bullets follow, one level only. A prose line after a sub-bullet would render as part of that sub-bullet.
- No blank lines: a blank line would end the list item.
- No lines that look like old-style session trailers (`Claude-session: …` or `- Claude-session: …`).

## How the linter recognizes agent entries

The first line marks an entry as an agent's:

- **Task entry:** a top-level line starting ``- [x] **Subject** (` ``, that is, a bold completed task followed by a backticked location. The linter then checks the whole location, the subject and the body.
- **Conversation entry:** a top-level `- **…` or `- [**…` line containing `-session:`. The linter checks the subject, the session, and the body's shape and length. For a linked entry, it checks that the note exists; a body is optional.
- **Anything else is the user's own:** a `- [x] **Bold**` task with no location, or with a plain parenthetical such as `(Oahu)`, is an ordinary user task. The rules on this page don't apply to it, but the general [entry rules](journal-format.md#entries) still do.
- **Errors:**
  - an agent entry nested under another item;
  - an agent entry under `**Tasks:**`;
  - a session trailer on a line of its own, anywhere.

This is a heuristic: an agent's computer-use task entry has no location, so it is linted only by the general rules.

## Editing rules

Several agent sessions may log to the same `log.md` at the same time. There is no lock, so these rules keep one session from silently erasing another session's entry:

- **Required:** use the Edit tool. Each harness has one:
  - Claude Code and Kimi Code: `Edit`
  - DeepSeek Harness: `edit`
  - Codex: `apply_patch` with `*** Update File`

  These tools replace a small span of the file *as it is on disk now*, so an entry another session appended a moment ago survives.
- **Prohibited, with no exceptions:** rewriting a `log.md` as a whole. That includes:
  - the `Write` or `write` tool,
  - Codex `*** Add File` or `*** Delete File`,
  - shell redirection (`>`, `tee`, `sed -i`),
  - scripts that read, modify and write the file.

  A whole-file write puts back whatever the agent read earlier and erases anything added since.
- **New months:** a monthly log that doesn't exist yet is created only by `init-monthly-log`.
- **Timing:** edit right before committing, and anchor the edit on text near the end of today's section, not on the whole section.
- **Pull first:** the journal is shared by several machines through GitHub. Before reading the log, pull:
  ```bash
  git -C ~/bullet-journal pull --rebase --autostash origin main
  ```
  - If the remote is unreachable (eg, offline), log locally anyway and tell the user; the next pull and push will sync it.
  - If the rebase stops on a conflict, run `git -C ~/bullet-journal rebase --abort` and tell the user. Don't resolve conflicts in another session's or machine's entries.

## Committing

Every entry is committed right away, and only the file that was touched, then pushed:

```bash
git -C ~/bullet-journal add YYYY-MM/log.md
git -C ~/bullet-journal commit -m "Log: <Subject>" -m "<Harness>-session: <id>" -- YYYY-MM/log.md
git -C ~/bullet-journal push origin main
```

- **Commit message:** the subject is `Log: ` followed by the entry's subject, and the trailer is the agent's session trailer. The entry itself serves as the body.
  - For a task entry, which carries no trailer, this commit is what ties the entry to its session.
  - The prefix keeps `git log --oneline` readable when an agent logs work on this repo, where the change commit and its log commit would otherwise share a subject.
  - The prefix can push the subject past 50 characters; that's accepted.
- **`-- <path>`:** commits only that file, even if another session has something else staged.
- **Pre-commit hook:** runs `pixi run lint`. If it fails, fix the reported lines with the Edit tool and commit again.
- **Commit-msg hook:** runs `scripts/check_commit_msg.py`.
  - A commit that touches only `YYYY-MM/log.md` files must have a `Log: ` subject and a session trailer.
  - A `Log: ` subject on a commit that touches anything else, including a note, is rejected.
- **Push:** if the push is rejected because the remote moved on, pull (as above) and push once more. If that fails too, leave the commit local and tell the user.
