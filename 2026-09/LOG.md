# September 2026

**Calendar:**

1 Tu
2 W
3 Th
4 F
5 Sa
6 Su
7 M
8 Tu
9 W
10 Th
11 F
12 Sa
13 Su
14 M
15 Tu
16 W
17 Th
18 F
19 Sa
20 Su
21 M
22 Tu
23 W
24 Th
25 F
26 Sa
27 Su
28 M
29 Tu
30 W

**Tasks:**

## Mon, Sep 28, 2026

- [x] **Set up agent-maintained bullet journal** (`~/bullet-journal` @ `0cc3f39`)
  The previous journal (~/second-brain) was maintained by hand, and agents working in other repos had no shared place to record finished work. This repo keeps the second-brain layout and adds a bullet-journaling skill, installed for Claude Code, Codex, DSH and Kimi Code, that has agents log each completed task as a commit-message-style entry with their session trailer. A linter run from a pre-commit hook enforces the format, and agents edit logs only with Edit tools rather than a locked write script, to keep the machinery small.
- [x] **Prefix log commits and add global log reminder** (`~/bullet-journal` @ `0816918`)
  Journal-entry commits reused the entry's subject, so an agent's change to this repo and the commit logging it looked identical in git log. They now start with "Log: ", enforced by a commit-msg hook, and the one earlier log commit was renamed to match. Agents also only logged when a skill happened to trigger, so each harness's global instructions (Claude Code, Codex, DSH, Kimi Code) now carry the same Bullet Journal reminder, along with the renamed Repository Long-term Memory section.
- [x] **Lint user-written entries, not only agent entries** (`~/bullet-journal` @ `5522209`)
  The linter checked only the task marker on the user's own bullets, so stray prose, * or numbered bullets, orphaned indented lines, notes under **Tasks:**, and misused strikethrough all passed. It now checks every entry against the format, whoever wrote it. Indentation may be tabs or spaces, since the user edits in editors that disagree on which to insert, and levels are compared by relative width rather than a fixed unit.
- [x] **Recognize agent entries by session trailer** (`~/bullet-journal` @ `214209c`)
  The linter treated every "- [x] **" line as an agent entry, so a user's own bold task drew a "missing trailer" error. An item is now an agent entry only if it carries a session trailer, the one thing only agents write. The trade-off is that an agent entry that forgets its trailer reads as a user task, though the general entry rules still check it.
- [x] **Rename bullet-journaling skill to log-task** (`~/bullet-journal` @ `4d5af27`)
  With a second, conversation-logging skill coming, the generic name no longer said which kind of logging the skill does. install.sh now links every skill in skills/ and removes links left under a retired name. The Bullet Journal reminder in each harness's global instructions (Claude Code, Codex, DSH, Kimi Code) now names log-task.
- [x] **Add log-conversation skill and entry format** (`~/bullet-journal` @ `acc8c2c`)
  Agents logged only finished work, so the conclusions of brainstorming conversations were lost with the transcript. When the user asks, and only then, an agent now logs a note bullet whose one level of sub-bullets holds the conclusions, decisions and open questions, ending in a session-trailer sub-bullet. It's a separate skill from log-task because the two fire under opposite conditions (automatically vs. on request), and the global reminders now say so.
- **Logging Claude Desktop conversations** (`Claude-session: 6ccbfae8-746b-4612-af0c-95d1ed3b6fef`)
  - Code tab is Claude Code: skills, Edit/Bash and session ID all work, so "log this conversation" works as-is
  - Cowork doesn't load ~/.claude/skills; the skills would have to be uploaded to the claude.ai account (Customize → Skills)
  - Cowork exposes no session ID; a trailer like "Cowork-session: <conversation URL>" would still pass the commit hook
  - Chat tab has no disk access, shell or session ID; recommended path is paste-back: ask Chat for an entry, paste it into Claude Code with "log this conversation"
  - A filesystem connector would let Chat edit LOG.md, but not lint or commit, so it isn't worth it
  - Open: whether Cowork has targeted file edits and can run git/pixi (unverified in docs; test by asking Cowork to log a test entry)
  - Source: code.claude.com/docs/en/desktop.md, skills.md, claude.com/docs/cowork/overview.md
