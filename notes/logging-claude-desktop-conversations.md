---
title: Logging Claude Desktop conversations
description: Which Claude Desktop tabs can log a conversation to the journal, and how
---

- Code tab is Claude Code: skills, Edit/Bash and session ID all work, so "log this conversation" works as-is
- Cowork doesn't load ~/.claude/skills; the skills would have to be uploaded to the claude.ai account (Customize → Skills)
- Cowork exposes no session ID; a trailer like "Cowork-session: <conversation URL>" would still pass the commit hook
- Chat tab has no disk access, shell or session ID; recommended path is paste-back: ask Chat for an entry, paste it into Claude Code with "log this conversation"
- A filesystem connector would let Chat edit LOG.md, but not lint or commit, so it isn't worth it
- Open: whether Cowork has targeted file edits and can run git/pixi (unverified in docs; test by asking Cowork to log a test entry)
- Source: code.claude.com/docs/en/desktop.md, skills.md, claude.com/docs/cowork/overview.md
