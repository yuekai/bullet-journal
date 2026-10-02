---
title: Multi-agent SFT data pipelines
description: How the arxivmath, arxivlean, repoprover, Rethlas and Danus systems on m2 generate training data — their agents, how the agents coordinate, what gets exported, and excerpts of real agent trajectories
date: 2026-10-02
---

This note describes five LLM systems on m2 that generate math training data. For each one it covers the agents, how they work together, what ends up in the training file, and short excerpts of real records. It's based on each system's code, prompts and run records, plus the exports as they stood on 2026-10-02. All paths are on m2; `~` is `/mnt/weka/home/yuekai.sun`.

Excerpts show only visible message text, tool calls and tool results, each cut short (`…`). Assistant reasoning (`think` fields) is left out.

## At a glance

| System | Source material | Agents | One training record is | Kept | Tokens | Export |
|---|---|---|---|---|---|---|
| arxivmath | arXiv papers, 51 categories | generator, verifier, full-text reviewer (single LLM calls) | a question with an exact answer (no trajectory) | 5,668 | — | `~/shrd/1T-math/data/arxivmath-training/arxivmath.jsonl` |
| arxivlean | arXiv papers, 30 `math.*` categories | formalizer plus 6 LLM gates, then a Lean prover agent | the prover's trajectory on one Lean theorem | 1,838 | 161.8M | `~/shrd/1T-math/data/arxivlean-training/sft/k3-fsmzb-correct.jsonl` |
| repoprover | Tropp's matrix concentration textbook | sketch/prove/maintain/scan/triage/progress contributors, math and engineering reviewers | one agent rollout (one PR attempt or one review) | 14,332 | 492.7M | `~/shrd/statlib/rollouts.jsonl` |
| Rethlas | 55 solveall research prompts (and 14 linalg problems) | generator, verifier | one generator or verifier session | 314 | 38.6M | `~/shrd/Rethlas/exports/solveall.{gen,ver}.jsonl` |
| Danus | the same linalg and solveall problems | main agent, GPT-5.5-pro consult, 7 workers per project, verifier, paper roles | one worker, verifier or paper session | 33,174 | 3.91B | `~/shrd/Danus/runtime/exports/sft_trajectories.jsonl` |

Two caveats:
- **arxivmath has no agent trajectories.** Its stages are one-shot model calls, and its output is question/answer pairs with a rule-based reward label. It is shaped for RL or answer-supervised training, not for imitating trajectories.
- **Danus's main agent is not in its export.** The 13 "main" records are health-check pings. The real orchestrator sessions sit unexported in `~/.kimi-code/sessions/wd_danus_a9bc6a6918dd/`.

**Shared gate.** The four trajectory exports were all gated by a strict SFT validator, `process_entry.py`, but not by the same copy:
- **repoprover, Rethlas and Danus** were re-exported on Oct 1 against `~/data-engineering/SFT/process_entry.py`.
- **arxivlean** (Aug 25) used `~/shrd/data-engineering/SFT/process_entry.py`.

The two copies differ, and how much wasn't checked. Both enforce four rules:
- every rollout must contain reasoning;
- tool calls must match the declared schemas exactly;
- no degenerate repetition;
- no leaked control markers such as `<|close|>`.

Each trajectory record is `{conversation, …, token_count, token_count_answer, token_count_think}`. In `conversation`, assistant turns carry `content`, `think` and `tool_calls`.

## arxivmath

**What it makes.** Each record is a hard question with a single exact answer, drawn from a central result of an arXiv paper. The code is in `~/shrd/1T-math`, with the MathArena submodule at `matharena/`.
- **Launch:** `scripts/arxivmath-training/run_train_array.sbatch` runs one Slurm task per category. There are 51 categories, from `cond-mat.dis-nn` to `quant-ph`.
- **Paper selection:** up to `LIMIT` papers per category (default 20), each with at least 10 citations, taken from the local crawl in `arxiv_papers_data/`.

**Stages.** Prompts are in `matharena/arxivmath/prompts/arxiv/`.
1. **Ingest** (`ingest_arxiv_crawl.py`): writes `metadata.json` and `full_text.md` for each paper.
2. **Generator** (`create_queries.py`, gpt-5.6-sol at xhigh effort, prompt `fulltext_query.md`): "determine whether a central result of the paper can be converted into a single, precise, objectively verifiable mathematical question with a unique, deterministic answer". If so it writes the question and answer; if not it rejects the paper.
3. **Verifier** (`verify_queries.py`, gpt-5.6-sol, `verify.md`): checks the question is self-contained, with no undefined terms or conventions. It also drops questions whose answer is too guessable: 0, 1, or just the question's own variable (such as "find X in terms of n" with answer n).
4. **Full-text reviewer** (`fulltext_review.py`, Claude Opus 4.8, `fulltext_review.md`): reads the whole paper and returns **keep**, **edit** or **discard**. It edits by adding assumptions that appear only in the full text, and discards questions that are wrong or not central.

**Coordination.** No agent sees another's reasoning. Each stage reads the previous stage's decision from the paper's `llm_annotation.json` and writes its own beside it. A paper moves on only on an explicit keep. Rerunning the launcher resumes from those checkpoints.

**Export.** `scripts/arxivmath-training/export_accepted_questions_as_jsonl.py` keeps papers that all three stages accepted. If the reviewer edited the question, the edited version is used.
- **Funnel:** 17,202 papers annotated → 6,952 generated questions → 6,143 verified → **5,668 exported**. Annotations date to about Jul 22; the export to Aug 7.
- **Row format:** `{prompt: [user message], label: answer, metadata: {data_source: "math__arxivmath", reward_model: {ground_truth, style: "rule"}, …}}`.
- **Training code:** `matharena/train/` has verl data prep, a rule reward and Qwen3.5-2B GRPO/SFT launchers for this data. Whether those runs happened wasn't checked.

**Example.** Paper math/0006218, "Spectral inclusion and spectral exactness for singular non-selfadjoint Sturm–Liouville problems" (25 citations), from `data/arxivmath-training/train_math_sp/math_0006218/llm_annotation.json`:

```text
[generator, gpt-5.6-sol--xhigh]
Q: Let τ[y]=w^{-1}(-(py')'+qy) be a singular, possibly non-selfadjoint Sturm–Liouville
   expression on [a,b), with a regular and b singular. Let M and L be closed realizations
   of τ having the same domain condition at b … regular truncations M_n, L_n on [a,b_n] …
A: r_n + t
[verifier, gpt-5.6-sol--medium]   {"keep": true}
[full-text reviewer, claude-opus-4-8]   action: edit
   rationale: "The result matches the quantitative content of the proof of Theorem 3.1
   (eq. (21)), giving s_n = r_n + t, and is a central contribution. The only issue is that
   the question stated the normalization identities as m·φ=-1 and m_n·φ_n=-1, whereas the
   paper explicitly uses m(λ)φ(λ)=1 … The answer is unaffected by this sign correction."
```

## arxivlean

**What it makes.** arxivlean has two phases:
- **Construction:** a gated pipeline turns arXiv theorems into Lean 4 statements, each ending in `:= by sorry`.
- **Proving:** a prover agent tries to prove each statement, and its successful trajectories become SFT data.

The code is in `~/shrd/1T-math/scripts/arxivlean-training/`, and it reuses the arxivmath stage scripts.

**Construction stages.** `run_category.sh` runs one category per job, over 30 `math.*` categories with at most 370 papers each. Prompts are in `matharena/arxivmath/prompts/lean/` and `prompts/shared/`. Every stage except the semantic judge uses gpt-5.6-sol at xhigh effort; the semantic judge uses Claude Opus 4.8.

| Stage | What it checks | Papers left |
|---|---|---|
| papers ingested | | 11,048 |
| theorem extraction | pulls out a theorem with its informal proof | 9,800 |
| candidate verification | the statement is self-contained | 8,931 |
| formalization + compile (`formalize_fulltext.md`) | writes exactly one Mathlib theorem ending in `:= by sorry`, with no new axioms or placeholder predicates; it must compile against Lean/Mathlib v4.29.0 via lean-lsp-mcp | — |
| semantic judge (`semantic_judge.md`, Opus) | Lean states the same theorem, neither weaker nor stronger: "If you are unsure, discard it." | 7,954 |
| solid authors (`solid_authors.md`) | at least one author has a real publication record in the field | 7,924 |
| hidden condition | no material hypothesis is missing from the Lean statement | 6,651 |
| prior work | the theorem is this paper's contribution, not a cited result | 3,278 |
| AI assistance | the paper discloses no LLM use, and its authors aren't all unaffiliated | **3,269** |

About 977 statements were lost between verification and the semantic judge, at the formalization and compile stage. Each gate requires an explicit keep from every earlier gate, so a malformed decision can't leak downstream. The 3,269 survivors are `data/arxivlean-training/arxivlean.jsonl`. Each task's `label` is the Lean statement and its `hint` is the paper's informal proof; the hint is never shown to the prover.

**Prover agent.** Kimi K3 (`moonshot/k3-fsmzb`) runs inside MathArena, one attempt per task (`run_proofs_array.sbatch`, 64 problems per array task). Its tools:
- `verify_lean`: compiles a snippet against Mathlib.
- `loogle`: Mathlib lemma search by pattern.
- `leanfinder`: semantic search over the LeanExplore index.

A run counts as correct only if the final proof compiles with the exact accepted statement. The exported system turn also declares `verify_submission` and `add_to_file`, the other tools the runtime used.

**Construction example.** Paper 0704.2824, "Sums of squares over totally real fields are rational sums of squares", passed every gate. From `data/arxivlean-training/train_math_ac/0704.2824/metadata_lean_fulltext.json`:

```text
[extracted statement] Let f ∈ ℚ[x₁,…,xₙ], and let v = (v₁,…,v_N)ᵀ be a finite column vector of
   monomials. Suppose there is an invertible real symmetric positive-semidefinite matrix B …
   such that … f = ∑ B_ij v_i v_j. Then there exists a rational symmetric positive-semidefinite
   matrix C ∈ Mat_N(ℚ) such that f = ∑ C_ij v_i v_j. …
[formalizer, gpt-5.6-sol]
   theorem exists_rational_gram_matrix_of_real (n N : ℕ) (f : MvPolynomial (Fin n) ℚ)
       (v : Fin N → (Fin n →₀ ℕ)) (B : Matrix (Fin N) (Fin N) ℝ) (hBsymm : B.IsSymm)
       (hBpsd : B.PosSemidef) (hBinv : IsUnit B) (hgram : MvPolynomial.map (algebraMap ℚ ℝ) f = …) :
       ∃ C : Matrix (Fin N) (Fin N) ℚ, C.IsSymm ∧ C.PosSemidef ∧ f = … := by sorry
[compile] okay: True, warnings: ["declaration uses `sorry`"]
[semantic judge, claude-opus-4-8] keep: "The Lean statement faithfully captures the hypotheses
   (rational polynomial f, monomial basis v, invertible real symmetric PSD B …) and the
   conclusion (existence of a rational symmetric PSD Gram matrix C …)."
[hidden condition] keep: "This accurately formalizes Theorem 1.2. … assumes that B is invertible …"
[prior work] keep: "The extracted statement is exactly Theorem 1.2, which the paper presents
   as its own generic positive result toward Sturmfels' open question. …"
[AI assistance] keep: "… Its acknowledgements mention only named human colleagues and an
   anonymous referee. The author is institutionally affiliated …"
```

**SFT export.** `export_agent_trajectories_sft.py` writes `data/arxivlean-training/sft/k3-fsmzb-correct.jsonl`, dated Aug 25.
- **Kept:** 1,838 judge-correct trajectories, 161.8M tokens (mean 88k, median 69.5k).
- **Rejected by the gate:** another 1,236 judge-correct trajectories, about 40%, in `k3-fsmzb-correct.rejected.jsonl`. The most common reason is that the assistant refers to a harness instruction ("oververbosity") that appears nowhere in the conversation.
- **Incorrect attempts:** `k3-fsmzb-other.jsonl` holds 61 of them, a partial export rather than all of them.

**Example.** Problem 35 (arXiv 1012.0778), which asks for the periodic points of a polynomial map on F₂³:

```text
[system] You are an expert Lean 4 proof engineer. You prove formal Lean statements using the
         available verification and library-search tools.
[user]   You are given a formal statement and its natural language description. Your task is
         to generate a proof for the statement using Lean v4.29.0. Under no circumstance are
         you allowed to add any axioms or assumptions. …
[assistant] I'll analyze this problem. The key observation is that every state maps into the
         set S = {000, 010, 111, 011} in one step, S is invariant, so any periodic point must
         lie in S. Let me start by exploring the dynamics and testing my approach.
         → verify_lean(code: "import Mathlib -- Test: check that decide works on the
           relevant facts example : let f : (Fin 3 → ZMod 2) → … ∀ x, f x ∈ …")
         → loogle(…)
[tool verify_lean] ### Compiles ### True  ### Valid Proof ### True …
[tool loogle] Found one declaration mentioning Function.iterate_succ_apply. …
[assistant] `decide` works for the image check. Now let me test the full proof structure.
         → verify_lean(code: "theorem f2_polynomial_map_periodic_states : … ↔ …")
[tool verify_lean] ### Compiles ### False … Application type mismatch: The argument ih has
         type 0 < k + 1 → Function.IsPeriodicPt f (k + 1) x → … but is expected to have type
         f^[k] (f x) ∈ S …
[assistant] The induction got polluted by hypotheses depending on `m`. Let me restructure by
         proving the invariance fact as a standalone statement.
         → verify_lean(code: "theorem f2_polynomial_map_periodic_states : …")
[tool verify_lean] ### Compiles ### True  ### Valid Proof ### True …
```

## repoprover

**What it is.** Meta's RepoProver, from the paper "Automatic Textbook Formalization" (Gloeckle et al., 2026; PDF in the repo). It formalizes a whole LaTeX textbook into a Lean 4 + Mathlib repository.
- **Code:** `~/statlib/repoprover`.
- **Book:** Joel Tropp, *An Introduction to Matrix Concentration Inequalities* (arXiv:1501.01571), in 8 chapters. The project repository is `~/statlib/MatrixConcentration`.
- **Model:** not recorded in the run files that were checked.
- **Harness:** RepoProver's own tool loop, with at most 512 iterations per agent; context is compacted at 150k tokens.

**The coordinator is code, not an LLM.** `BookCoordinator` (`src/repoprover/coordinator.py`) runs a priority loop and saves state after every pass. The order:
1. Collect finished reviews and agents.
2. Merge approved PRs.
3. Launch reviews and revisions.
4. Launch provers for theorems still holding `sorry`.
5. Launch sketchers for chapters with no sketch.
6. Launch maintenance agents.

**Contributor agents.** `ContributorAgent` in `agents/contributor.py` has one shared prompt plus a mode prompt. Its tools:
- file read and write;
- git worktree operations;
- `lean_check`;
- Mathlib search;
- a sandboxed `bash`;
- the issue tracker.

Every run ends with `-- DONE`, `-- FIX`, `-- ISSUE` or `-- BLOCKED`, and the text after that line becomes the PR description. The modes:

| Mode | Job |
|---|---|
| sketch | reads a chapter's TeX and writes the Lean definitions and theorem statements, leaving the proofs as `sorry` |
| prove | fills one theorem's `sorry`; it may use other theorems still marked `sorry` |
| maintain | works one issue and closes it |
| scan | looks for API gaps, naming problems and placeholder statements, and files issues |
| triage | closes resolved issues and splits large ones |
| progress | traces what blocks each target theorem, appends to `PROGRESS_LOG.md` and files blocker issues |

**Reviewer agents** (`agents/reviewers.py`). They are read-only: file tools, Mathlib search and `lean_check`.
- **Math reviewer:** checks correctness and faithfulness to the TeX.
- **Engineering reviewer:** checks style, imports and docs. Its prompt says "Compilation is already verified before this review runs".
- **Verdicts:** "APPROVE will immediately merge the PR. REQUEST_CHANGES triggers a full revision round — use it ONLY when you have at least one [BLOCKING] finding." Non-blocking findings become follow-up issues.

**How the agents work together.** Each agent works in its own git worktree, on a branch named after its agent id.
- **Review:** a finished branch is rebased onto main and built with `lake build`. Then both reviewers run in parallel, and both must approve.
- **Merge:** an approved branch is merged `--no-ff` and rebuilt. If the merge conflicts or the build breaks, the merge is undone and the branch goes back for revision.
- **Revision:** the same agent resumes on its branch with the review feedback as its new task, up to 16 rounds. After that the PR fails and the work restarts from scratch.
- **Shared state:**
  - `issues/*.yaml`, a file-based issue tracker;
  - `CONTENTS.md`, the proof map;
  - the append-only `PROGRESS_LOG.md`;
  - `-- LEARNING:` notes, which are fed into later prompts.
- **Runs:** five runs between Aug 25 and Aug 30. The last run ended "completed" with **791 of 791 theorems proven and 0 `sorry`s**, after about 19k commits to the project repository.

**Export.** `~/shrd/statlib/rollouts.jsonl` holds one record per finished rollout, 14,332 in all.
- **Exporter:** untracked; `~/statlib/repoprover/scripts/export_sft_trajectories.py`.
- **Record ids:** `<run>/<agent_id>#<segment>.<part>`. A segment is one start-to-finish cycle, such as one revision. A part is the stretch between context compactions.
- **Role field:** `source.agent_type`.
- **System prompts:** rebuilt from the agent class, because the recordings don't store them.
- **Not included:** only status-`done` rollouts that pass the gate are kept. The runs on Aug 25 morning predate reasoning capture and contribute nothing.

| Role | Rollouts | Tokens | Mean |
|---|---|---|---|
| engineering_reviewer | 3,975 | 109.4M | 27.5k |
| math_reviewer | 3,950 | 122.5M | 31.0k |
| progress | 2,809 | 117.4M | 41.8k |
| maintain | 2,498 | 82.2M | 32.9k |
| triage | 699 | 39.4M | 56.4k |
| prove | 231 | 11.3M | 49.1k |
| scan | 137 | 8.5M | 61.9k |
| sketch | 33 | 2.0M | 60.0k |

**Examples** (`~/shrd/statlib/rollouts.jsonl`)

`20260825-182809/math-pr-00400bee#0.0`, math reviewer:

```text
[system] You are a mathematical reviewer for Lean 4 formalization projects. Your job is to
         review pull requests for mathematical correctness and faithfulness to source material. …
[user]   Please review this pull request. ## PR Information - Title: maintain for - Agent:
         maintain-0b10c5a3 - Agent Type: maintain - Files Changed: issues/077b335d.yaml …
         ## PR Description Triaged and closed issue 077b335d (non-blocking review nits from
         merged PR pr-ba67b129). All five findings are …
[assistant] I'll review this PR by first examining the issue file and then verifying the
         maintainer's claims against the codebase.
         → file_read(issues/077b335d.yaml)   → file_list(.)
[tool]   status: closed / origin: non-blocking review findings from PR pr-ba67b129 …
[assistant] Now let me verify the claims in the issue file against the actual codebase.
         → file_read(MatrixConcentration/IntrinsicDimension/Chapter7.lean, start_line 250)
[tool]   250      1 ≤ intrinsicDim A := by
         251    have hnorm : 0 < ‖A‖ := norm_pos_iff.mpr hne …
  …
[assistant] I have now verified all five findings from the issue: 1. `intrinsicDim_pos`
         docstring remark (lines 265-267): … the review observation is accurate … No change
         needed. ✓ …
```

`20260825-182809/prove-frobenius_norm_sq_eq-63e528#0.0`, prover:

```text
[user]   ## Target Prove theorem: `frobenius_norm_sq_eq_sum_singularValues_sq` …
         1. Read `CONTENTS.md` for proof architecture, status, strategy notes …
[assistant] I'll start by reading the project structure and finding the target theorem.
         → file_read(CONTENTS.md)
         → file_grep(MatrixConcentration/Background/Chapter2.lean, frobenius_norm_sq_eq_…)
[tool]   Formalization of Joel A. Tropp, *An Introduction to Matrix Concentration Inequalities*
         (arXiv:1501.01571), prepared for RepoProver. …
  …
[assistant] The proof is complete and committed.
         -- DONE
         Proved `frobenius_norm_sq_eq_sum_singularValues_sq` … 1. Rewrite using the
         trace–Frobenius identity … 2. Apply Mathlib's
         `Matrix.IsHermitian.trace_eq_sum_eigenvalues` to the PSD Gram matrix …
```

`20260825-182809/sketch-mci-intrinsic-dimension-0f281f#1.0`, a sketcher's revision round after its merge failed:

```text
[user]   ## Chapter - Source (tex): MatrixConcentration/tex/IntrinsicDimension/Chapter7.tex
         ## Reviewer Feedback Build failed: Merge conflict with main in: …/Chapter7.lean
         ## Resolving Merge Conflicts Your branch has diverged from main. Run `git_rebase()` first …
[assistant] → bash(git log main..HEAD --oneline)   → git_status()
[tool]   b1b78c4d4 Sketch Chapter 7 (intrinsic dimension): intrinsicDim API + Bernstein statements
[tool]   Working tree clean - no changes
[assistant] → git_rebase(main)
[tool]   Rebase paused due to conflicts. Conflicted files: - …/Chapter7.lean …
[assistant] → git_conflicts()   → file_read(…/Chapter7.lean)
```

The other roles open in the same way:
- **Engineering reviewer:** gets the same PR with its diff.
- **Maintain:** "## Task Work on issue a7fb8779".
- **Progress:** reads `manifest.json` and the 55k-line `PROGRESS_LOG.md`.
- **Triage:** starts from `list_issues(status=open)`.
- **Scan:** checks the 4,164 existing issues before filing new ones.

## Rethlas

**What it is.** Two agents that write and check informal proofs. A generator writes a markdown proof "blueprint" for a research problem, and a separate verifier judges it.
- **Code:** `~/Rethlas`.
- **Problems:** `agents/generation/data/{solveall,linalg}/`, 55 solveall prompts and 14 numerical-linear-algebra problems.
- **Models:**
  - Kimi K3 (`local/k3-256k`, thinking effort max) via the Kimi Code CLI;
  - a parallel Codex run (gpt-5.6-sol), excluded from the export because its reasoning is encrypted.

**Generator** (`agents/generation/AGENTS.md`).
- **Skills:** immediate conclusions, toy examples, counterexamples, subgoal decomposition, direct proving, recursive proving, failure analysis and literature search.
- **MCP tools:** `search_arxiv_theorems`, `memory_*`, `branch_update`, `verify_proof_service`.
- **Subgoals:** recursive proving can hand the subgoals of a decomposition to a subgoal-prover subagent.
- **Stopping rule:** "Stop only when the blueprint passes verification and the verified markdown proof has been published as `blueprint_verified.md`."
- **What counts as failure:** "Any verifier `wrong` verdict, any critical error, or any gap counts as verification failure."

**Verifier** (`agents/verification/AGENTS.md`).
- **Fresh session per request:** each `POST http://127.0.0.1:8091/verify` (`api/server.py`) starts a new `kimi -p` session.
- **Skills, in order:** check each statement in sequence, check referenced results (arXiv search first, then the web), then write the report.
- **Output:** `verification.json`, holding `{summary, critical_errors, gaps}`, a verdict and repair hints.
- **Verdict rule:** "correct" if and only if both lists are empty.

**How they work together.**
- **Driver:** `scripts/kimi/run_kimi.sh` resumes one generator session for up to 10 iterations. It alternates "think deeply by yourself" rounds (no search) with search-allowed rounds, and stops once `results/<pid>/blueprint_verified.md` exists.
- **Memory:** each agent keeps its own append-only JSONL channels (failed paths, subgoals, verification reports and so on). They share no memory; the HTTP call is the only link.
- **What happened in practice:** the MCP verify call timed out. Generators then found the service URL and called it directly with `curl`, often sending proof fragments for verification. Their prompt allows only whole proofs. As a result one problem, the binary deletion channel's capacity, accounts for 144 of the 287 verifier sessions.

**Export.** `~/shrd/Rethlas/exports/`: 27 generator records in `solveall.gen.jsonl` plus 287 verifier records in `solveall.ver.jsonl`, 38.6M tokens in total.
- **Role field:** `lane` (`gen` or `ver`).
- **Linalg:** contributes nothing. Its 3 Kimi sessions that ran never completed an assistant turn.
- **Kimi solveall status:** 35 solved, 13 errors, 4 failed.

**Examples** (`~/shrd/Rethlas/exports/`)

`solveall.gen.jsonl`, `session_2db681ad-…`, problem `full-multiple-break-theory-for-latent-group-structure-and-coefficients`:

```text
[system] You are Kimi Code CLI, an interactive general AI agent running on a user's computer. …
         (followed by AGENTS.md)
[user]   Use AGENTS.md exactly to solve the math problem in data/solveall/full-multiple-break-
         theory-for-latent-group-structure-and-coefficients.md. Use problem_id=solveall/… Use
         reference_dir=….refs if it exists.
[assistant] I'll start by reading the problem file and checking the workspace state.
         → Read(data/solveall/full-multiple-break-….md)
         → Bash(ls -la data/solveall/ …; ls -la results/solveall/ …; ls -la memory/solveall/ …)
[tool Read] Let {x_t}_{t=0}^T be an N-dimensional time series … with observed N×N network
         weight matrices {W_t} … x_{it}=z_{it}^⊤θ_i(t/T)+ε_{it} …
```

`solveall.gen.jsonl`, `session_4d22074e-…`, showing the verifier being reached around the MCP timeout:

```text
[assistant] The full blueprint is in place. Now submitting to the verify service.
         → mcp__reasoning_agent__verify_proof_service(statement: "For each n, observe (y,X)
           from the high-dimensional linear model …")
[tool]   Tool "mcp__reasoning_agent__verify_proof_service" failed: MCP error -32001: Request timed out
  …
[assistant] → Bash(grep -n "VERIFY_PROOF_URL\|VERIFY" mcp/server.py …; curl -s -m 5 … -X POST
           http://127.0.0.1:8091/verify -H 'Content-Type: application/json' -d '{}')
[tool]   27:VERIFY_PROOF_URL = "http://127.0.0.1:8091/verify" …
```

`solveall.ver.jsonl`, `session_b8937a55-…`, problem `capacity-binary-deletion-channel`:

```text
[user]   Run_id: 20260813T133655Z_c96ad03b96be. Statement: The following is fragment of a
         verification blueprint concerning the capacity of the binary deletion channel and its
         high-deletion coefficient c_infty … judge the internal correctness of each result …
[assistant] I'll work through the AGENTS.md workflow: initialize memory, verify each statement
         sequentially, check references, then synthesize and write the report.
         → memory_init(run_id, meta: {statement: "Fragment on BDC high-deletion coefficient …"})
[assistant] **thm:prc-bridge** — I checked every deduction: the exact Poisson factorization,
         both capacity inequalities (1)–(2) … All sound. …
         → memory_append(statement_checks, {item: thm:prc-bridge, status: pass, …})
         → memory_append(statement_checks, {item: thm:continuum-characterization,
           status: pass_with_minor_gap, …})
         → memory_append(failed_checks, {kind: gap, severity: moderate, location: "Theorem
           thm:stationary-regenerative-variational, proof of (5c)", …})
```

## Danus

**What it is.** A swarm that works on one hard problem per project and builds a graph of verified facts. Its central rule is a hard separation between producing mathematics and deciding it's correct. The fact graph and why it makes progress are covered in [How Danus makes incremental progress](how-danus-makes-incremental-progress.md).
- **Code:** `~/Danus`.
- **Problems:** the same 14 linalg problems and 53 solveall prompts that Rethlas used.
- **Models:** every agent is Kimi K3 via the Kimi Code CLI. Strategy consults go to GPT-5.5-pro.

**Agents.** The MCP gateway (`danus/gateway/roles.py`) enforces each role's tool access.

| Role | Contract | Tools | Job |
|---|---|---|---|
| Main agent | `agents/contracts/main_agent.md`, skills in `.agents/skills/` | memory, `fact_search`, `fact_revoke`, paper tools, the `danus` CLI; **no `fact_submit`** | "No math yourself." Writes elaborations, runs consults, turns their replies into `master_guidance`, assigns `TASK.md` to each worker, stops the swarm when done |
| Consult | `.agents/skills/consult/SKILL.md` | none (external API) | GPT-5.5-pro reads an elaboration and proposes the next strategy |
| Worker (7 per project) | `agents/contracts/worker.md` | `fact_submit`, memory, `fact_search`, arXiv search | proves lemmas round by round; each round is a fresh session that re-reads `TASK.md` |
| Verifier | `agents/contracts/verifier.md` | arXiv search, web search | stateless judge for each `fact_submit`: "The fact is written to the fact graph iff you return `"correct"`." |
| Paper roles | `agents/skills/write-paper/roles/` | none (one-shot, no filesystem) | writer, planner, section writer, reviser, math verifier, reference auditor and verifier; they turn verified facts into an amsart paper |

**How they work together.**
- **Memory:** there are three tiers. Each worker has private notes. Global memory holds shared conclusions, dead ends, guidance and every verification verdict. The content-addressed fact graph is the only source of truth.
- **Strategy:** the main agent publishes an elaboration and consults GPT-5.5-pro, then reassigns workers from the reply, about every two hours.
- **Proving:** a worker calls `fact_submit`, which spawns the verifier. If it rejects the fact, the worker repairs it from the repair hints and resubmits.
- **Finishing:** the operator finalizes a project by naming the fact that proves the target. The paper pipeline then writes, compiles, audits references and re-verifies the whole paper.
- **Linalg run:** Aug 21 to Sep 9. Twelve projects made facts (p3a led with 705), and three were finalized.
- **Solveall run:** started Sep 9 but only the first 4 of 53 projects ran, and it stopped by Sep 14.

**Export.** `~/shrd/Danus/runtime/exports/sft_trajectories.jsonl` holds 33,174 of 33,776 candidate records, 3.91B tokens.
- **Role field:** `metadata.role`, taken from the session's working directory.
- **Subagents:** included. `metadata.agent` is `main` or `agent-N`.
- **Most drops are model errors:** arguments passed as strings instead of arrays, invented arguments, repetition loops.

| Role | Records | Tokens | Mean |
|---|---|---|---|
| verify | 18,520 | 1.40B | 75.6k |
| worker | 14,571 | 2.50B | 171.7k |
| authoring | 61 | 5.0M | 81.7k |
| main | 13 | 0.3M | health pings only |
| other | 9 | 0.25M | probes |

**Examples**

Main agent, **not in the export**. Raw session `~/.kimi-code/sessions/wd_danus_a9bc6a6918dd/session_d692724d-…/agents/main/wire.jsonl`, which opens with "I wish to use Danus to solve the linalg problems I previously gave to Rethlas":

```text
[assistant] Now the strategic cycle. Checking whether the first array tasks started, then
         building the p2a elaboration.
         → Bash(squeue -j 2197712 …; bin/danus list | head -6)
[tool]   2197712_0  R  1:28  1 fs-mbz-gpu-335 …
[assistant] Writing the p2a initial elaboration per the five-section template, with honest
         empty states and the draft's literature context placed in §0/§3/§4.
         → Write(runtime/projects/p2a-gecp-growth-polynomial-upper-bound/strategy/
           elaboration-000-initial.md: "# Elaboration — p2a … ## 0. Mathematical verdict
           **Not solved.** …")
         → mcp__danus__gm_add(kind: elaboration, claim: "**Not solved.** Project start (no
           verified facts): goal fixed — prove GECP growth g(n) ≤ C·n^C or any n^{o(ln n)}
           bound; main blocker = no known machinery forces sublinear log-exponent
           accumulation along complete-pivoting trajectories …")
[tool]   {"id": "5aa37358379b7f69", "kind": "elaboration"}
[assistant] p2a elaboration published (`5aa37358379b7f69`). Launching its strategy consult in
         the background, then writing the p5b elaboration.
         → Bash(bin/consult --file …/elaboration-000-initial.md --out …/consult-reply-001.md
           --effort high)
```

Worker `high2` on `p5a-matvec-query-complexity-low-rank`, `session_ef0570e4-…` (131k tokens):

```text
[user]   You are worker 'high2' on project 'p5a-matvec-query-complexity-low-rank'. Continue
         solving the problem (this is a continuation round, not a fresh start).
         1. Read TASK.md — your current assignment … 2. Follow AGENTS.md (worker.md) exactly …
  …
[assistant] Now submitting the extraction brick — statement and proof written for strict
         verification.
         → mcp__danus__fact_submit(statement: "(Lemma RankK_Schatten_extraction — two-sided
           Ritz pinching: the exact rank-k analog of BN23's rank-1 Schatten-p conversion,
           arXiv:2304.03191 Lemmas 7.5+7.6, for all p >= 1.) NOTATION. All matrices and
           vectors are real. …", …)
[tool]   {"accepted": true, "fact_id": "264b9c7770527f67",
          "undefined_symbols": ["(k,r)", "B_{11}", "B_{22}", "I_m", …]}
```

Verifier, `session_470a49f3-…` (33k tokens):

```text
[user]   Run_id: 20260821T221725Z_094ea436043f. Statement: Lemma (Schur-complement entries are
         ratios of minors). Let n ≥ 1 and 0 ≤ k < n be integers and let M ∈ R^{n×n}. …
[assistant] I'll verify this proof following the AGENTS.md workflow, starting with the
         required skills.  → Skill(verify-sequential-statements)
[assistant] → Skill(check-referenced-statements)
  …
[assistant] Verification complete — details below; now writing the final JSON to the
         specified path.  → Write(runtime/verify-runs/20260821T221725Z_094ea436043f/
         verification.json)
[assistant] Verification finished. The proof was checked statement by statement in textual
         order: the block-form identification … is correct …, the block Gaussian
         factorization in the claim checks out by direct multiplication of all four blocks …
```

Paper writer, `session_abb61269-…`. This is a single turn: the whole contract and the facts are pasted into the prompt, and the answer is the paper.

```text
[user]   You are the PAPER WRITER. Everything you need is embedded below; you have no
         filesystem to read. Produce a single complete main.tex per the contract and role
         prompt. ===== BEGIN AGENTS.md ===== # AGENTS.md — the standing contract for the
         paper agent …
[assistant] \documentclass[12pt]{amsart}
         \usepackage{amsfonts,amssymb,amsthm,mathtools,enumitem} … \newtheorem{thm}{Theorem}[section] …
```

## How the five compare

**What checks the work:**
- **arxivmath:** only other LLMs (a verifier, then Opus reading the full paper).
- **arxivlean:** the Lean compiler checks the proof, and LLM judges check that the statement is faithful.
- **repoprover:** `lake build` plus two LLM reviewers.
- **Rethlas and Danus:** an LLM verifier, run fresh each time, with an explicit verdict schema.

**What becomes a training record:**
- **arxivmath:** a question/answer pair.
- **arxivlean:** one full proof-search trajectory.
- **repoprover, Rethlas and Danus:** one session per role, so a single task is spread across many records.

**Where the role signal lives:**
- `source.agent_type` (repoprover)
- `lane` (Rethlas)
- `metadata.role` (Danus)

**Known gaps:**
- arxivlean's gate drops about 40% of correct proofs.
- Rethlas is solveall only, and its verifier data is dominated by one problem.
- Danus has no orchestrator or consult data.
- repoprover's export doesn't record which model generated it.
