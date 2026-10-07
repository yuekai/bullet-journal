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
  - The trajectories are in `~/shrd/statlib/rollouts.jsonl`. Rejects, per-run parts and the export summary stay in `~/statlib/`.
  - Spark's pilot runs and m2's `20260825-085031` contribute nothing: they predate reasoning capture, and the default gate requires think.
  - Re-gating a 500-record sample passed with no errors, and no rollout ids are duplicated.
- [x] **Refresh Danus SFT export on m2** (`~/Danus`)
  The Sep 2 trajectory export missed the last week of linalg runs and all of solveall, and it had been gated against the shrd/ copy of the validator. The existing exporter and validator scripts were re-run unchanged over all runtime/kimi-home sessions and gated with `~/data-engineering/SFT/process_entry.py`. Result: 33,174 of 33,776 trajectories kept (98.2%), 3.91B tokens, averaging 117.8k (median 92.4k). The earlier run kept 20,006 trajectories and 2.40B tokens.
  - The trajectories are in `~/shrd/Danus/runtime/exports/sft_trajectories.jsonl` on m2. Candidates, failures and `export_report.md` sit beside it, and the Sep 2 files are archived in `2026-09-02/` there.
  - Drops are model-side violations such as string-encoded array args, invented args and repetition loops, so they stay dropped. The orchestrator's own operator sessions in `~/.kimi-code` stay out of scope.
- [x] **Export all Rethlas Kimi trajectories on m2** (`~/Rethlas`)
  The Aug 20 Rethlas export covered solveall only, was gated against the shrd/ validator copy, and discarded the validator's token counts. The untracked exporter now keeps the validated entries with their counts, and it was re-run over every linalg and solveall Kimi archive, gated with `~/data-engineering/SFT/process_entry.py`. Result: 314 of 331 trajectories kept, 38.6M tokens, averaging 122.9k (median 98.7k). The Aug 20 run kept 313.
  - Codex runs (2,318 gpt-5.6 sessions) are excluded: their reasoning is encrypted, so none can pass the gate's think requirement. The 3 linalg Kimi archives hold no completed assistant turn, so linalg contributes nothing.
  - Outputs, rejects and `export_report.md` are in `~/shrd/Rethlas/exports/` on m2. The Aug 20 files are archived in `2026-08-20/` there.
- **LeanMarathon ErdosGraham run artifacts on m2** (`Claude-session: 707489e6-0609-4211-903c-7958b3ba46fd`)
  The only LeanMarathon run (Jul 1–2) is on m2, with nothing on spark. The checkout is `~/shrd/LeanProofs/LeanMarathon`; per-target state is in its `.orchestrator-repos/UMich-FATML/ErdosGraham/`.
  - Logs: `.orchestrator-runs/` (audit/result JSON, 76 job logs)
  - Trajectories: `.codex-session-home/<job>/sessions/**/rollout-*.jsonl` (76 Codex rollouts, 44 MB)
  - Unfinished: stage 2 stopped in round 9 when its Refiner's PR #75 didn't merge; 34 nodes merged, 14 `sorry`s left in `Main.lean`
- [**Scientific skills database access costs**](scientific-skills-database-access-costs.md) (`Claude-session: 38c27805-0f74-49ad-b513-674f7466a5dc`)

## Fri, Oct 2, 2026

- [**How Danus makes incremental progress**](how-danus-makes-incremental-progress.md) (`Claude-session: 423756ed-138e-4655-953b-e446f411af8c`)
- [**Math SFT data pipelines**](math-sft-data-pipelines.md) (`Claude-session: 01066a2f-4222-44b3-a973-8c5ee55989f8`)
  A copy of the note describing the arxivmath, arxivlean, repoprover, Rethlas and Danus data pipelines sits at `~/shrd/math-sft-data-pipelines.md` on m2. It is a one-off snapshot of the journal note at `3e10d7f` and won't track later edits.
- [x] **Allow short bodies on linked conversation entries** (`~/bullet-journal` @ `94a1bcd`)
  A linked entry had to be a bare subject, so related work like copying the note elsewhere needed a second task entry. Linked entries may now keep an optional body under the usual shape and 500-character limit, so one entry covers the note and that work.
- [**Answer-conditioned reasoning**](answer-conditioned-reasoning.md) (`Claude-session: 480592c9-9154-47c0-8a6c-e5339fc733aa`)
  Revised the same day: a new proposal-distributions section covers hinted sampling and MCMC projection sampling (Karan, Chen and Du, 2026); iterative training moved to open questions; the warm-start and summary sections were dropped.
- [**Open vs closed LLM ecosystem model**](open-vs-closed-llm-ecosystem-model.md) (`Claude-session: 0e13ea82-cce8-4589-9bb0-028ffd5747ed`)

## Sat, Oct 3, 2026

- [**Open vs closed LLM ecosystem model**](open-vs-closed-llm-ecosystem-model.md) (`Claude-session: 0e13ea82-cce8-4589-9bb0-028ffd5747ed`)
  Revised: users are now task mixes on the simplex with per-unit prices, log per-unit value and unbounded stock learning, replacing intensity vectors, fixed prices, bounded abilities and depreciation. New sections record the two-task results and every alternative setup explored. Simulation scripts are in `assets/`.

## Sun, Oct 4, 2026

- [**Open vs closed LLM ecosystem model**](open-vs-closed-llm-ecosystem-model.md) (`Claude-session: 0e13ea82-cce8-4589-9bb0-028ffd5747ed`)
  Questions folded into §1.7 and later sections renumbered. Added three-task results under three user densities, with the script in `assets/`. The "what this says" section now states the thin-tail result geometrically and no longer claims that profit-funded R&D removes the open-takes-all corner.

## Tue, Oct 6, 2026

- economic modeling of LLM risk-management/safety? what do they say about open vs closed ecosystems?

- [x] **Restart llama gateway after service job stopped** (`m2:~/llama`)
  The gateway service job (2433789) had been stopped on 2026-10-02T20:26Z and the userspace Tailscale node's key had expired a day earlier, so `svc:llama` still resolved in MagicDNS while nothing served it; only the GPU engines survived, which made the stack look up.
  Resubmitted the service job (2605661) after `validate` and the test suite, and deleted the dead `llama-gateway` device record so the replacement node re-registers cleanly. The controller adopted the three running engines because their marks matched the current namespace, so no duplicate GPU jobs were submitted.
  The new node registered with key expiry disabled, which the old one lacked, and the four service ports, the worker list, and one completion per model verified the stack end to end.

- [**Open vs closed LLM ecosystem model**](open-vs-closed-llm-ecosystem-model.md) (`Claude-session: 0e13ea82-cce8-4589-9bb0-028ffd5747ed`)
  Learning now slows with overall quality: usage-driven gains are divided by ‖aⱼ‖, for the open model too. The long-run section carries the corrected ratio formula and why the penalty enlarges the open territory. New §2.4 compares exponents; the comparison script is in `assets/`.

## Wed, Oct 7, 2026

- [x] **Restart the Comet gateway service job** (`m2:/mnt/weka/shrd/k2m/yuekai.sun/sglang-serve`)
  The comet-gateway service job (2526343) failed on 2026-10-02 when the workspace ran out of space writing `state/`, taking the SMG gateway and the tailnet leg down while the GPU engine allocations kept serving on their own; `svc:comet` therefore still resolved in MagicDNS while nothing answered it.
  Resubmitted the singleton service as job 2606375 after `validate` passed and a write test confirmed the disk-full condition had cleared. The controller adopted the running engines because their ownership comments matched the instance namespace, and it submitted one replacement kimi-k3 low-prio replica after counting nine live allocations against a target of ten.
  Verified end to end: gateway `/health` and `/v1/models` (kimi-k3, deepseek-v4.1-flash, glm-5.3), eleven healthy registrations, and the documented tailnet checks, with `serve status` showing the TCP 8000 forwarder and `Self.CapMap["service-host"]` carrying `svc:comet`.

- [x] **Prune non-connected devices from the tailnet** (`~/second-brain` @ `02bcec5`)
  The tailnet had accumulated 145 devices that were not connected, mostly per-job Slurm workers created with non-ephemeral auth keys, and they could not be removed from this machine because deleting a device is an admin-API-only operation with no corresponding `tailscale` CLI subcommand.
  Added a script that lists devices through the REST API and deletes the ones that are not currently connected, dry-run by default with `--apply` to act, plus an option to dump full device records to a backup beforehand.
  Selection keys off `connectedToControl` rather than `lastSeen`, since distinct devices can share a hostname and report recent timestamps, and deletions match on device id so a stale record cannot collide with a live device of the same name. Ran it with a backup: 145 deleted, 0 failed, leaving the 6 connected devices, all of which still respond.