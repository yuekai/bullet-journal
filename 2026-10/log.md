# October 2026

**Calendar:**

1 Th
2 F  : HL in China; daycare early dismissal at 1 PM
3 Sa : HL in China
4 Su : HL in China
5 M  : HL in China; daycare closed
6 Tu : HL in China
7 W
8 Th
9 F
10 Sa
11 Su
12 M
13 Tu
14 W
15 Th
16 F
17 Sa
18 Su
19 M
20 Tu
21 W
22 Th
23 F
24 Sa
25 Su
26 M
27 Tu
28 W
29 Th
30 F
31 Sa

**Tasks:**

## Thu, Oct 1, 2026

- [**Online p-value publication game**](online-p-value-publication-game.md) (`Claude-session: de1b2c20-8451-4307-a3d5-b50525cbdd03`)
- [**Strategic z-value publication game**](strategic-z-value-publication-game.md) (`Claude-session: de1b2c20-8451-4307-a3d5-b50525cbdd03`)
- [x] **Install journal skills on m2 and spark** (`~/bullet-journal` @ `89e6e23`)
  Agents on the Linux machines m2 and spark couldn't log their work: the journal wasn't cloned there and pixi.toml only supported osx-arm64, so the pixi-backed git hooks failed. Both machines now have the journal cloned over SSH, with `log-task` and `log-conversation` linked for Claude Code, Codex, DSH and Kimi Code. The workspace now also supports linux-64 and linux-aarch64.
- [x] **Add journal instructions to m2 and spark agents**
  The skills were installed on m2 and spark, but those machines' global agent instructions never told agents to use them, so nothing would get logged. The Bullet Journal section from this Mac's CLAUDE.md/AGENTS.md is now in each harness's global instructions there (Claude Code, Codex, DSH, Kimi Code), before Package Management. Other sections were left as-is, and the originals were backed up as `.bak`.
- [x] **Sync global agent instructions to m2 and spark**
  The remotes' global CLAUDE.md/AGENTS.md files had drifted from this Mac's: an older commit-memory scheme (spark's Codex still used `Memory:` trailers), different pixi rules, and no memory section in m2's CLAUDE.md. All four harnesses' files on both machines now match the local copies. The Mac-only Kimi desktop app section was dropped, since its paths don't exist on Linux.
