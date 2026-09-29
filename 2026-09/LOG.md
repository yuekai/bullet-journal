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
	Claude-session: 368d5791-4132-443f-8f46-b634c2d0d483
- [x] **Prefix log commits and add global log reminder** (`~/bullet-journal` @ `0816918`)
	Journal-entry commits reused the entry's subject, so an agent's change to this repo and the commit logging it looked identical in git log. They now start with "Log: ", enforced by a commit-msg hook, and the one earlier log commit was renamed to match. Agents also only logged when a skill happened to trigger, so each harness's global instructions (Claude Code, Codex, DSH, Kimi Code) now carry the same Bullet Journal reminder, along with the renamed Repository Long-term Memory section.
	Claude-session: 368d5791-4132-443f-8f46-b634c2d0d483
- [x] **Lint user-written entries, not only agent entries** (`~/bullet-journal` @ `5522209`)
	The linter checked only the task marker on the user's own bullets, so stray prose, * or numbered bullets, orphaned indented lines, notes under **Tasks:**, and misused strikethrough all passed. It now checks every entry against the format, whoever wrote it. Indentation may be tabs or spaces, since the user edits in editors that disagree on which to insert, and levels are compared by relative width rather than a fixed unit.
	Claude-session: 6ccbfae8-746b-4612-af0c-95d1ed3b6fef
