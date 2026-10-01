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
- [x] **Set up bullet journaling on m2 and spark** (`~/bullet-journal` @ `89e6e23`)
  Agents on the Linux machines m2 and spark couldn't log their work: the journal wasn't cloned there, pixi.toml only supported osx-arm64 so the pixi-backed git hooks failed, and their global agent instructions never mentioned the journal. Both machines now have the journal cloned over SSH, with `log-task` and `log-conversation` linked for Claude Code, Codex, DSH and Kimi Code. Each harness's global CLAUDE.md/AGENTS.md there now has this Mac's Bullet Journal section, and the workspace also supports linux-64 and linux-aarch64.
- [x] **Sync global agent instructions to m2 and spark**
  The remotes' global CLAUDE.md/AGENTS.md files had drifted from this Mac's: an older commit-memory scheme (spark's Codex still used `Memory:` trailers), different pixi rules, and no memory section in m2's CLAUDE.md. All four harnesses' files on both machines now match the local copies. The Mac-only Kimi desktop app section was dropped, since its paths don't exist on Linux.
- [x] **Export repoprover rollouts for SFT on m2** (`~/statlib/repoprover`)
  The Sep 1 SFT export merged separate start..done segments (e.g. reviewer revisions) and pre/post-compaction dialogs into conversations the model never saw, and it validated against the shrd/ gate instead of `~/data-engineering/SFT/process_entry.py`. The untracked exporter on m2 now emits one entry per rollout, keeps only status `done`, and gates with that file's defaults. Result: 14,332 rollouts, 492.7M tokens (avg 34.4k), 1,421 rejected to `rollouts.rejects.jsonl`.
  - Spark's pilot runs and m2's `20260825-085031` contribute nothing: they predate reasoning capture, and the default gate requires think.
  - Re-gating a 500-record sample passed with no errors, and no rollout ids are duplicated.
