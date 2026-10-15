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
- [x] **Merge the duplicate-rows fix into main** (`~/genebench-max` @ `075f0c0`)
  The duplicate-rows fix (6a251cb) was cut before the data/ move, so it couldn't fast-forward main. Merged main into it, kept the new data/ paths in the docs and validator messages, and fast-forwarded main; pixi run check passes in the main checkout.
- [x] **Start a Kimi-K3 engine on the main partition** (`m2:/mnt/weka/shrd/k2m/yuekai.sun/sglang-serve`)
  The kimi-main pool target was 0, so nothing served K3 on the high-priority path while all ten kimi-lowprio K3 allocations sat pending. Raising the target to 1 had the running controller submit one 2x8-H200 allocation (2626508) on its next reconcile cycle; the engine loaded, registered healthy, and answered a completion through the gateway.
  - Left uncommitted by request: the target stays local, together with the file's other uncommitted pool reductions (gemma4/mova/qwen36/k26 to 0, glm53 2 to 1).
- [x] **Scale the main Kimi-K3 pool to eight engines** (`m2:/mnt/weka/shrd/k2m/yuekai.sun/sglang-serve`)
  One main-partition K3 allocation left no high-priority spare, so losing it to preemption would drop K3 off the main path while the low-priority pool stayed pending. Raising the kimi-main target from 1 to 8 let the running controller fill the pool itself, with no service restart.
  - The controller submits at most one allocation per pool per 300 s cooldown, so the seven new engines arrived over half an hour (17:34-18:04) and each then needed about 19 minutes to load shards; the last of eight was serving at 18:33.
  - Verified: all eight records ready and attached to the gateway (17 workers total, the rest being kimi-lowprio, glm-5.3 and deepseek-v4.1-flash), and a completion through the gateway returned the expected text.
  - Left uncommitted, consistent with the previous turn's choice; the engine key, jobs list, and node names stay out of the journal.
- [x] **Resume Alpha Vantage symbol searches** (`~/genebench-max` @ `78e1202`)
  economic_cpi sampled only 364 rows after an old chunking bug, and symbol_search was empty because the 25-call daily budget ran out. This run re-fetches CPI (370 rows) and searches 24 of 56 keywords (211 matches); the next daily run continues the searches.
- [x] **Add reasoning efforts to the llama provider models** (`~/.dsh`)
  The glm and kimi models on the llama route offered no reasoning levels in the picker, and deepseek-v4.1-flash's had been silently erased. The Models settings page rebuilds each model entry from only the fields it shows, so any save there drops reasoningEfforts. All three now declare their documented tiers in cordis.patch.yml, with a comment marking that file as the field's only editor.
  - Probed the live gateway rather than trusting the docs: all three honor top-level reasoning_effort, including GLM, whose docs prescribe chat_template_kwargs. This lets all three share one plain dispatch with no compat override.
  - GLM and Kimi deliberately omit xhigh, since their documented tiers stop at max and undeclared levels resolve as unsupported.
- [x] **Add live defender arena to apache-camel task** (`~/cyber-arena`)
  The apache-camel offensive task had no defensive role, so two-agent red-vs-blue play was impossible on it. It now ships an arena overlay: an instruction-defender.md blue-team brief, a defender container with per-instance root SSH on the target, a supervisor-mode boot (the app restarts on kill without re-minting the flag/token), a staged no-shell patched jar as the decisive defense, and a deterministic checker that conjunctively scores availability sampling, per-tick flag-capture watching, and an integrity gate.
  - The gate compares flag/helper/jar/routes/process state against baselines the target commits to /truth before sshd starts, so "defense" by deleting or rotating the flag, rewriting ground truth, blackholing the attacker, or running an impostor service scores 0 — as does leaving the service dead; capture-then-delete cannot hide because the attacker's flag file is hashed every tick.
  - Fix selection was grounded in the collinear defensive-audit packs: their flat-numeric reward artifacts, behavior-only probes, infra-void semantics, and brief style were adopted, while the LLM-judge channel was excluded (the live defender's outcomes are fully observable programmatically, so there is no probe-enumeration gap for a judge to close).
  - Verified end to end: solo grading unchanged (golden captures vs vuln, fails vs PATCHED=1, full xchg verifier flow rewards 1.0); defender golden scores 1 alone; the simultaneous race goes to the attacker first (~15 s; documented in the arena README); staged "stupid defender" violations each fail the named gate check; 23 checker unit tests pass.
- [x] **Publish cyber-arena to the LLM360 org remote** (`~/cyber-arena` @ `3c41924`)
  The workspace had an unborn branch with no commits. Made the initial import commit (collinear packs + rollout data; sre-world excluded as a symlink to its own repo, .DS_Store ignored; secret scan found only shipped test certs), added origin, and pushed main to github.com/LLM360/cyber-arena.git.

## Sat, Oct 10, 2026

- [x] **Reduce the main Kimi-K3 pool to two replicas** (`m2:/mnt/weka/shrd/k2m/yuekai.sun/sglang-serve` @ `099e158`)
  The main K3 pool had been scaled to eight 2x8-H200 allocations, more main-partition capacity than serving needs. The target is now 2, so the running controller cancelled the six excess allocations on its next reconcile cycle, with no service restart.
  - Scale-down cancels the newest running allocations first, so the two oldest engines survived and kept serving; the gateway lists two kimi-k3 workers, verified against the ready records.
  - Only this hunk was committed; the file's other uncommitted pool reductions were left as they are.
- [x] **Add chain oracle + LLM judge to camel arena** (`~/cyber-arena` @ `bb36422`)
  The apache-camel arena graded defense purely on outcomes (liveness + no capture + integrity gate), so an idle defender still scored 1 while the SSTI→token→command-injection chain sat wide open, and no channel reviewed the defender's conduct. The checker now replays the reference exploit chain against the end-state app as a scored chain_closed conjunct (token re-steal so live rotation can't false-fail, an RCE canary the patched jar's argv echo can't fake, and a randomized second pass to deter harden-then-reopen), and an agentic judge grades the redacted defender transcript against a 15-item rubric mirroring the defensive-audit packs' doctrine (infra death or malformed output voids only the judge channel with programmatic fallback, or the whole trial under JUDGE_MODE=required). Ships a mock OpenAI endpoint for zero-cost judge-path e2e plus replay.py for offline rubric iteration; 64 unit tests and four calibration games pass, and the solo task's chain and grading are untouched.
- [x] **Value plans past the window with a simulated tail** (`~/llm-marketplace` @ `0964034`)
  The receding-horizon solver pinned each plan's last training fraction at 1 and valued nothing past t + H, which biased firms toward training and valued stocks over at most H periods. Plans are now scored over 30 extra periods repeating their last actions, every fraction is chosen, and the suite runs in parallel.
  - Rerun headline: both closed firms price at 0 to grab data and the open model is gone by period 4 at every H and K; open weights no longer saves it. At c0 = 0.08 the open model stalls closed firms out and climbs to 0.89.
  - The tail makes the closed firms' plan game cycle (18 to 80 of 100 periods) after the open model is gone; per the user, cycles are reported, not smoothed.

## Sun, Oct 11, 2026

- [x] **Add two more main Kimi-K3 engines** (`m2:/mnt/weka/shrd/k2m/yuekai.sun/sglang-serve` @ `62b90df`)
  The main K3 pool served two 2x8-H200 allocations; raising kimi-main to four had the running controller submit the two new allocations five minutes apart, the 300 s submit cooldown, with no service restart.
  - Both are still queued on QOSGrpNodeLimit: the k2m QOS group sits about 100 nodes over its 226-node allowance cluster-wide, so they start only as that usage drops, then need about 19 minutes to load shards. The two running engines keep serving meanwhile.
  - Only this hunk was committed; the file's other uncommitted pool reductions were left as they are.

- [x] **Align llama provider model configs across dsh hosts**
  The local dsh (desktop profile) and m2 dsh (web profile) had drifted: local lacked glm-5.3's developer-role compat flag and carried stale limits, m2 under-declared flash's image input, and kimi-k3/glm-5.3 had no explicit limits at all on m2. Both llama model blocks are now byte-identical apart from baseURL - flash at 1048576/393216 keeping image input with xhigh dropped, kimi-k3 at 262144/32768 and glm-5.3 at 1048576/131072 text-only, each with low/high/max and glm carrying supportsDeveloperRole false.
  - Probes against the live gateway showed the compat flag is required: GLM silently drops a `developer` message (HTTP 200, prompt_tokens 45 -> 19, instruction lost) while flash and kimi handle it correctly, and glm rejects images with a 400 "Model only supports text input", confirming text-only is right.
  - m2's GLM comment claimed every effort maps to max; measured reasoning tokens contradict it (absent 65, low ~10, high ~33, max ~67), and the endpoint's wire grammar accepts 'none' but rejects 'off' with a 422. Since the harness sends nothing for a null `off:`, offering `off` for kimi would falsely promise no thinking, which is why neither kimi nor glm lists it.
  - Reasoning defaults were left unset per the user, so flash (0 reasoning tokens with no effort sent) still does not think by default; kimi and glm do. A route-level `reasoning` would fix flash but also changes glm, as per-model default effort is not expressible in the profile.
  - Both files were validated through dsh's own loader with --patch --dump-config, and the pre-edit files are kept as .20261011-align.bak. The local change needs an app restart, since the desktop profile has no patchReload: live.

- [x] **Mirror m2's web profile patch into headless**
  m2's headless profile patch was an empty list, so a headless run there had no llama models and no default model. It now carries a verbatim copy of the web profile's cordis.patch.yml, so both profiles on m2 resolve the same three models and the same default.
  - Patch entries turn out to be id-targeted overrides rather than inserts: an entry whose id is absent from the tree is reported "entry X not found" and skipped. llm-pi-ai and agent-default-model both exist in the headless tree so the mirror takes effect, while ui-settings-general does not - it is a client UI plugin belonging to the web bundle - so that one is inert in headless and emits a startup warning.
  - Verified by md5 that the headless file is byte-identical to the web file, and that those exact bytes compose against a headless profile (--patch --dump-config exits 0 with only the not-found warning). The previous empty patch is kept as .20261011-align.bak.

- [x] **Mirror desktop dsh patch into web and headless**
  Desktop's profile patch held the aligned llama config plus its client-UI entries, while web and headless still ran the old single-model llama block and had never seen kimi-k3 or glm-5.3. Web and headless now share desktop's entry set with each target's unique entries appended rather than dropped, because a verbatim copy would have removed web's ui-settings-general and llm-deepseek and headless's llm-deepseek and its permission pin of defaultPreset danger-full-access.
  - Patch entries are id-targeted overrides, so the shared ids (llm-pi-ai, agent-default-model) take desktop's values; that also moved both targets' baseURL from llama.taildd337d to llama-gateway.taildd337d, which serves the same backend.
  - Headless has no ui-chat, ui-settings, ui-settings-account or agent-preset-registry in its tree, so those four mirrored entries are inert and log "not found" warnings on every start; dropping them from the headless file is a one-line follow-up.
  - Verified with --dump-config that both profiles compose cleanly and resolve three llama models with the new limits, and that headless still pins danger-full-access while web keeps ui-settings-general and llm-deepseek. Previous files kept as .20261011-mirror.bak.

- [x] **Point local dsh profiles at llama.taildd337d**
  Mirroring desktop's entries into web and headless had also carried over desktop's llama-gateway baseURL, an incidental side effect of the shared llm-pi-ai id rather than a deliberate choice. Both hostnames front the same backend, so all three local profiles now name llama.taildd337d.ts.net, which is what web and headless used before and removes an unexplained discrepancy between profiles.
  - Verified both hostnames resolve to distinct Tailscale IPs yet return identical model lists and identical developer-role behavior, so the choice is cosmetic; standardizing keeps the profiles diffable against each other.
  - m2's profiles deliberately keep baseURL 127.0.0.1:8000: m2 sits off the tailnet with no DNS for the tailscale names, so it reaches a node-local gateway instead.
  - The gateway now also serves mimo-v2.6-pro, which no profile configures yet; adding it is a separate decision.

- [x] **Restore web and headless patches, mirror only the llama models**
  Mirroring desktop's whole entry set into web and headless had dragged in its client-UI entries and dropped each target's own settings. Both files are now restored from .20261011-mirror.bak, so web keeps ui-settings-general and llm-deepseek and headless keeps llm-deepseek and its permission pin of defaultPreset danger-full-access, with only the models list under the llama provider copied across.
  - The three profiles' models blocks are byte-identical (41 lines, confirmed by diff and sha), covering flash, kimi-k3 and glm-5.3 with the shared limits and glm's developer-role compat flag, while each target keeps its own displayName and baseURL fields.
  - Comments that document a single model entry travelled with that entry, but desktop's provider-level CAUTION note about the Models settings page was left out, since the instruction was to mirror model config rather than provider commentary.
  - Both profiles compose cleanly with no warnings, unlike the merged version, which had logged four not-found entries for headless.

- [x] **Restore m2's headless patch, keep only the llama models**
  Mirroring m2's web patch into headless had copied the whole entry set into a profile that had none, so headless also acquired the glm-5.3 default model and a client-UI entry that only web can mount. Headless is restored from .20261011-align.bak, an empty list, and now carries only an llm-pi-ai entry configuring the llama provider's models, byte-identical to the other profiles'.
  - The provider's transport fields (api, baseURL 127.0.0.1:8000, apiKeyEnv) came along because a models list means nothing without the route it belongs to; agent-default-model and ui-settings-general were deliberately not mirrored.
  - Consequence worth knowing: with no agent-default-model override, m2's headless falls back to the bundle default of deepseek-official/deepseek-flash, so the llama models are selectable there but not the default.
  - The pre-restore mirrored state is kept as cordis.patch.yml.20261011-mirrored.bak beside the align backup, and the file composes against a headless tree with no warnings.

- [x] **Default m2's headless runs to llama**
  Headless carried no agent-default-model override, so it fell back to the bundle default of deepseek-official/deepseek-flash and the freshly configured llama models were merely selectable. An agent-default-model entry pinning provider llama and model deepseek-v4.1-flash now sits alongside the model config, so fresh headless agents start on flash.
  - reasoningEffort was left out, since the field is optional and the standing decision was to leave reasoning defaults unset; the practical effect is that flash will not think unless a level is chosen, as it reports no reasoning tokens when no effort is sent, whereas local headless pins high.
  - Verified with --dump-config against a headless tree: the profile composes with no warnings, the default resolves to llama/deepseek-v4.1-flash, and all three llama models stay available. The pre-edit state is kept as .20261011-modelonly.bak.

- [x] **Pin reasoningEffort high for m2's headless default**
  The headless default-model entry added a moment earlier omitted reasoningEffort, which would have left flash not thinking, since it reports no reasoning tokens when no effort is sent, unlike the local profiles that pin high. The entry now reads provider llama, model deepseek-v4.1-flash, reasoningEffort high, so headless runs reason by default.
  - This reverses the earlier leave-reasoning-unset choice for this one default-selection field only, not for the route-level setting, which would also have moved glm-5.3 off its own default.
  - Verified with --dump-config against a headless tree: the profile composes with no warnings and resolves the pinned effort.

## Mon, Oct 12, 2026

- [x] **Serve MiMo-V2.6-Pro as a fourth engine pool** (`~/llama` @ `e40c096`)
  The fleet served only Kimi K3, DeepSeek V4.1 Flash, and GLM-5.3. The recipe is the cookbook H200 Pro cell (marlin MoE) with llama standard metrics, cache-report, and HiCache flags, admission capped at 64, and an audio_tokenizer mount the eager AudioTokenizer load needs.
  - Weights were already mirrored complete at /mnt/weka/shrd/k2pta/models/MiMo-V2.6-Pro-RL (130/130 shards), so nothing was downloaded. The running controller submitted job 2646025 on fs-mbz-gpu-637 within a minute; it reached ready in 47 minutes (tp8, marlin MoE, fa3 attention auto-selected, hicache host pool 2.46M tokens).
  - Gateway validation passed: /v1/models lists mimo-v2.6-pro, a thinking completion split reasoning_content (25 reasoning tokens), an identical repeat prompt reported cached_tokens 21/22, and a weather tool request returned parsed tool_calls with finish_reason tool_calls.
  - The image is pinned to lmsysorg/sglang:v0.5.21, the stable release containing the cookbook cell, rather than the cookbook's moving dev tag, so 28-day replacement allocations stay reproducible.

## Tue, Oct 13, 2026

- [x] **Mirror harness-engineering skill to m2**
  The skill existed only on the laptop, so the agents running on m2 could not consult it. On m2 it now lives at `~/.agents/skills/harness-engineering`, the shared user-level root that Codex and DSH both scan, with `~/.claude/skills/harness-engineering` symlinked to it for Claude Code.
  - The canonical copy stays on the laptop and m2 holds the mirror, because the skill is authored locally; re-syncing is one rsync of the skill directory, so the link layout never has to be revisited.
  - Only one link was needed: DSH's installed skill provider already scans `$HOME/.agents/skills` alongside `$DSH_HOME/skills`, which is also why the hf-cli and tailscale skills sit there, and Codex's roots are `~/.codex/skills` plus `~/.agents/skills`.
  - Verified by enumerating skills in each harness rather than by eye: Codex's rendered prompt input lists harness-engineering from the `~/.agents/skills` root, and a headless Claude Code run lists it among its skills. The DSH there runs under the llama service, so instead of starting a second server its installed provider's roots were checked, and that service sets no DSH_AGENTS_HOME override.
- [x] **Install dsh globally on m2**
  The only dsh on m2 was the project install at `~/llama/vendor/dsh`, pinned to 0.1.7-rc.2 by its own lockfile and off PATH, so it was reachable only by absolute path and with a node borrowed from pixi or nvm. A user-level global install now puts 0.2.0-rc.2 under the nvm v26.4.0 prefix, so `dsh` resolves on PATH in login shells.
  - The latest version was chosen over the one the vendor copy pins, at the user's instruction. The vendor copy stays because llama's service hardcodes it, so the two now differ and share `~/.dsh`: state written by the 0.2 CLI can change what the 0.1.7-rc.2 service reads.
  - npm 11 blocked five install scripts. Rather than allow them, each was checked: node-pty ships no spawn-helper on linux-x64, and node-pty and koffi both load, so nothing is missing. The CLI reports 0.2.0-rc.2 and resolves profiles.
  - An earlier attempt was interrupted mid-install and left a partial 0.1.7-rc.2 global tree with no bin link; it was removed before the latest install.
  - Non-interactive ssh still sees no dsh, because nvm is loaded only by the shell rc files. Scripts and agents must keep using an absolute path.
- [x] **Update llama's vendored dsh to 0.2.0-rc.2** (`~/llama`)
  The vendored install pinned 0.1.7-rc.2, and the plugin bundles that `~/.dsh/profiles/node_modules` symlinks to come from that same tree, so the CLI and the profile bundles it boots could only move together. The lockfile now resolves 0.2.0-rc.2 and holds no 0.1.7-rc.2 reference, which also matches the global install from earlier today, so both CLIs boot the same bundles.
  - Verified by booting the web app with the service's exact argv and env on a scratch port against the real `DSH_HOME`: the custom `cordis.patch.yml` still composes, the UI serves (303 with its token, 401 without), and the one-line banner that `record_dsh_url` regexes is unchanged, so the gate keeps publishing the URL. The test process was killed afterwards.
  - `vendor/` is gitignored, so this leaves no repo diff and `llama validate` still passes. The profile, token and settings files were copied to `~/.dsh/backup-pre-0.2.0-rc.2-20261014T053527` first, so the update can be rolled back.
  - npm 11 again blocked five install scripts, the same set checked during the global install: node-pty ships no spawn-helper on linux-x64 and both node-pty and koffi load, so nothing is missing.

## Wed, Oct 14, 2026

- [x] **Adapt vendored static checks to science-tasks** (`/mnt/weka/shrd/k2m/yuekai.sun/science-tasks`)
  The static checks vendored from tb-science assumed human authors, upstream's canary and names, Modal GPUs, a proposal step and GitHub runners, and most fixtures failed several checks besides their target. The checks now enforce this repo's format: its own canary, `science-tasks/` names, agent-author metadata with sources, a taxonomy file, one task per PR, CPU-only tasks, an EC2 box budget and required hints. Every FAIL or WARN line says how to fix it and names the doc section that owns the rule.
  - A single `ci_checks/checks.txt` lists the per-task checks, which the coordinator's runner reads. Every fixture was upgraded, so each `fail-static-*` fixture fails only its target and every other fixture passes; 95 pytest cases hold this in place.
  - Also added `docs/authoring/task-format.md`, a `templates/task` scaffold with `scripts/new-task.sh`, and a `check-no-todo.sh` that fails on placeholders the scaffold leaves behind. Uncommitted, at the coordinator's request.
- [x] **Grant read access to comet-gateway.json**
  The SGLang serving state file at /mnt/weka/shrd/k2m/yuekai.sun/sglang-serve/state/ was mode 0600, so k2m members such as hao.wang could not read the Comet gateway config even though every directory on the path is group-traversable. It is now mode 0644, readable by all, at the file owner's request.
  - Effective access is the k2m group rather than the whole cluster, because the root-owned /mnt/weka/shrd/k2m directory is mode 2770 and blocks traversal by non-members; changing that would need an admin.
- [x] **Swap deepseek capacity for three glm engines** (`/mnt/weka/shrd/k2m/yuekai.sun/sglang-serve` @ `1d74474`)
  The comet fleet ran one deepseek-v4.1-flash and one glm-5.3 engine. Zeroing deepseek-main frees its 8xH200 node and drops the model from the gateway; raising glm53-main to four has the controller submit three additional single-node engines, one per 300 s cooldown, with no service restart.
  - The deepseek job was cancelled within one reconcile cycle and the gateway stopped advertising the model immediately; all three new engines booted, registered healthy, and passed a gateway generation smoke test, with one landing on the node the deepseek stop freed.
  - The three main-partition nodes pushed the QOS group over its node limit, so Slurm preempted four of the ten kimi-lowprio engines at 04:42 and requeued them; they pend on priority and the pool self-heals when group capacity frees, but lowprio ran six engines until then.
- [x] **Tag calibration re-runs; clarify reviewer errors** (`/mnt/weka/shrd/k2m/yuekai.sun/science-tasks` @ `11668d8`)
  Calibration always reused a model's earlier S3 records, so re-measuring after comet capacity changed meant re-reading stale timeouts; `--run` tags a fresh measurement. A reviewer that crashed told the author to fix "items", though nothing was theirs to fix.
  - glm-5.3 re-run on four glm engines (tag r2): 37/37 planted defects caught, agent time median 271 s and max 489 s, vs 20/37 with all 17 misses being 1800 s timeouts on the single overloaded engine.
- [x] **Start each box run from an empty output dir** (`/mnt/weka/shrd/k2m/yuekai.sun/science-tasks` @ `77eb994`)
  A re-run on the same PR sha synced its record into the dir holding the earlier run's jobs, and readers took the oldest: /reviewers on PR 2 reported the old timeout though the new review finished. Error reviews now also show their cause.
- [x] **Post required checks on the PR head explicitly** (`/mnt/weka/shrd/k2m/yuekai.sun/science-tasks` @ `1028ced`)
  execution-checks and merge-gate came only from the first pull_request_target run's jobs: a /pipeline re-run attached them to main's commit and slash commands made none, so a PR whose first run failed could never merge. pipeline.py now posts both itself.
  - Verified by reopening smoke PR 2: the new run posted green execution-checks over the cancelled one, and merge-gate failed on the two request-changes reviews as intended; PR 2 closed unmerged.
- [x] **Switch glm-5.3 recipe to fp8 KV cache** (`/mnt/weka/shrd/k2m/yuekai.sun/sglang-serve` @ `0be5733`)
  Hopper DSA defaulted GLM-5.3 to bf16 KV. Per the cookbook config tips, fp8_e4m3 KV with flashmla_sparse_q8 prefill (native FP8, no dequant round-trip) and flashmla_kv decode halves per-token KV bytes: more tokens at the same 0.8 mem fraction.
  - All four glm53-main engines rolled one at a time via the raise-target/cancel-older runbook; each boot logged the fp8 backends with 338,496 KV tokens per rank (was 207,744 bf16), zero errors, healthy EAGLE accept length ~3.0, and correct gateway smoke-test answers with reasoning parsing intact.
- [x] **Run author agents with a scoped fine-grained PAT** (`/mnt/weka/shrd/k2m/yuekai.sun/science-tasks` @ `e030796`)
  Agents pushed with the owner's full gh login, so they could change workflows or settings. A repo-only PAT without Workflows/Admin now makes GitHub reject that. It can't read check runs, so agents poll sticky comments; it still acts as the owner.
  - Open as PR #15, unmerged; verified gh and git authenticate via the PAT with an empty GH_CONFIG_DIR, not yet run end to end with a dsh author.
- [x] **Add rubric-eval and fix judges on large tasks** (`/mnt/weka/shrd/k2m/yuekai.sun/science-tasks` @ `b4b9350`)
  Judge assignments rested on recall alone. rubric-eval now runs the real check on boxes over the 37 planted-defect fixtures and the 71 merged terminal-bench-science tasks, which adds a precision measure. Large tasks failed because the instruction overflowed argv, and judges timed out because `-k 2` ran two of them. The instruction is now uploaded as a file, and each judge runs one rollout with a 60-min timeout.
  - r2 (PR #16): glm-5.3 caught 37/37 fixtures, with false fails on 15 of 69 tb-science tasks and 2 timeouts; kimi-k3 caught 35/37, with false fails on 19 of 71 tasks; glm-5.3 stays the check judge.
- [x] **Install Keenable WebQL MCP server for DSH**
  The keenable-webql MCP server was configured in Claude Code only, so DSH agents could not use its web-search and report tools. Added it as a dsh-mcp-client streamable-http entry in DSH's home-level user patch layer (~/.dsh/cordis.patch.yml), which the hmr plugin applies live to every profile — the same scope semantics as claude mcp add -s user.
  - Verified end to end without an app restart: a fresh subagent sees mcp__keenable-webql__select plus the two html-report tools and the shared MCP resource tools.
- [x] **Label task PRs new task or task fix** (`/mnt/weka/shrd/k2m/yuekai.sun/science-tasks` @ `43b2f83`)
  Task proposals were only findable by the "New task:" title convention, which nothing enforces. A label job in static-checks now tags every task PR, drafts included, from the file list, reusing the labels expected-settings already defines.
  - Merged as PR #18 via maintainer-merge (enforce_admins restored); classification dry-run against PR #2 gave `new task`; not yet run in Actions on a task PR, and the `task fix` path is untested because main has no tasks yet.
- [x] **Add glm-5.3 himem canary at mem-fraction 0.85** (`/mnt/weka/shrd/k2m/yuekai.sun/sglang-serve` @ `70d9501`)
  The cookbook says tune mem-fraction up from 0.8 on H200. A glm53-himem pool runs one engine at 0.85 while glm53-main keeps three at 0.8 as controls, so no controller resubmit can silently shift the experiment.
  - It boots clean: KV tokens 338,496 → 457,536 per engine (+35%), 20.7 GB still free after the pool, no OOM at cuda-graph capture or warmup, and a direct smoke test answers correctly with reasoning parsing intact.
  - The k2m QOS group is at its node limit (QOSGrpNodeLimit), so the canary could not add a 5th node; it replaced the newest 0.8 engine instead, dipping glm capacity to 3 workers for the ~22-minute boot.
- [x] **Raise glm-5.3 himem canary to mem-fraction 0.9** (`/mnt/weka/shrd/k2m/yuekai.sun/sglang-serve` @ `b2becd3`)
  The 0.85 canary booted clean, so the same pool now tests the next step toward a fleet default raise. The 0.85 engine was cancelled and the controller's replacement picked up the edited recipe, keeping glm capacity at 3 workers only for the ~19-minute boot.
  - It boots: KV pool 33.0 GiB / 576,512 tokens per rank (+70% over the 0.8 fleet default, +26% over 0.85), 13.4 GB free after the pool, 4.2 GB still free after graph capture and DeepGEMM warmup, no OOM.
  - Serving verified directly (EAGLE accept length 3.1-3.5 on cuda graphs) and through the gateway (exact-reply smoke test); the gateway lists the canary healthy and ready.
- [x] **Stress glm-5.3 himem canary with primality checks** (`/mnt/weka/shrd/k2m/yuekai.sun/sglang-serve`)
  Long primality reasonings (random 10-digit numbers, ground truth via local Miller-Rabin) made GLM-5.3 burn every token given: one 32k-token request at 300-380 tok/s, then 15 concurrent 16k-token requests against the 0.9 canary.
  - Peak KV token usage 36% of the 576k pool, aggregate 1.4-1.7k tok/s, EAGLE accept length 4.1-4.7, queue empty, no retraction, no OOM; engine and gateway stayed healthy and returned to idle.
  - No request concluded: 10-digit primality exceeds what the model settles within 16-32k reasoning tokens, so all hit the length limit without a verdict — load fully exercised, accuracy untested.
- [x] **Reject glm-5.3 mem-fraction 0.9 after runtime OOM** (`/mnt/weka/shrd/k2m/yuekai.sun/sglang-serve` @ `558470c`)
  Asked whether 0.9 was safe to roll fleet-wide, I probed past the 15-way stress with a 40-request burst; it found the ceiling. At ~30 running requests the DSA indexer decode workspace (dsa_indexer _get_topk_ragged -> deep_gemm fp8_mqa_logits) asked for 626 MiB with 250 MiB free on 6 of 8 ranks; the engine died and dropped 29 in-flight requests, and comet auto-submitted a replacement.
  - 0.9's 4.2 GB post-boot headroom cannot cover the 48-request EAGLE cap because that workspace scales with batch x draft positions. Reverted the himem recipe to 0.85 (~11 GB headroom, ~2x the demonstrated need) and cancelled the pending 0.9 replacement before it booted. Fleet answer: 0.9 no; 0.85 is the ceiling to roll.
- [x] **Mirror comet's glm-5.3 fp8 KV + 0.85 recipe** (`~/llama` @ `ee671e1`)
  Llama's glm-5.3 engine still ran the cookbook's bf16-KV 0.8 cell while comet rolled an fp8 KV cache and raised the mem fraction to 0.85, its canary-proven ceiling. Mirrored both deltas into llama's recipe so both fleets serve these weights with the same engine config, then replaced the running engine with one on the new recipe.
  - Rolled via the raise-target/cancel-older runbook: the new engine (job 2686423) booted with flashmla_sparse_q8 prefill / flashmla_kv decode and fp8_e4m3 KV at 457,536 tokens per rank with 20.68 GB free — exactly comet's canary numbers — and passed reasoning-split, tool-call, cache-report, and gateway smoke tests before the old engine (job 2557337) was cancelled.
- [x] **Roll glm-5.3 fleet to mem-fraction 0.85** (`/mnt/weka/shrd/k2m/yuekai.sun/sglang-serve` @ `c180b2d`)
  Every recent 0.8 engine log showed the KV pool saturating (0.97-1.00) under real long-context traffic, and the canary proved 0.85 boots and serves with ~11 GB headroom, so the main recipe now carries 0.85 with the 0.85 verdict and the 0.9 rejection documented in its header.
  - All three glm53-main engines were replaced one at a time (raise target, wait healthy, cancel old, restore) with no serving dip; two cycles waited out QOSGrpNodeLimit pends of 8-20 min for a group node. Each new boot logged the exact canary numbers (KV 26.19 GiB / 457,536 tokens per rank, ~20.7 GB free).
  - The glm53-himem pool and recipe are retired; a gateway smoke test on the rolled fleet answered exactly, and live traffic flowed on the new engines immediately.
- [x] **Scale glm53-main to four engines** (`/mnt/weka/shrd/k2m/yuekai.sun/sglang-serve` @ `c03ebf2`)
  Raised the pool target from three to four for more glm-5.3 capacity after the 0.85 rollout. The controller submitted job 2686887, which started immediately (no QOSGrpNodeLimit pend) and booted with the rolled recipe's exact numbers (KV 26.19 GiB / 457,536 tokens per rank, ~20.7 GB free) before registering as the fourth healthy gateway worker.
