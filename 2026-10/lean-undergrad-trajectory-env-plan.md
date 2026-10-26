---
title: Lean undergrad-gap formalization environment plan
description: Refined plan for an agent swarm that formalizes undergrad math missing from mathlib, with trajectories and a repo-level RL environment as the headline artifact
date: 2026-10-25
---

## The idea and what is new about it

Deploy a swarm of agents to formalize the [undergrad math topics missing from mathlib](https://leanprover-community.github.io/undergrad_todo.html) (machine-readable: [undergrad.yaml](https://raw.githubusercontent.com/leanprover-community/mathlib4/refs/heads/master/docs/undergrad.yaml)) from textbooks, and keep the agents' trajectories as training data.

Textbook-scale formalization itself is no longer novel: [RepoProver](https://arxiv.org/abs/2604.03071) (130K LOC in a week, 30K Claude Opus agents, ~$100K), [M2F](https://arxiv.org/abs/2602.17016) (154K LOC), [AutoformBot/ATLAS](https://arxiv.org/abs/2605.29955) (26 open-access books, 45K declarations), and the quality audit in [2606.14000](https://arxiv.org/html/2606.14000). None is a data paper. The two genuine novelties, agreed as the headline:

1. **Open-weight policies, so trajectories are usable.** Anthropic/OpenAI terms forbid training competing models on outputs, so the Claude-generated trajectories of the papers above are unusable as training data. Open models (DeepSeek, Qwen3-Coder, Kimi, GLM, gpt-oss) are the only route to a releasable repo-level Lean trajectory corpus.
2. **A repo-level RL environment, "SWE-Gym for Lean".** [OProver/OProofs](https://arxiv.org/abs/2605.17283) releases 6.86M verified proofs with repair trajectories, but all isolated-statement. Nobody has released tasks where the agent navigates a real library, reuses existing API, and lands a PR that passes linters and review.

The headline is the dataset/environment, not a model result. Volume estimate: the final library may be only a few thousand declarations, but trajectories run to a few B tokens (e.g. the Tropp-monograph subset of [IFM/research-lean-formalization-rollouts](https://huggingface.co/datasets/IFM/research-lean-formalization-rollouts) is 14k records / ~492M tokens).

## Decisions

- **Targets:** only the genuinely missing clusters, not all 111 undergrad_todo items. Many items are already in mathlib and merely unlinked in `undergrad.yaml` (see the [trivial-targets wiki](https://github.com/leanprover-community/mathlib/wiki/Undergrad-TODO-trivial-targets)); others are not theorems ("examples", "phase portraits"). Missing clusters: distribution theory (large, wholly absent); ODE qualitative theory (maximal solutions, Duhamel, linearisation/stability); Laurent series, residues, meromorphic functions; Fourier series (Dirichlet, Fejér); numerical linear algebra (row reduction, LU, Gershgorin, Jacobi/Gauss–Seidel, Newton); Jordan normal form and matrix exponential; representation theory of finite groups (characters, Fourier on finite abelian groups). Skip numerical ODE: 2606.14000 already did it.
- **Base repo:** fork TauCeti, not mathlib. Mathlib is 2.2M LOC and builds for hours; every scaled effort uses a downstream lake project pinned to a mathlib revision. [TauCeti](https://github.com/TauCetiProject/TauCeti) (Lean FRO + Mathlib Initiative) already packages mathlib's linter set, axiom allowlist, import guard and open adversarial review rubrics. Fork all three repos: TauCeti (strip their math, keep `scripts/`, `.github/`, lakefile, pinned mathlib), [TauCetiRoadmap](https://github.com/TauCetiProject/TauCetiRoadmap) (one roadmap per cluster: README + challenge files + textbook-chapter mapping), [TauCetiReview](https://github.com/TauCetiProject/TauCetiReview) (rubrics and engine, edited as below). Staying rubric-compatible keeps upstreaming to real TauCeti free.
- **No `Blueprint/` library and no sorry-allowed integration branches.** Agents keep `sorry`s on their own branches; `main` stays sorry-free under unchanged TauCeti CI. Frozen target statements live as *challenge files* in the roadmap fork (TauCeti's own `Suggested.lean` pattern), verified against proof PRs by the Lean FRO comparator (see "Statement freeze").
- **Orchestrator:** a thin, environment-centric one composed from Symphony (dispatcher) and Choir (protocol); see below. Not RepoProver.
- **Worker:** dsh headless, not RepoProver's agent loop; verified, see "Worker".
- **Tracker:** GitHub issues/PRs on the fork, kept viable by collapsing review traffic to one comment per round; see "Review changes".
- **Executor:** Slurm, as in the existing `undergrad-todo` runs.
- **Contamination:** not a concern now (Rudin, Axler, Artin, Munkres, Shakarchi are in pretraining corpora anyway). Mathlib community dynamics are irrelevant once building on TauCeti.
- **Licensing:** deferred, tracked as tech debt in this plan (below).

## Does TauCeti's QC catch what 2606.14000 found?

As review rubrics, mostly; as mechanical gates, no. TauCeti CI ([AGENTS.md](https://github.com/TauCetiProject/TauCeti/blob/main/AGENTS.md)) enforces: no `sorry`; axioms ⊆ {`propext`, `Classical.choice`, `Quot.sound`} (kills `native_decide`); no meta imports; full mathlib linter set; import-header guard; auto-merge when every rubric approves on the current head and the PR touches only `TauCeti/`.

**TauCeti review, as it is.** After CI is green, one read-only agent per rubric (prompt = `rubrics/_common.md` + angle file; Read/Grep/Glob only; clean-room HOME; verdict read through a one-time marker token so PR text cannot forge an approve) reviews a workspace holding the PR head, the roadmap repo and pinned mathlib source. Rubrics run sequentially and a `block` halts the round. Output is a head-pinned **scoreboard** comment (rubric → verdict, head SHA, spend, hidden provenance) that auto-merge reads, plus a thread per rubric with findings posted individually; authors contest on a rubric's thread, which reopens that rubric. Reviewers acquire a git lease per (repo, PR, head). Supported reviewers: Claude, Codex, Kiro, and DeepSeek/MiniMax/Grok via OpenRouter through `pi`. Detailed run records go to TauCetiData; `judge.py` there A/B-tests review runs with a cross-family judge panel and human escalation.

The [rubrics](https://github.com/TauCetiProject/TauCetiReview/tree/main/rubrics): `scope`, `correctness`, `reuse`, `attribution` are blocking integrity angles; `api-design`, `generality`, `placement`, `naming`, `documentation`, `proof-quality` may only approve or request changes.

| 2606.14000 problem | TauCeti mechanical | TauCeti LLM review | Gap |
|---|---|---|---|
| Semantic drift (Lean ≠ NL source) | none | `correctness.md`: adversarial hunt for mis-formalization, vacuity, content moved into hypotheses, `True` placeholders, unexercised predicates, faked prerequisites | Judges against the roadmap, not a textbook span; no round-trip; same Skolemization-misreading risk as the paper's judge |
| Re-proving mathlib (`exact?` finds it) | none | `reuse.md`: grep mathlib + TauCeti per declaration, goal, intermediate step | Grep-by-LLM is weaker than the paper's `exact?+all` probe |
| Cross-file reuse (B re-derives A inline) | none | `reuse.md`, partially | Nobody checks textbook dependency edges appear as name references |
| Sorries / axioms | yes, hard | — | Fine once statements live outside `main` |
| Low coverage (48% fully proved) | — | — | Process metric; measure it |
| Statement weakened to make proof pass | none | sometimes | Critical for RL reward integrity; must be mechanical |

**Review changes (decided).** We are generating training data, not saving tokens, so: run all ten rubrics in parallel every round (no block-halts; blocked PRs still yield reviewer trajectories), and post **one comment per round**: the marked scoreboard header (kept byte-compatible so auto-merge still parses it) with per-rubric findings as collapsed `<details>` sections. This cuts GitHub content requests per round from 11+ to 1. Consequences: GitHub's 65,536-char comment cap means per-rubric findings are truncated with a pointer to the archived record (the engine already writes full records; our trajectory store takes TauCetiData's role); author contests become a reply on the single comment naming the rubric (`contest: reuse — …`); the integrity rubrics run first only for latency, not for gating. Changes land in `runner/post.py` and the merge workflow of the TauCetiReview fork. Also: extend `correctness.md` to take the textbook span, add round-trip NL back-translation as a second vote, add Skolemization-idiom guidance.

**Mechanical gates to add on top of TauCeti CI:** (1) statement freeze via comparator (below); (2) `exact?` probe on every new theorem, hit ⇒ request_changes with the lemma named (also a reuse-rubric label); (3) trivial-proof tag (closes under `simp`/`aesop`/`omega`), not blocked but marked low-value; (4) AutoformBot's structural tagger (vacuous bodies, hypothesis smuggling, trivial instances) as a non-blocking label feeding the correctness rubric; (5) new `def`/`structure` must have a nontrivial instance or consumer in the same PR.

## Statement freeze: challenge files + comparator

The [Lean FRO comparator](https://github.com/leanprover/comparator) (now `lake comparator` / `lake check` in core since v4.35.0) takes a trusted `Challenge` module with `sorry`'d statements and an untrusted `Solution` module, and guarantees the listed theorems prove the *same statement* (every constant in the statement identical, followed down through definitions), use only permitted axioms, and are kernel-accepted. Optional `definition_names` holes let a solution fill in definitions whose name, type, universes and safety level must match.

Flow:

| Step | Goes to | Gate | Task type |
|---|---|---|---|
| New definitions + minimal API + nontrivial example or consumer | code `main`, small sorry-free PRs | TauCeti CI + rubrics | *sketch* (definition part) |
| Challenge file: `sorry`'d targets per chapter, each with its textbook span ref, importing `main` at a pinned commit | roadmap fork | builds against `main`; correctness + fidelity + scope review | *sketch* |
| Proof, developed on a branch where `sorry`s are fine | code `main` | sorry-free + comparator vs. the challenge + TauCeti CI + rubrics | *prove* |
| Stuck → propose sub-challenges (Choir-style decomposition, but to the roadmap fork, never `sorry`s to `main`) | roadmap fork | as for challenge files | *decompose* |

Scheduling is leaves-up (a node is assigned once its dependencies are proved), as in LeanMarathon; textbook dependency graphs are wide enough. Helper lemmas need no freezing (kernel-proved; only placement/duplication matter, which `reuse` catches). Costs: challenge files go stale when `main` moves, so the roadmap fork needs a nightly rebuild against current `main`, and any edit to a frozen statement goes back through correctness review (a *maintain* task, not a backdoor); workers need the roadmap repo checked out (TauCeti reviewers already do).

## Orchestrator: Symphony dispatcher + Choir protocol, environment-centric

Survey conclusion (unchanged): every existing system — [UMich repoprover fork](https://github.com/umich-fatml/repoprover), [AutoformBot](https://github.com/facebookresearch/autoform-bot), [LeanMarathon](https://arxiv.org/abs/2606.05400), [Choir](https://arxiv.org/abs/2609.31903), [TauCetiWorker](https://github.com/TauCetiProject/TauCetiWorker) — is formalization-centric with traces as an afterthought. We need the first-class object to be a task = (environment snapshot, prompt, deterministic reward), library as side effect. Compose, don't adopt.

**Shape:** an orchestrator that creates issues on the TauCeti fork, and a dispatcher that watches those issues, makes an isolated workspace per issue and runs a worker session in it.

- **Dispatcher = the [Symphony spec](https://github.com/openai/symphony/blob/main/SPEC.md)** (tracker adapter → poll → per-issue workspace with lifecycle hooks → agent session; retries with backoff, stall detection, reconciliation on issue-state change, concurrency caps; deliberately no task semantics). Implement the spec ourselves (it is small) rather than use the Elixir reference, because: it runs `codex app-server` only; it is single-machine by design (not a distributed scheduler); it keeps blocked-issue state in memory; and Lean workspaces need worktrees from a local bare mirror plus a read-only shared mathlib (`.lake/packages`) under a sandbox — the Oct 25 log records agents deleting 125 files from a shared Mathlib checkout and corrupting `~/.cache/mathlib`. Community ports ([symphony-ts](https://github.com/sociotechnica-org/symphony-ts) with a `generic-command` runner and bare-mirror clones, [oh-my-symphony](https://github.com/cskwork/oh-my-symphony) with pluggable backends) are references for the adapter seams.
- **Protocol = Choir**, adapted: issues as typed tasks whose bodies open with a YAML record; dependency graph rederived from the built project; decomposition and salvage of failed PRs; the four-check gate (rebuild, axiom-honesty, sorry-delta, statement-immutability). Three Choir choices change because our workers are not an untrusted crowd: the dispatcher is the only claimer (no comment races, no day-long leases, branches pushed to the same repo, no forks); statements live in challenge files, not `sorry`'d on `main`; and statement-writing and review become dispatched tasks (their trajectories are data) rather than orchestrator-agent work — the Choir paper names the orchestrator agent as its scaling bottleneck.
- So the orchestrator is a **deterministic scheduler** (challenge-file DAG → issues, readiness, attempt budgets, task-record emission) plus a **small LLM planner** for judgment calls only: chapter → node split, triage of repeatedly failing tasks, salvage vs. decompose.
- **Executor = Slurm:** dispatcher on a login node or a long-lived service job; standing allocations; each session an `srun` job step with its own CPUs/memory; node-local read-only mathlib cache; a per-node Lean service (REPL pool + LSP + Loogle via MCP, the one RepoProver piece worth keeping) shared by the steps on that node.
- **Task taxonomy = TauCetiWorker's cascade** so *maintain* tasks (rebase, mathlib bump, lint repair, fix CI, fix review findings, mathlib-overlap fix) are scheduled alongside sketch/prove/review/decompose. Once a PR is open the same issue stays active; CI failures and review findings trigger continuation turns on the same worker session (`--session-id`), so one trajectory covers the whole "land a PR" episode.

Issue body header (the canonical, replayable task record; joined on issue number to PR, CI, verdicts, merge outcome and trajectory):

```yaml
type: prove            # sketch | def | prove | decompose | review | maintain
base: <main sha>
challenge: roadmap/Distributions/Ch3.lean
theorems: [Distribution.deriv_heaviside]
source: {book: <id>, span: "§3.2, Thm 3.4"}
deps: [412, 415]       # issues that must be closed first
budget: {attempts: 3}
```

**GitHub rate budget.** GitHub allows ≤80 content-generating requests/minute and ≤500/hour per account ([docs](https://docs.github.com/rest/overview/rate-limits-for-the-rest-api)); TauCeti's REVIEWING.md already documents 2-second comment spacing and 422 "submitted too quickly" retries at their volume. With one review comment per round, no label churn (state derived from issue open/closed + linked PR status), and separate GitHub Apps for author, reviewer and orchestrator (separate budgets; do not multiply author machine accounts, which breaches GitHub ToS), a merged task costs ≈6 requests (issue, PR, scoreboard create + edit, merge, close) → ~80 merged PRs/hour, failed ones ~3 each. RepoProver's record run was ~35 declarations/hour, so GitHub fits with headroom; self-hosted Forgejo only if 10× more is wanted. CI runners self-hosted on the cluster regardless.

## Worker: dsh headless, verified

dsh over RepoProver's agent loop because the trajectories should come from a general coding harness with a standard tool set (the harness a trained model will later run in), dsh is maintained in-house so logging gaps are fixes not workarounds, and `dsh --profile headless` already does one-task-then-exit with `--session-id` resume and persisted session logs. RepoProver's role prompts become per-task-type prompt templates; its REPL pool becomes the per-node Lean MCP service; its tracker/merge queue are replaced by the dispatcher.

Verified on 2026-10-25 by running headless under `setsid`, stdin `/dev/null`, `DISPLAY` unset, `TERM=dumb`, against `deepseek-v4.1-flash` on the `m2` OpenAI-compatible route:

- **Tool outputs persisted exactly as the model saw them.** A 372 KB command output was tail-truncated by the bash tool to 49,931 chars with `[...]` / `Omitted N bytes` markers; the persisted `tool/result` event is byte-identical to that, and the model's own description of what it saw matched. No further truncation in `session.v4.jsonl.zstd`.
- **Reasoning captured:** `assistant/message` events carry `{"type":"reasoning","text":…}` blocks from the open model.
- **Runs detached, no GUI/web token**, exit 0, empty stderr — but headless does not read the web profile's stored credential: the job step must export `LLAMA_API_KEY` (the dsh-web unit takes it from `~/dsh-web/.env`).
- **Use the session file, not `--json`, as the trajectory source:** the `--json` stream clipped the same tool result to 8,192 chars; it is a progress feed. Event types: `system/message`, `user/message`, `assistant/message`, `tool/call`, `tool/result`, `request/header`, `step/*`, `turn/*`, plus resolved model/provider per step.
- **Spill files are invisible to sandboxed bash:** long outputs spill to host `/tmp/dsh-spill-*/…`; under the headless `workspace-write` sandbox, `bash` cannot see host `/tmp` but the `read` tool can (verified). For Lean workers (`lake build` output is long) either pin the spill dir inside the workspace in the `lean-worker` profile or instruct in its AGENTS.md to read spill paths with `read`/`grep`, never `bash`.

`lean-worker` profile to build: credential export in the job step, spill dir pinned, Lean MCP (REPL/LSP/Loogle), TauCeti AGENTS.md conventions, restricted tool set, vLLM/m2 endpoint, and a session→trajectory exporter (a dsh-flavoured counterpart of the existing RepoProver `export_rollouts.py`). Specialized provers (OProver, Goedel) can be added later as a "subcontract this goal" tool without changing the harness.

## Task schema (emitted automatically from every merged PR)

- *sketch*: textbook span → definitions PR to `main` and/or challenge-file statement; reward = elaborates ∧ correctness rubric approves ∧ fidelity judge.
- *prove*: challenge statement → proof PR to `main`; reward = build ∧ no sorry ∧ axiom allowlist ∧ comparator pass ∧ `exact?` miss (binary, exact).
- *decompose*: stuck target → sub-challenge PR to the roadmap fork; reward = sub-challenges elaborate ∧ parent provable from them ∧ correctness review.
- *review*: PR diff → per-rubric verdict; labels from merge outcome + meta-review.
- *maintain*: mathlib bump / refactor breaks N files or challenge files → fix; reward = green CI with statements unchanged (free on every re-pin).

Log per PR: full dsh session trajectory, Lean service observations, CI results, rubric verdicts, final diff, textbook span. Keep failures (RL negatives, OProver-style repair pairs).

Environment evaluation (not a model): coverage per cluster, fidelity-judge agreement with a human sample, `exact?`-hit rate, reviewer precision from meta-review.

## Phases

0. Audit the target clusters with LeanSearch/Loogle/`exact?`: confirm absence, estimate declaration counts, check ATLAS overlap (`v1/README.md` of [atlas-lean](https://github.com/facebookresearch/atlas-lean); import its statements as targets where it overlaps). Ship unlinked-item `undergrad.yaml` PRs to mathlib as cheap goodwill.
1. Infrastructure: the three forks (TauCeti stripped, roadmap with challenge files, review engine with single-comment parallel rounds); comparator + extra gates in CI on self-hosted runners; the dispatcher (Symphony spec, Slurm executor, worktrees + read-only mathlib, per-node Lean MCP); the `lean-worker` dsh profile and exporter; GitHub Apps per role.
2. Pilot on 2–3 clusters with the strongest open model; accept lower yield than Claude; log everything.
3. Release environment + trajectories; optionally SFT/RL a ~30B open model and run expert iteration (trained model becomes the swarm).
4. Propose the clusters as TauCeti roadmaps.

## Tech debt (deferred deliberately)

- **Textbook licensing.** Trajectories embed textbook text, so releasing them needs redistribution rights, not reading access; NC clauses (Lebl, Trench are CC-BY-NC-SA) may restrict commercial downstream training. Pay off: a per-textbook license column in the roadmap manifest, a release filter that strips or excludes spans from non-redistributable sources, and an NC policy decided before any public release. Open-license candidates: Grinberg (public domain), Hefferon, Judson, OpenStax, Axler (open access).
- **Model output licenses.** DeepSeek (MIT), Qwen (Apache-2.0), Kimi (modified MIT) are fine; verify any other model used by swarm or reviewers.
- **Closed-model verdicts.** If closed models judge, confirm the "labels, not generations" reading of their ToS before publishing labels.
- **Challenge-file staleness.** Nightly rebuild against `main` and a reviewed *maintain* path are designed but not built; until then a mathlib bump can silently invalidate the frozen targets.
- **Lean tools and services for workers are unspecified.** The plan assumes a per-node Lean MCP service (REPL pool + LSP + Loogle) but has not decided its contents. [TauCetiWorker](https://github.com/TauCetiProject/TauCetiWorker) exposes none (read from its `prompts/roadmap.md`, `prompts/local-verification.md`, and `docs/verification.md`, `docs/shared-mathlib.md`, `docs/sandbox.md`; the `fix`/`bump`/`rebase`/`lint-repair`/`v0` prompts were not read): agents get their CLI's stock tools, `grep` over the vendored `.lake/packages/mathlib`, foreground `lake build --iofail`, prefetched caches (`lake exe cache get`, `lake cache get` from `cache.taucetiproject.org`), `claim.sh`, `git-safe-push`, `gh-safe-pr-create`, and `tauceti verify` (scoped changed-module build/axiom/lint checks with exact-input receipts). Candidates to evaluate: [lean-lsp-mcp](https://github.com/project-numina/lean-lsp-mcp) (goal state, diagnostics, `multi_attempt`, local search, local Loogle, REPL mode), a shared-Mathlib read-only lower layer with a per-round private writable layer via rootless bubblewrap OverlayFS (TauCetiWorker's design; needs user namespaces on compute nodes; addresses the Oct 25 shared-Mathlib corruption), and `tauceti verify`-style scoped verification for the *prove* reward. Open: which tools to expose, whether to run lean-lsp-mcp per session or per node, and that giving workers proof-state tools makes our trajectories not comparable to TauCeti's own. Until decided, workers get only dsh's stock tools plus `lake build`.
- **dsh spill/credential quirks.** The spill-dir pin and headless credential export are profile config, not harness fixes; if the `lean-worker` profile is reused elsewhere these must travel with it.

## Related

- A RepoProver run over undergrad books is already in progress on the HPC cluster (`undergrad-todo` project; see the Oct 25 task entry on distributed four-node runs). This plan is the next iteration of that effort.
