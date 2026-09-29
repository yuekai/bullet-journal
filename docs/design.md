# Design

Core beliefs and the reasons behind the decisions that shape this repo. When a decision changes, edit it here in place; the reasoning behind each change goes in its commit message.

## Core beliefs

1. **Everything is in the repo.** Whatever an agent needs to maintain the journal is checked in: formats in `docs/`, procedures in `skills/`, and rules in `scripts/lint.py`. Anything that lives only in a chat or in someone's head effectively doesn't exist for the next agent.
2. **Readable by people first.** The journal is plain Markdown that the user can read, and edit in Obsidian or any editor, with no tooling. Agents adapt to the format; the format isn't bent for agents.
3. **Enforce rules mechanically, and make errors explain themselves.** A rule that can be checked is checked by `pixi run lint`, from the pre-commit hook, and each error says how to fix it and which doc explains why. Prose in `docs/` covers only what a linter can't judge, such as whether a subject is in the imperative mood.
4. **`AGENTS.md` is a map, not a manual.** It stays short and points into `docs/`. Details live in exactly one doc.
5. **Docs, linter and tests change together.** A format change updates `docs/`, `scripts/lint.py` and `tests/` in the same commit, so the three never drift apart.

## Decisions

- **Monthly folders hold both monthly and daily logs** (`YYYY-MM/LOG.md`, plus `assets/`). This is carried over from `~/second-brain`: a month is small enough to read in one sitting, and daily sections inside it keep the file tree shallow.
- **No index and no future log.** The file tree is the index. Future tasks go straight into the target month's log.
- **Agent work is logged as a completed task (`- [x] **Subject**`).** The user chose this over note bullets so finished work reads as done at a glance. The bold subject makes agent entries stand out from the user's own tasks when reading.
- **Conversations are logged as notes, only when the user asks.** Brainstorming and advice conversations reach conclusions that were otherwise lost with the transcript.
  - **Note bullet with sub-bullets** (`- **Subject**`), not `[x]`: a bujo note records what was discussed, so the log keeps "discussed" apart from "done".
  - **Optional prose, then one level of sub-bullets**, the same body shape as a task entry: the entry stays scannable, and anything longer goes to `notes/`.
  - **Session ID in parentheses after the subject**, where a task entry has its location. A conversation has no commit to point to, so the ID must live in the entry. Putting it on the first line keeps the body free for conclusions.
  - **On request only:** the user decides which conversations are worth remembering. Logging automatically would fill the journal with chats the user doesn't care about.
- **Two skills, `log-task` and `log-conversation`.** An agent decides whether to load a skill from its description alone, and the two fire under opposite conditions: `log-task` automatically after work, `log-conversation` only on request. Separate skills keep each trigger precise, and `log-task` never mentions conversations, so an agent can't log a chat unasked. `log-conversation` points to `log-task` for editing and committing, so those rules live in one place.
- **The first line marks an agent entry.** A bold `[x]` with a backticked location is a task entry, and a bold note with a session ID is a conversation entry. Treating every `- [x] **…` line as an agent entry would give the user's own bold tasks agent-entry errors, and task entries no longer carry a trailer to tell them apart. This is a heuristic. An agent's computer-use entry has no location, so it reads as a user task and gets only the general entry rules.
- **Task entries read like commit messages but carry no session trailer.** Each repo's git history is already its detailed memory, following the global commit-message guidelines, and the journal is the cross-repo timeline. The entry's location points to the commit, which carries the trailer. The `Log:` commit that adds the entry carries it too, so the session is still one lookup away. Repeating it in every entry was noise when reading the journal.
- **Journal-entry commits are prefixed `Log: `.** Without the prefix, an agent's change commit to this repo and the commit logging that change would share a subject, and `git log --oneline` would stop reading as an index. A commit-msg hook enforces the prefix.
- **Agents edit `LOG.md` directly; there is no write script.** A dedicated append script with a file lock was considered and rejected as more machinery than a journal needs. To keep the risk of lost updates small instead:
  - agents must use the Edit tool (targeted replacement) and never overwrite the whole file,
  - new months are created only by `init-monthly-log`,
  - each entry is committed right away.

  The remaining race, two sessions editing the same few lines at the same instant, is accepted.
- **The linter is strict for new content.** It rejects the loose habits of the old journal: empty calendar ` :`, headers without a weekday, wrong weekdays. The linter only has to be correct for logs this repo creates.
- **The linter checks every entry, not only agent entries.** The user's own bullets follow the same format, so malformed items (stray prose, `*` bullets, broken nesting, misused strikethrough) are caught whoever wrote them. Indentation may use tabs or spaces, because the user edits in Obsidian and other editors, which don't agree on which to insert. Levels are compared by relative width, not a fixed unit, and a tab counts as 2 spaces. Agent entries must use 2 spaces per level, since agents write them. If an editor turns an agent entry's indent into tabs, lint fails until the indent is fixed.
- **Skills, installed as symlinks.** `pixi run install` links each directory in `skills/` into each harness's user skills directory. Symlinks mean an edit in this repo reaches every harness immediately. A renamed skill's old name is listed in `scripts/install.sh` so that its stale links get removed.
