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
15 Th : fly to AA
16 F  : faculty meeting; fly to SF
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
- [x] **Add a harness-engineering skill for all harnesses**
  There was no shared guidance on setting up repos for agents, so each harness had to rediscover it. A new skill in `~/.agents/skills/harness-engineering`, symlinked from `~/.claude/skills` and `~/.kimi-code/skills`, condenses OpenAI's harness-engineering principles into a mechanical repo audit and a setup procedure sized to the repo.
- [x] **Create repo from the bullet-journal model note** (`~/llm-marketplace` @ `e89204a`)
  The open-vs-closed LLM model, its simulations and results lived in one journal note with loose asset files, so nothing checked that numbers matched scripts or that references resolved. Now docs, scripts and per-run results sit together under lint and tests.
  - The note is split by top-level section with global § numbers, and the lint checks every reference resolves.
  - Each simulation configuration writes its own result file, a generated summary backs every number in the results section, and a test checks the committed results reproduce.
- [x] **Reconstruct sre-world to Incident Arena parity** (`~/sre-world` @ `9102533`)
  abundant-ai/sre-world went offline, leaving the yuekai/sre-world fork at a Jul 21 snapshot; the original's later work survived only in a public fork, the 20 Incident Arena tasks and its GHCR images. Branch `parity-sep28` rebuilds it from those: all 20 Arena tasks regenerate exactly (up to documented snapshot drift), tests and gates pass, and an AGENTS.md harness makes it workable.
  - `28d44ce`: the public mrshu/sre-world fork's 312 commits through Sep 19 (#488) were checked as the original's (no fork-owner authorship, GitHub-signed merges, Arena answer-key SHAs in history) and fast-forwarded onto main.
  - `bd9f688`: verifier (now verifier/), chart edits, task.toml/test.sh, window-derived profiles, answer keys and RC image pins back-ported from the Arena tasks; `tools/arena_parity.py` is the gate and `tools/arena_backport.py` recovers scenario sources. 35 scenarios on the old report-graded contract were retired (`9acb124`).
  - Images: every digest the Arena tasks pin (24 images, 136 tags) plus Slack v22, Saleor v10 and the Sep 19 lock images were copied with crane to ghcr.io/yuekai/sre-world with identical digests, verified tag by tag, before the original's registry changed further.
  - `9635551`: post-Sep-19 loadgen, sidecar and main code recovered from the published images (newest wins) and Saleor 10-T1 added; rebuilding the Go source with the image's toolchain reproduces the v21 slack-go binaries byte-for-byte. Slack images build again after pinning pnpm and mirroring MinIO (`fcfee30`).
  - `f0cd838`: 186 tests that encoded Sep 19 behaviour were ported to the recovered contract and gates retargeted at shipped tasks; 1938 tests and 17/17 smoke gates pass, with the one unrecoverable verifier profile a strict xfail.
  - `9102533`: AGENTS.md map, docs/plans with tech debt, D25, an arena gate in validate.sh and CI, a doc-link test and a scoped pre-commit hook.
  - Local Kind runs, the private packages and merging into main were handled next; see "Ready sre-world PR #1 and get its CI green".
- [x] **Add tech-debt list and doc link check** (`~/bullet-journal` @ `ec555b5`)
  A harness-engineering audit found known compromises scattered across design.md and commit messages, and nothing catching broken links in the agent-facing docs. Cleanup passes now have one list to work from, and pixi run check fails when a rename or heading change breaks the map.
- [x] **Compare Xian Zhang's E&E scores to Stats 506** (`~/xian-zhang-review`)
  The interim review draft (.md and .docx) discussed Stats 507 enrollment trends, which say little about teaching quality. That sentence is replaced with a comparison against the Stats 506 instructor from the department comparison report: Xian matched or exceeded on every item in FA24, trailed in FA25 (largest gap Q199), with similar mean grades and her class considerably larger.
- [x] **Ready sre-world PR #1 and get its CI green** (`~/sre-world` @ `bdbb9a9`)
  The reconstruction could not be trialled or merged: Slack tasks never came up on local Kind, the agent harness had gaps an audit ranked, and yuekai/sre-world#1's task-ci had never run on this fork. Kind now runs Calico (oracle of Arena task 007 scores 1.0), all seven audit gaps are closed, and five CI fixes get task-ci running end to end; auto-merge waits on task-ci, parity and smoke.
  - Diagnosis: a tech-debt note blamed kindnet for dropping kubelet probes, but a repro showed probes pass; the causes were private GHCR images and kindnet dropping reply packets to pods under Ingress NetworkPolicies (DNS included). The user made the codex-tools and Slack packages public; Frappe and Saleor stay private.
  - `a8484fc`: the trusted Kind environment disables kindnet, uses k3s's pod CIDR and installs a sha256-pinned Calico; the chart and generated tasks are unchanged, so Arena parity holds.
  - `788c6ea`: four audit gaps get checks: a README Arena-number catalog verified by arena_parity, live-doc path checks, evidence tags on tech-debt entries, and ordered D-numbering.
  - `f503378` (separate session): the grader parity test replays only v1 verdicts, so local oracle runs under `jobs/` no longer crash the unit suite.
  - `4fa7200`: `./validate.sh kind` and the kind-netpol workflow check NetworkPolicy enforcement on the trusted cluster; on plain kindnet it fails the two reply checks.
  - `f1762d7`: eight historical docs moved to docs/archive/ with banners; docs/README.md indexes the live ones and a test makes new docs pick a side.
  - CI fixes found by Auto-fix: `0ddaf7b` counts base contracts the head's verifier rejects as affected instead of crashing the impact job; `e8a80a1` keeps the impact job's outputs under GitHub's 1 MB limit; `3707c1d` moves kind-surface to ubuntu-latest and gives its script Calico; `7222d60` pins the episode clock before the kind-surface verifier check; `bdbb9a9` (Oct 8) lets the Kind smoke wait for Calico to converge.
  - The user turned on repo auto-merge and made task-ci, parity and smoke required on main.
- [x] **Trace results by name, check trailer, add CI** (`~/llm-market` @ `cf2f136`)
  §3.7 labelled runs in prose, so most result files could not be found by search, one was cited nowhere, and the H = 0 claim had no run. Now every number names its configuration and the lint enforces it; new H = 0 runs correct the σ = 0 claim. CI and the trailer check do the rest.
  - The new runs showed the one-period game cycles in 39 of 100 periods at σ = 0 once the open model is gone; §3.7 had said it settles. §3.7 and §6 now say so.
  - Remote: github.com/UMich-FATML/llm-marketplace (private); CI runs `pixi run check` and passed on the first push.
- [x] **Collect schemas and stats for all 108 databases** (`~/genebench-max` @ `7c24c84`)
  GeneBench-Pro-style task generation needs every table's columns, join keys, units, missing-value meaning and data artifacts, but the skills repo's 108 databases had only endpoint docs. A new repo now holds per-database schemas, stats from up to 370 sampled rows per table, and a cross-database identifier crosswalk, each regenerable by a collector script.
  - Coverage, sampling designs, gaps and open questions: [genebench-max.md](genebench-max.md)
- [x] **Make the repo legible and self-checking for agents** (`~/genebench-max` @ `ce009f0`)
  Knowledge lived in a 91-line AGENTS.md manual, chat and a journal note, and only some rules were checked, manually. AGENTS.md is now a map into docs/ (design, collecting, tech debt, plans). `pixi run check` (validate, stale-output check, tests) runs from a pre-commit hook. ID names and leaked emails are now validator errors.

## Thu, Oct 8, 2026

- [x] **Rename ~/scientific-db-schemas to ~/genebench-max** (`~/genebench-max` @ `c56e9d4`)
  The repo's name now matches its purpose, GeneBench-Pro-style task generation. Pixi's env hardcoded the old path, so it was rebuilt; `pixi run check` passes. The pixi project name, AGENTS.md heading and API caller IDs now say genebench-max too.
  - The journal note is now [genebench-max.md](genebench-max.md); the repo's original plan doc keeps the old path as history.
- [x] **Hold compute cost constant in the LLM market** (`~/llm-marketplace`)
  The model had compute getting cheaper at rate g, which kept closed firms training forever; the user asked to simplify to a constant cost. Spec, script and all results now use cₜ = c₀; §2.2 becomes a cheap-compute benchmark and §2.3 says closed firms stall while the budgeted open model keeps growing.
  - Uncommitted: §3.7 is on hold. The solver pins each plan's last-period training fraction at 1; optimizing it flips the baseline from the open model squeezed out to the open model taking every user (recorded in §6). The user decides which solver to use.
- [x] **Sample rows for every catalogued table** (`~/genebench-max` @ `5eec4d9`)
  Collectors sampled at most ~20 core tables per database, leaving 974 tables schema-only. The cap is gone: 777 of them now have samples, and the rest carry a specific reason. Re-runs reuse cached samples, and the call budget is now per table, since flat ~300 can't cover SDSS.
  - MouseMine's 150 tables are still blocked by HTTP 429; 47 others are empty or need access (e.g. GI_API_KEY).
- [x] **Stop parsing bare times of day as dates** (`~/genebench-max` @ `d665091`)
  collect_stats sent strings like "14:30:00" or "20:00:00+00:00" to pandas, which anchors them to today, so date_range changed on every rerun. Time-only values are now excluded from datetime parsing; such columns become categorical.
  - Regenerated 8 affected stats files (usgs, alphavantage, cod, imaging-data-commons, sdss, treasury, usfiscaldata); on branch claude/inspiring-margulis-47b6df, not merged.
- [x] **Catalogue KEGG and openFDA's remaining endpoints** (`~/genebench-max` @ `2736df4`)
  Both databases named endpoints in a gap but never catalogued them, so tasks couldn't stage them. KEGG gains 10 tables and openFDA 24 (every endpoint its download index lists), all sampled, with contact details dropped from rows.
- [x] **Sample 370 rows per table unless it has fewer** (`~/genebench-max` @ `b25ae4e`)
  Collectors capped calls at ~10 per table, so APIs returning 10 rows per call gave 10-120-row samples. The row count now wins: 794 short tables were re-sampled, and validate fails any sample under 370 rows without a stated reason, so the rule can't silently slip again.
  - 18 tables stay short with reasons; Alpha Vantage and NASA need re-runs once their daily quotas reset.
- [x] **Merge bare-time date fix and regenerate stats** (`~/genebench-max` @ `573cd37`)
  The fix landed on a branch whose regenerated stats predated today's re-sampling, so those conflicted. Kept the current samples and regenerated every database's stats with the fixed script; 21 files changed, and four collectors re-ran from cache to refresh column kinds.
- [x] **Read keys from the repo's .env; finish NASA NeoWs** (`~/genebench-max` @ `a118976`)
  Keys moved from ~/.env to a git-ignored .env in the repo, which neither the collectors nor the credential scan read. Both now load it first. NASA's collector capped calls even with a real key; with NASA_API_KEY, neo and close_approach now reach 370 rows.
- [x] **Sample Census data and GI async-job tables** (`~/genebench-max` @ `f89afe7`)
  With CENSUS_API_KEY and GI_API_KEY set, 20 tables that had no rows now have 370. The Census collector never sent its key, so county-level sampling was added; GI now submits its own async jobs to sample their lifecycle. GI's variant tables still need a VCF in S3.
- [x] **Let Alpha Vantage searches span several days** (`~/genebench-max` @ `188e3b9`)
  The 25-call daily quota can't reach 370 search matches in one run, and a run that hit the quota replaced earlier rows with none. Searches now cache per keyword and resume, and a short series is re-fetched but kept if the call fails.
  - Scheduled tasks alphavantage-recollect-day1/-day2 run the re-collection at 10:30 PDT on Oct 9 and Oct 10; the quota looks like a rolling 24 h window, not a UTC-midnight reset.
- [x] **Sample all 164 MouseMine classes** (`~/genebench-max` @ `bdcd150`)
  MouseMine's query endpoint returned HTTP 429, so no class had rows, and the collector still capped core classes at 100 rows. The service answers again: classes are now drawn by random object IDs, avoiding slow deep offsets, and every non-empty class has 370 rows or all of its objects.
  - Found that lib.random_offsets draws overlapping pages; 107 cached samples have repeated rows. Suggested as a separate task, not fixed yet.
- [x] **Sample each record once and flag duplicate rows** (`~/genebench-max` @ `6a251cb`)
  Random page starts weren't spaced, and some APIs repeat records or ignore offsets, so 107 samples held repeats. Pages now never overlap, draws are deduped and topped up, stats count repeats, and validate fails keyed tables with repeated rows.
  - On branch claude/lucid-leavitt-727843, not yet merged to main; the main checkout's cache/ already holds the re-sampled rows.
  - Not the offset bug: BioGRID ignores start above ~510k (now sampled by random ID); gnomAD answered batches of 19 or more variants with another query's cached response; BRENDA and GTEx repeat records in responses.
  - About 50 wrong primary-key declarations fixed. DisGeNET, OMIM and Data Commons samples were topped up, not redrawn, to save quota.

## Fri, Oct 9, 2026

- [x] **Move schema collection into data/** (`~/genebench-max` @ `9980d13`)
  Collectors, scripts and their outputs filled the repo's top level, leaving no room for the modeling and task-generation work built on them. They now live in data/; docs, tests, vendor/ and .env stay at the root since they serve the whole repo.
- [x] **Revert to slowly falling compute cost** (`~/llm-marketplace`)
  The Oct 8 simplification to constant compute (g = 0) was uncommitted. Under it closed firms stop training at a point set by the transient, so the long run has no closed form. The model is back to the committed cₜ = c₀·e^{−g·t} with g = 0.03, where every developer eventually trains on all it can access and the §2.2 fixed point is the long run.
  - The constant-compute work is kept in the git stash "constant-compute WIP (Oct 8), reverted Oct 9"; its plan is marked Abandoned.
  - Kept its finding as a §6 issue: the solver pins each plan's last-period training at 1, which biases firms toward training.
  - Rebuilt the stale pixi env (built under the old ~/llm-market path) so pytest runs. Uncommitted.
- [x] **Keep falling compute as a variant of g = 0** (`~/llm-marketplace` @ `6a30bf2`)
  The revert above misread the request: the user wants falling compute alongside the constant-compute baseline, not instead of it. The Oct 8 work is restored from the stash, and g is back in the cost with baseline 0 and a `g-falling` configuration at 0.03, which reproduces the Oct 7 baseline. The spec covers both cases.
  - Existing result files only gained g = 0 in their configs, so no rerun was needed beyond g-falling.
  - §3.7 is still mostly Oct 7 numbers, pending the user's choice of solver fix; a note there says which rows are current.