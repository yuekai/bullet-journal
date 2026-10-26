---
title: Verified code synthetic data plan
description: Plan to extend the code_prompts/code_solutions pipeline with Lean formalization and proofs of outputs, intermediate states and running time, via Algo2Lean
date: 2026-10-25
---

A plan to extend the [`code_prompts` pipeline](synthetic-code-prompts-pipeline.md) in LLM360/synthetic-data-bbq with a formalization and verification stage: generate Lean definitions of each `code_solutions` solution, then prove properties of its outputs, intermediate states and running time, in the spirit of [Algo2Lean](https://www.algo2lean.com/current/) and [Anthropic's formal verification work](https://www.anthropic.com/research/formal-verification). Every artifact the new stage keeps is checked by Lean, so the design goal is yield per proof token, not rows.

## What exists today

- `code_prompts` records "meta-prompt → problem" (27.8M rows kept of 29.9M, gpt-oss-120b); `code_solutions` records "problem → solution". Each problem is grounded in one of 1,304 reference implementations (TheAlgorithms/Python + keon/algorithms), and the output rows carry the concept name in the `behavior` field.
- The `all_knobs` variant can emit explicit constraints, starter code and tests with the problem; the base variant pins everything to vague.
- Lean infrastructure from arxivlean (see [math-sft-data-pipelines.md](math-sft-data-pipelines.md)): a prover agent (K3) with `verify_lean`, `loogle` and `leanfinder`, Lean/Mathlib via lean-lsp-mcp, a gated construction pipeline where every gate requires an explicit keep from every earlier gate, and the rollouts record format with an SFT gate.

## Design choice: compiler-defined semantics, differential testing as the gate

Three design points were considered:

| | Who defines semantics | What the LLM writes | What comes for free |
|---|---|---|---|
| Algo2Lean | a compiler from a typed Python-like subset (`.algo`) | only proofs | output relations, named-line intermediate states, explicit cost counters (running time) |
| Anthropic/Theorem | ISA + OS semantics | proofs, and patches to the code when a proof fails | a generic spec ("the test suite always passes"), proof reuse across programs |
| VeriBench / Verina | the LLM (shallow embedding, Lean `def`) | impl + tests + pre/post + theorems + proofs | nothing — "compiles but `sorry`" and trivial specs dominate (theorem coverage ≤ 0.16 for Codex and Claude Code) |

Decision: **Algo2Lean where the solution fits its subset, shallow embedding as the fallback, and in both cases gate the Lean definition by differential testing against the original Python.** The compiler route is what makes intermediate-state and running-time theorems tractable; without cost counters, running time means a hand-rolled cost monad per problem.

Algo2Lean facts ([lunjiah/algo2lean](https://github.com/lunjiah/algo2lean), Apache 2.0):

- Headless CLI: `python3 -m algo2lean compile x.algo -o XGenerated.lean --check`; Python ≥ 3.9; Lean 4.33.1 pinned. Integer-only programs need no Mathlib; exact reals and randomized programs have optional Mathlib companions.
- Subset: Int, infinite mutable `Seq` (`Int → Int`, so `len(a)` becomes an explicit `n`), tuples, finite sets/dicts, classes, `randint`, `fork_join`, imports, `while`/`range` loops, recursion. Programs may diverge.
- `tick("clock", amount)` charges a named clock; `# @name` above a statement names the state before it and generates `f.At.name`, `f.Local.x` accessors in a separate `…Points.lean` file.
- Interface: `f.Returns input output` (a completed execution exists), `f.ReturnsWithCost input output costs`, `f.CallFrom state heap output` (local contracts from a named line).
- Caveats: proofs are low-level (the `sum_loop` example walks `Step.sum_to_pc4 → pc3 → …` by hand; the docs say "automatic invariant proofs are not provided"), so even trivial programs need long proofs. The compiler, not the kernel, is the trusted base for "this Lean means that `.algo`".
- **Divergence:** `f.Returns` is a relation; a nonterminating run satisfies it for no output. So `(run : f.Returns input r) → Post input r` and any `ReturnsWithCost` bound are vacuously true for an infinite loop. Termination (`∃ r, f.Returns input r`) must be a required theorem, as in the repo's merge-sort analysis (`terminates` + `every_output_correct`).

## Stages

Fits the existing slice/SLURM/vLLM shape: one job per slice, skip slices whose output exists.

1. **Select or steer for formalizability.** Filter on `behavior`: `sorts`, `searches`, `data_structures`, `dynamic_programming`, `graphs`, `maths`, `strings` are the core; skip `web_programming`, `computer_vision` and the like. Add one diversity profile to `synthetic_problem_generator.py` ("verifiable": pure function, typed signature over ints/lists/strings, no I/O or floats, the problem states 2–3 properties the output must satisfy). It's one more config, not a new generator.
2. **Specs from the problem, not the solution.** A spec derived from the solution is circular. Pre/Post come from the problem statement and its tests; the `all_knobs` tests are themselves a spec ("every test passes"), and "terminates and never throws" is a generic property provable for every problem.
3. **Lean definition of the solution.** (a) Canonicalize the `code_solutions` output into `.algo` (explicit `n`, named loop heads, one `tick` per iteration or call) and compile with `--check`; (b) else an LLM-written shallow-embedded Lean `def` with fuelled recursion. Gate for both: differential testing, Python vs Lean (`#eval` or compiled) on generated inputs plus edge cases. It is the only check that the Lean thing *is* the solution.
4. **Tiered properties**, so yield can be measured and the budget cut where it stops paying: T0 unit tests as `decide`/`native_decide`; T1 output properties (Post) **plus termination**; T2 intermediate state (loop invariants at `@name` lines, stated as local contracts `f.CallFrom`); T3 running time (`costs "clock" ≤ f(n)` via `ReturnsWithCost`).
5. **Prove** with the arxivlean prover agent and tooling; the trajectory is the record.
6. **Patch loop.** When a proof fails on a real bug, the model patches the solution, the Lean is regenerated, and proving resumes (Anthropic's loop). Rejected and patched solutions are both kept: rejects go to pre-training with the rejection reason as a label.

**Gates**, each requiring an explicit keep from every earlier gate: `compile --check`; differential test; compiles with no `sorry`; `#print axioms` shows only the standard axioms; `terminates` present; spec non-triviality by mutation (a buggy variant of the solution must be rejected by the spec: tests fail or the theorem is unprovable); semantic-faithfulness judge in the `semantic_judge.md` pattern ("Lean states the same property, neither weaker nor stronger; if unsure, discard").

## The concept taxonomy as a proof library

Every problem is grounded in one of 1,304 reference implementations. Prove the references first (1,304 Algo2Lean compilations plus T1–T3 proofs, a one-time bounded cost), then problem-level proofs import those lemmas. Anthropic measured 17% fewer tokens with a shared proof workspace and agents succeeding after solo failures; the taxonomy supplies that sharing structure, and Algo2Lean's low-level proofs make it necessary. It also gives a curriculum: problem proofs within a concept should get cheaper as the concept's library fills in. Measure that in the pilot.

## Records

All five are kept. A, B and E are single-turn pairs (the `{"text", "token_count"}` shape); C and D are agent trajectories (the rollouts shape), so the SFT gate must accept both.

| record | teaches | shape | admitting gate |
|---|---|---|---|
| A: problem → Lean spec | specification writing | pair | compiles · semantic judge · mutation check |
| B: Python solution → `.algo` + generated Lean | code autoformalization | pair | `compile --check` · differential test |
| C: (definition, spec) → proof trajectory | proving | trajectory | no `sorry` · axioms · `terminates` |
| D: problem → impl + spec + proofs | end-to-end verified code generation | trajectory | all of the above |
| E: failed proof → patched solution → proof | verification-guided debugging | pair or short trajectory | patched solution passes C's gates and the original tests |

Running example (Lean is schematic, written against Algo2Lean's interface names, not compiled). Concept `searches/binary_search.py`; problem: *given a non-decreasing sequence `a` of `n` integers and an integer `t`, return the smallest index `i` in `[0, n)` with `a[i] ≥ t`, or `n` if none.*

- **A.** Prompt: problem + the `.algo` signature `lower_bound(a: Seq, n: Int, t: Int) -> Int`; the solution is not shown. Response:

  ```lean
  def Sorted (a : Seq) (n : Int) : Prop := ∀ i j, 0 ≤ i → i ≤ j → j < n → a i ≤ a j
  def Pre  (a : Seq) (n t : Int)   : Prop := 0 ≤ n ∧ Sorted a n
  def Post (a : Seq) (n t r : Int) : Prop :=
    0 ≤ r ∧ r ≤ n ∧ (∀ i, 0 ≤ i → i < r → a i < t) ∧ (r < n → t ≤ a r)
  ```

  Mutation check: Post rejects the "upper bound" mutant (`a=[5], n=1, t=5` returns 1, fails `a 0 < 5`).
- **B.** Prompt: problem + the Python solution (`lo, hi = 0, len(a); while lo < hi: mid = (lo+hi)//2; if a[mid] < t: lo = mid+1 else: hi = mid; return lo`). Response:

  ```text
  def lower_bound(a: Seq, n: Int, t: Int) -> Int:
      lo: Int = 0
      hi: Int = n
      # @loop
      while lo < hi:
          tick("lower_bound")
          mid: Int = lo + (hi - lo) // 2
          if a[mid] < t:
              lo = mid + 1
          else:
              hi = mid
      return lo
  ```

  Metadata: `compile --check` ok; differential test on 2,000 random sorted inputs plus edge cases, Python == Lean.
- **C.** Statements, one file per problem so the T2 lemma is visibly reused:

  ```lean
  theorem every_output_correct (a : Seq) (n t r : Int) (h : Pre a n t)
      (run : lower_bound.Returns (a, n, t) r) : Post a n t r
  theorem terminates (a : Seq) (n t : Int) (h : Pre a n t) :
      ∃ r, lower_bound.Returns (a, n, t) r
  theorem loop_contract (s : Configuration) (a : Seq) (n t lo hi : Int)
      (at_loop : lower_bound.At.loop s)
      (hlo : lower_bound.Local.lo s = some lo) (hhi : lower_bound.Local.hi s = some hi)
      (inv : 0 ≤ lo ∧ lo ≤ hi ∧ hi ≤ n ∧ (∀ i, 0 ≤ i → i < lo → a i < t)
               ∧ (∀ i, hi ≤ i → i < n → t ≤ a i)) :
      ∃ r, lower_bound.CallFrom s s.heap r ∧ Post a n t r
  theorem running_time (a : Seq) (n t r : Int) (costs : Clocks) (h : Pre a n t)
      (run : lower_bound.ReturnsWithCost (a, n, t) r costs) :
      costs "lower_bound" ≤ Nat.log 2 n.toNat + 1
  ```

  The record is the prover's full trajectory: `verify_lean` attempts, `loogle`/`leanfinder` lookups, imports from the concept library, ending in a compiled file with no `sorry`.
- **D.** Same content as A + B + C in one trajectory, starting from the problem alone; the model also writes the code. The Lean artifact may diverge from the `code_solutions` output; the differential test is then against the problem's tests.
- **E.** Suppose the sampled solution had `if a[mid] <= t:`. Tests without an exact hit pass and the differential test passes (Python and Lean agree, both wrong), but the prover gets stuck at `⊢ a i < t` with `a i ≤ t`. Prompt: problem + spec + `.algo` + the stuck goal. Response: diagnosis (advances past elements equal to `t`, computes the upper bound; counterexample `a=[5], n=1, t=5 → 1`, expected 0), patch `<`, re-run closes `every_output_correct`. Metadata: `bug_class = off-by-one on equality`, `found_by = proof failure`.

## Pilot

Details to be decided. Shape: 3 concepts × 1k problems (`sorts`, `searches`, `dynamic_programming`), run every stage, fill in the gate table, and measure per-concept proof cost over time (does the library effect show up?).

| gate | in | kept | drop reason breakdown |
|---|---|---|---|
| formalizable (`behavior` filter / verifiable profile) | | | |
| `.algo` canonicalization + `compile --check` | | | |
| differential test | | | |
| spec: compiles · judge · mutation | | | |
| T0 tests | | | |
| T1 Post + `terminates` | | | |
| T2 loop contract | | | |
| T3 running time | | | |
| patch loop (E rows produced) | | | |

## Risks and open questions

- **Subset mismatch:** `code_solutions` outputs are arbitrary Python; the canonicalization rejection rate is unknown. Acceptable — rejects stay in pre-training — but the rejection reason should be recorded.
- **Proof cost:** 27.8M problems × 10⁵–10⁸ proof tokens is not a plan; the pilot sets the budget, and the library effect decides how far it stretches.
- **Trusted base:** the Algo2Lean compiler (its semantics for the `.algo` subset) and the LLM judges on spec faithfulness. Mutation checks and differential tests bound the second; nothing bounds the first except the compiler's own tests.
- **T2/T3 yield:** likely low at first; Algo2Lean's named-line proofs are step-by-step. Decide after the pilot whether T2 is generated by the prover or by a separate invariant-proposal stage (a new, trainable task on its own).
- **Toolchains:** Algo2Lean pins Lean 4.33.1; arxivlean runs Mathlib v4.29.0. Two toolchains on the cluster is acceptable.

## Related work

- [Verina](https://github.com/sunblaze-ucb/verina) — 189 hand-curated Lean tasks (description, code, pre/post, proof, tests); best model 3.6% proof success single-shot. Defines the artifact schema.
- [VeriBench](https://cs.stanford.edu/people/brando9/veribench/blog/veribench-launch) — 884 Python-to-Lean tasks, agentic with verifier feedback; shows frontier agents compile everything but capture the right theorems ≤ 16% of the time. Defines the failure modes the gates target.
- FVAPPS — thousands of machine-generated Lean problems from APPS with `sorry`'d theorems; scale without checked proofs.
- [BRIDGE](https://arxiv.org/abs/2511.21104) — code-first prompting across code/spec/theorem; SFT on its traces gives ~1.5× Lean pass rate over code-only SFT, evidence that records A–D are learnable.
- Anthropic/Theorem OSS-Fuzz proofs — tests-as-specs, patch-then-prove, and proof reuse; the three ideas this plan borrows.
- The gap: nobody pairs a concept-grounded problem generator with compiler-defined semantics, running-time theorems and a patch loop at pipeline scale.
