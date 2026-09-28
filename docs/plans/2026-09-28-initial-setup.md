# Plan: agent-maintained bullet journal (`~/bullet-journal`)

Status: done (2026-09-28). The bullets under "Decisions confirmed with the user" include later revisions: the linter is `scripts/lint.py`, and the session-ID table was dropped in favor of each harness's user-global instructions.

## Context

The user is switching from `~/second-brain` (a hand-maintained markdown bullet journal) to this repo. The new journal also serves as long-term memory that people can read, for coding and computer-use agents running in *other* directories. Those agents record each finished task as a completed-task bullet whose text reads like a git commit message (subject plus before/after/why body) and ends with the agent's session ID. Agents, not the user, will mostly maintain the repo. So it follows harness-engineering principles:
- `AGENTS.md` is a short table of contents.
- `docs/` is the system of record.
- Rules are enforced by a linter, a pre-commit hook and tests, whose error messages tell the agent how to fix the problem.
- Agents and the user edit `LOG.md` directly; the linter keeps the format consistent.

No migration from `~/second-brain`.

Decisions confirmed with the user:
- **Bullet shape:** always a completed task, `- [x] **Subject** …`.
- **Auto-commit:** agents commit each entry to this repo right after writing it.
- **Harnesses:** Claude Code, Codex, DeepSeek Harness (DSH) and Kimi Code.
- **No write script:** agents edit `LOG.md` directly, then run the linter and commit. The user accepts a small risk of losing an entry when two sessions write at the same moment.

## Layout (carried over from second-brain)

```
AGENTS.md                      # ~60–100 line TOC: purpose, layout, commands, pointers to docs/
docs/
  journal-format.md            # LOG.md + notes/ format spec (ported from second-brain docs/bullet-journal-plugin-specs.md, minus index/future log/collections)
  agent-entries.md             # exact agent bullet grammar, session trailers per harness, commit behavior
  design.md                    # core beliefs + decisions (why scripted writes, why [x], why trailers match git trailers)
  plans/                       # checked-in execution plans for non-trivial changes to this repo (this plan goes here as the first one)
YYYY-MM/LOG.md                 # monthly log: calendar + Tasks + daily sections; optional YYYY-MM/assets/
notes/                         # long-form notes, kebab-case slug, frontmatter title/description
scripts/
  init_monthly_log.py          # ported from ~/second-brain/scripts/generate_monthly_log_skeleton.py (renamed; drop the legacy --logs-dir alias)
  lint.py                      # structural linter
skills/bullet-journaling/SKILL.md
.githooks/pre-commit           # runs `pixi run lint`
tests/                         # pytest: init_monthly_log (ported), lint
```

The LOG.md format is unchanged from `~/second-brain/AGENTS.md`: the `# Month YYYY` title, the `**Calendar:**` lines (`D Abbrev[ : event; event]`), `**Tasks:**`, and `## Mon, Sep 28, 2026` daily headers (no zero-padding). Task markers are `[ ]`, `[x]`, `[>]` and `[ ] ~~…~~`, and nesting uses tab indentation.

## Agent entry format (`docs/agent-entries.md`)

```markdown
## Mon, Sep 28, 2026

- [x] **Add retry logic to dataset uploader** (`~/HDP-lib` @ `a1b2c3d`)
	Uploads to the Hub failed outright on transient 5xx errors, so long runs lost hours of work. The uploader now retries with backoff; chose backoff over a queue because failures are rare and short-lived.
	Claude-session: 368d5791-4132-443f-8f46-b634c2d0d483
```

- **Subject line:** at most 50 characters, capitalized, imperative mood, no trailing period, in bold.
- **Location suffix (optional):** `` (`<repo, ~-abbreviated>` @ `<short hash>`) ``. It links the entry to that repo's commit history, which is the per-repo memory. Leave it out for work that isn't in a repo, such as computer use.
- **Body (optional):** one tab-indented continuation line per paragraph, with no blank lines, so the Markdown list item stays intact. Paragraphs follow the global commit guidelines: before, what was wrong, now, and why. No how-to details.
- **Trailer (required, last line):** the same trailer the harness already writes in git commits, so a single grep matches both systems.

The session ID and trailer key come from each harness's user-global `AGENTS.md`/`CLAUDE.md` (the same ones used for git commit trailers); the skill doesn't duplicate them.

## Logging procedure (in the skill, run from any cwd)

1. If `~/bullet-journal/YYYY-MM/LOG.md` doesn't exist, run `pixi run --manifest-path ~/bullet-journal/pixi.toml init-monthly-log YYYY-MM`.
2. If today's `## Mon, Sep 28, 2026` header is missing, insert it in chronological order (after `**Tasks:**` if there are no daily sections yet).
3. Append the entry at the end of today's section, right before committing.
   - **Required:** the `Edit` tool, or the harness's equivalent targeted string-replacement or patch tool, such as DSH's `edit` or Codex's `apply_patch`. These act on the file's current contents, so an entry another session just added survives.
   - **Prohibited:** overwriting the whole file with the `Write` tool, or with shell redirection like `cat > LOG.md`. That can silently discard another session's entry.
   - The skill states both rules, and `docs/agent-entries.md` explains why. There are no exceptions: agents never create or overwrite a log with `Write`. A new monthly log is created only by `init-monthly-log`. During implementation, check the exact edit-tool names in each harness's docs rather than guessing (especially Kimi's).
4. Run `pixi run --manifest-path ~/bullet-journal/pixi.toml lint` and fix anything it reports.
5. Commit only that file: `git -C ~/bullet-journal commit -m "<subject>" -m "<trailer>" -- YYYY-MM/LOG.md`. The commit subject is the entry subject, and the commit carries the same session trailer. The pre-commit hook runs the linter again.

## `scripts/lint.py` (pixi task `lint`)

Checks, each with a message that explains the fix and cites `docs/…`:
- **LOG.md:**
  - The directory name is `YYYY-MM` and matches the title.
  - The calendar has exactly the month's days with the correct weekday abbreviations.
  - `**Tasks:**` is present.
  - Daily headers are well-formed, belong to that month, are unique and are in ascending order.
  - Task markers are valid.
- **Agent entries:** any bullet that has a `*-session:` line, or a `- [x] **…**` first line, must follow the full grammar above.
- **notes/\*.md:** frontmatter has `title` and `description`, and the filename is a kebab-case slug.

`pixi run check` runs `lint` and then `pytest`. `.githooks/pre-commit` runs `pixi run lint`, so the check also covers commits made by hand or by an agent.

## Skill: `skills/bullet-journaling/SKILL.md`

It must work from any cwd and in any of the four harnesses, so every path is absolute and nothing depends on a harness-specific tool. Contents:
- **When to log:** after finishing a task that changed state (code, config, data, computer use), and after its git commit, if there is one. Skip pure Q&A and aborted work. One entry per completed task.
- **How to write it:** the subject and body rules, stated inline because other harnesses may not load the Claude global CLAUDE.md. Includes a good and a bad example. If the task produced a commit, reuse the commit message.
- **How to get the session ID:** defer to the harness's user-global instructions.
- **The logging procedure above,** with the exact commands. If lint fails, follow the error message.
- **Pointer:** `~/bullet-journal/docs/agent-entries.md` for the details.

Frontmatter description: "Use after completing a task to log the work to the user's bullet journal (~/bullet-journal)…".

## Install (pixi task `install`)

The `install` task runs `scripts/install.sh`, which does the following and can be re-run safely:
1. `git config core.hooksPath .githooks`
2. Symlinks `skills/bullet-journaling` into:
   - `~/.claude/skills/` (Claude Code)
   - `~/.agents/skills/` (Codex, and DSH's `user-agents` root per `~/deepseek-harness/docs/subsystems/skills.md`)
   - `~/.kimi-code/skills/` (Kimi Code)
3. Refuses to overwrite an existing non-symlink.

During implementation, confirm that Codex reads `~/.agents/skills/`. If it doesn't, also link into `~/.codex/skills/`.

The skill only tells agents to log their work; the harnesses load it on demand. As an optional follow-up, the user could add a one-line reminder to each harness's global AGENTS.md or CLAUDE.md. This plan does not edit those files.

## pixi

- `pixi add python pytest`, since pytest is on conda-forge.
- Tasks: `lint`, `test`, `check`, `init-monthly-log` (runs `scripts/init_monthly_log.py`), `install`.
- Keep the existing `.gitignore` and add `__pycache__/` and `.pytest_cache/`.

## Out of scope

- Porting the second-brain `/log` and `/migrate` skills. They could be added later under `skills/`.
- A doc-gardening agent.
- Migrating second-brain content.

## Verification

1. `pixi run check`: the linter and all tests pass. The tests cover:
   - `tests/test_init_monthly_log.py`, ported from `~/second-brain/tests/test_generate_monthly_log_skeleton.py`.
   - Lint cases: good and bad fixtures for each check. Each failure message must name the fix.
2. `pixi run install`, then check the symlinks with `ls -l` in each of the three skill directories.
3. From another directory (such as `~/second-brain`), follow the skill's procedure by hand for a test entry. Confirm that:
   - the entry lands under `## Mon, Sep 28, 2026` in `2026-09/LOG.md`,
   - `pixi run lint` passes,
   - `git log -1` in `~/bullet-journal` shows the subject and the `Claude-session:` trailer.

   Then break the entry on purpose (drop the trailer) and confirm that both lint and the pre-commit hook reject it with a message naming the fix.

   Then remove the test commit with `git reset --hard HEAD~1`, only if it was the sole new commit.
4. Make the initial commit of the scaffold, following the global commit guidelines and including the `Claude-session:` trailer.
