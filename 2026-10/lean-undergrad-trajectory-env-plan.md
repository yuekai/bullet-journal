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
- **Base repo:** fork TauCeti, not mathlib. Mathlib is 2.2M LOC and builds for hours; every scaled effort uses a downstream lake project pinned to a mathlib revision. [TauCeti](https://github.com/TauCetiProject/TauCeti) (Lean FRO + Mathlib Initiative) already packages mathlib's linter set, axiom allowlist, import guard and open adversarial review rubrics. Fork all three repos: TauCeti (strip their math, keep `scripts/`, `.github/`, lakefile, pinned mathlib), [TauCetiRoadmap](https://github.com/TauCetiProject/TauCetiRoadmap) (one roadmap per cluster: README + `Suggested.lean` + textbook-chapter mapping + manifest), [TauCetiReview](https://github.com/TauCetiProject/TauCetiReview) (rubrics, edited as below). Staying rubric-compatible keeps upstreaming to real TauCeti free.
- **Agent runtime:** the [UMich-FATML repoprover fork](https://github.com/umich-fatml/repoprover) already uses an OpenAI-compatible endpoint (vLLM/SGLang) and has training-grade trajectory logging. Not committed to RepoProver as the orchestrator, though; see the survey below.
- **Contamination:** not a concern now (Rudin, Axler, Artin, Munkres, Shakarchi are in pretraining corpora anyway). Mathlib community dynamics are irrelevant once building on TauCeti.
- **Licensing:** deferred, tracked as tech debt in this plan (below).

## Does TauCeti's QC catch what 2606.14000 found?

As review rubrics, mostly; as mechanical gates, no. TauCeti CI ([AGENTS.md](https://github.com/TauCetiProject/TauCeti/blob/main/AGENTS.md)) enforces: no `sorry`; axioms ⊆ {`propext`, `Classical.choice`, `Quot.sound`} (kills `native_decide`); no meta imports; full mathlib linter set; import-header guard; auto-merge when every rubric approves. The [rubrics](https://github.com/TauCetiProject/TauCetiReview/tree/main/rubrics): correctness, reuse, scope, attribution are blocking "integrity" angles; api-design, generality, placement, naming, documentation, proof-quality are not.

| 2606.14000 problem | TauCeti mechanical | TauCeti LLM review | Gap |
|---|---|---|---|
| Semantic drift (Lean ≠ NL source) | none | `correctness.md`: adversarial hunt for mis-formalization, vacuity, content moved into hypotheses, `True` placeholders, unexercised predicates, faked prerequisites | Judges against the roadmap, not a textbook span; no round-trip; same Skolemization-misreading risk as the paper's judge |
| Re-proving mathlib (`exact?` finds it) | none | `reuse.md`: grep mathlib + TauCeti per declaration, goal, intermediate step | Grep-by-LLM is weaker than the paper's `exact?+all` probe |
| Cross-file reuse (B re-derives A inline) | none | `reuse.md`, partially | Nobody checks textbook dependency edges appear as name references |
| Sorries / axioms | yes, hard | — | Conflicts with sorry-first sketching (below) |
| Low coverage (48% fully proved) | — | — | Process metric; measure it |
| Statement weakened to make proof pass | none | sometimes | Critical for RL reward integrity; must be mechanical |

Also useful: `tauceti-review` runs on open models (DeepSeek/MiniMax via OpenRouter through `pi`, Codex via OpenAI-compatible endpoints), so review can be fully open-weight, or closed models can serve as judges only (verdicts are labels, not generations). TauCeti's meta-review A/B machinery (`judge.py` in TauCetiData: two review runs, cross-family judge panel, human escalation) yields reviewer training labels for free.

**Hard conflict:** RepoProver merges `sorry`-ed sketches to main, then provers fill them; TauCeti CI rejects any `sorry` on main. Resolution: two lake libraries in the fork. `Blueprint/` allows `sorry`; CI builds it, lints, checks axioms, and runs correctness + scope rubrics on statements. The gated no-sorry library is where declarations graduate with a proof. The graduation PR is exactly the *prove* task.

**Mechanical gates to add:** (1) statement freeze for prover PRs; (2) `exact?` probe on every new theorem, hit ⇒ request_changes with the lemma named (also a reuse-rubric label); (3) trivial-proof tag (closes under `simp`/`aesop`/`omega`), not blocked but marked low-value; (4) source-fidelity judge: extend `correctness.md` with the textbook span, add round-trip NL back-translation as a second vote, add Skolemization-idiom guidance; (5) new `def`/`structure` must have a nontrivial instance or consumer in the same PR.

## Orchestrator survey: nothing fits all five requirements

Requirements: open-model backend; textbook/roadmap-driven multi-file library growth; TauCeti-grade review; kernel-level statement-immutability gate; training-grade trajectory logging.

- **UMich repoprover fork:** has open backend and logging; build-only gate, sorries on main, own reviewer prompts; the AutoformBot paper calls the original "loosely organized". Best starting point for the agent loop.
- **[AutoformBot](https://github.com/facebookresearch/autoform-bot):** 3-tier orchestrator, MCP tools (REPL, LSP, Loogle), worktrees, skill loading, and an evaluation metaprogram that tags vacuous bodies, hypothesis smuggling and trivial instances. Public `main` is a plugin/CLI without orchestration; the `execution` overlay branch was not reachable. Steal the evaluation metaprogram. ATLAS already covers 26 open-access books; check its `v1/README.md` for overlap with the target clusters and import its statements as targets where it overlaps.
- **[LeanMarathon](https://arxiv.org/abs/2606.05400) ([repo](https://github.com/YuanheZ/LeanMarathon)):** best contract/gate design (Stage-1 adversarial target-review loop before proving; workers confined to a frozen region; prose↔formal dependency parity; 7-check CI), but Codex-CLI-bound, single blueprint file, research-paper-shaped. Port the design, not the code.
- **[Choir](https://arxiv.org/abs/2609.31903) ([repo](https://github.com/Weber-GeoML/Choir)):** not a prover; GitHub issues as tasks, workers claim via fork PRs. Its deterministic gate is exactly the RL reward spec: rebuild, axiom-honesty, sorry-delta (with a decomposition exception), statement-immutability via the Lean FRO kernel-level comparator (follows definitions down; stronger than a byte diff).
- **[TauCetiWorker](https://github.com/TauCetiProject/TauCetiWorker):** one-unit-per-round cascade (rebase → mathlib bump → lint repair → fix CI → fix review → review → mathlib-overlap scan → roadmap item); supports Claude/Codex/Kiro and DeepSeek-V4-Pro/MiniMax via OpenRouter. The cascade is the right task taxonomy; its logs strip thinking and truncate tool results, so unusable for training.
- M2F (thin repo), FormalFlow (not released as a framework), Lean Pool (archive maintenance): pass.

**Conclusion: roll a thin orchestrator that composes these.** Every existing system is formalization-centric with traces as an afterthought; this project needs an environment-centric one where the first-class object is a task = (environment snapshot, prompt, deterministic reward) and the library is the side effect. That inversion touches the core loop, so a small new orchestrator costs about the same as retrofitting. The heavy parts all exist.

Composition: gate = Choir's four checks (Lean FRO comparator for statements) + TauCeti axiom/linter/import checks + AutoformBot's structural tagger as a non-blocking label. Review = `tauceti-review` engine + rubrics, self-hosted on open endpoints, `correctness.md` extended with the textbook span. Contracts = LeanMarathon's, generalized to one blueprint file per chapter in `Blueprint/`. Agent loop + logging = the repoprover fork, dropping its tracker/merge queue. Task taxonomy = TauCetiWorker's cascade. New code = task DAG from roadmap/manifest, leases, worktrees, REPL pool, merge queue, and the emitter that serializes every merged PR into task records. GitHub-issues-as-queue is fine at this scale; RepoProver's file-based tracker if API rate limits bite at thousands of agents.

## Task schema (emitted automatically from every merged PR)

- *sketch*: textbook span → `Blueprint/` statement; reward = elaborates ∧ correctness rubric approves ∧ fidelity judge.
- *prove*: `Blueprint/` statement → gated-library proof; reward = build ∧ no sorry ∧ axiom allowlist ∧ statement unchanged ∧ `exact?` miss (binary, exact).
- *review*: PR diff → per-rubric verdict; labels from merge outcome + meta-review.
- *maintain*: mathlib bump breaks N files → fix; reward = green CI with statements unchanged (free on every re-pin).

Log per PR: full message/tool-call trajectory, REPL observations, CI results, rubric verdicts, final diff, textbook span. Keep failures (RL negatives, OProver-style repair pairs).

Environment evaluation (not a model): coverage per cluster, fidelity-judge agreement with a human sample, `exact?`-hit rate, reviewer precision from meta-review.

## Phases

0. Audit the target clusters with LeanSearch/Loogle/`exact?`: confirm absence, estimate declaration counts, check ATLAS overlap. Ship unlinked-item `undergrad.yaml` PRs to mathlib as cheap goodwill.
1. Infrastructure: the three forks, `Blueprint/` library, gates, orchestrator, logging.
2. Pilot on 2–3 clusters with the strongest open model; accept lower yield than Claude; log everything.
3. Release environment + trajectories; optionally SFT/RL a ~30B open model and run expert iteration (trained model becomes the swarm).
4. Propose the clusters as TauCeti roadmaps.

## Tech debt (deferred deliberately)

- **Textbook licensing.** Trajectories embed textbook text, so releasing them needs redistribution rights, not reading access; NC clauses (Lebl, Trench are CC-BY-NC-SA) may restrict commercial downstream training. Pay off: a per-textbook license column in the roadmap manifest, a release filter that strips or excludes spans from non-redistributable sources, and an NC policy decided before any public release. Open-license candidates: Grinberg (public domain), Hefferon, Judson, OpenStax, Axler (open access).
- **Model output licenses.** DeepSeek (MIT), Qwen (Apache-2.0), Kimi (modified MIT) are fine; verify any other model used by swarm or reviewers.
- **Closed-model verdicts.** If closed models judge, confirm the "labels, not generations" reading of their ToS before publishing labels.

## Related

- A RepoProver run over undergrad books is already in progress on the HPC cluster (`undergrad-todo` project; see the Oct 25 task entry on distributed four-node runs). This plan is the next iteration of that effort.
