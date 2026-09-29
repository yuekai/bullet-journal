---
title: Logging Claude Desktop conversations
description: Which Claude Desktop tabs (Code, Cowork, Chat) can log a conversation to the journal, what each lacks, and the recommended workaround
---

Only the Desktop app's Code tab can log a conversation to this journal from start to finish. From the Chat tab, the recommended route is paste-back into Claude Code. Cowork is untested.

**What logging a conversation needs**, per [agent-entries](../docs/agent-entries.md#conversation-entries):
- The `log-conversation` skill ([SKILL.md](../skills/log-conversation/SKILL.md)), so the agent knows the entry format.
- Targeted edits to `LOG.md`. Whole-file writes are forbidden because other sessions may be appending at the same time ([editing rules](../docs/agent-entries.md#editing-rules)).
- A shell, to run `pixi run lint` and `git commit`.
- A session ID for the entry's `` (`<Harness>-session: <id>`) `` and for the commit trailer, which [check_commit_msg.py](../scripts/check_commit_msg.py) requires.

**Code tab:** it is Claude Code, so everything works, and "log this conversation" works as is.
- Skills load from `~/.claude/skills`, and global instructions load from `~/.claude/CLAUDE.md`.
- The Edit and Bash tools are available.
- `CLAUDE_CODE_SESSION_ID` is set.
- This covers local sessions only. Cloud sessions don't load `~/.claude/CLAUDE.md`.

**Cowork tab:**
- **Skills:** it doesn't read `~/.claude/skills`. Skills come from the claude.ai account (Customize → Skills), so both `log-task` and `log-conversation` would have to be uploaded there.
- **Global instructions:** it doesn't read `~/.claude/CLAUDE.md`. Where it gets account-level instructions isn't documented.
- **Files and shell:** the docs say it reads and writes local files. They don't say whether it can make targeted edits or only write whole files, or whether it can run `git` and `pixi`. Both are unverified.
- **Session ID:** none is documented. A trailer like `Cowork-session: <conversation URL>` would still pass the commit hook and the linter, since both accept any `<Name>-session: <value>` with no spaces. The cost is that the value can't be grepped for anywhere else.

**Chat tab:**
- It has no skills from disk, no shell, no disk access and no session ID.
- MCP servers configured in `claude_desktop_config.json` are available to Chat as well as to the Code tab. With a Filesystem MCP server scoped to `~/bullet-journal`, Chat could edit `LOG.md` directly, but whether it can make targeted edits is unverified. Chat also couldn't lint or commit, so its entry would stay uncommitted until another session's `Log:` commit swept it in under the wrong subject. This isn't worth it unless a shell connector is added too.

**Recommendation:** log from the Code tab. For a Chat conversation, at the end ask Chat for a bullet-journal conversation entry in the [format](../docs/agent-entries.md#conversation-entries). Then paste it into a Claude Code session with "log this conversation". That session lints and commits it under its own session trailer.

**Open:** can Cowork make targeted file edits and run `git` and `pixi`? To find out, open Cowork on `~/bullet-journal` and ask it to log a test entry.

**Sources:**
- [Conversation summaries plan, § Claude Desktop](../docs/plans/2026-09-28-conversation-summaries.md#claude-desktop)
- https://code.claude.com/docs/en/desktop.md (skills, file editing and the terminal in the Code tab; MCP servers shared with Chat)
- https://code.claude.com/docs/en/skills.md (skills in Cowork and cloud sessions; string substitutions)
- https://code.claude.com/docs/en/env-vars.md (`CLAUDE_CODE_SESSION_ID`)
- https://code.claude.com/docs/en/settings.md (scope of `CLAUDE.md`; Cowork file access)
- https://claude.com/docs/cowork/overview.md
