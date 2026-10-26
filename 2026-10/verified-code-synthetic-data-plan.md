---
title: Verified code synthetic data plan
description: Plan to extend the code_prompts/code_solutions pipeline with VeriBench-style Lean artifacts — shallow-embedded implementations, specs, and proofs of outputs, loop invariants and running time
date: 2026-10-25
---

A plan to extend the [`code_prompts` pipeline](synthetic-code-prompts-pipeline.md) in LLM360/synthetic-data-bbq with a formalization and verification stage: for each `code_solutions` solution, produce a Lean 4 artifact in the [VeriBench](https://cs.stanford.edu/people/brando9/veribench/blog/veribench-launch) shape (implementation, tests, pre/post, property theorems, imperative twin, equivalence), then prove properties of its outputs, intermediate states and running time, in the spirit of [Anthropic's formal verification work](https://www.anthropic.com/research/formal-verification). Every artifact the new stage keeps is checked by Lean, so the design goal is yield per proof token, not rows.

Revised Oct 26: the first draft compiled solutions through [Algo2Lean](https://github.com/lunjiah/algo2lean)'s typed Python-like subset. That tied the pipeline to a subset and to low-level PC-stepping proofs; the plan now follows VeriBench's shallow embedding (the LLM writes the Lean `def` directly), and what the compiler used to give for free — termination, intermediate states, cost counters — is recovered by construction rules below.

## What exists today

- `code_prompts` records "meta-prompt → problem" (27.8M rows kept of 29.9M, gpt-oss-120b); `code_solutions` records "problem → solution". Each problem is grounded in one of 1,304 reference implementations (TheAlgorithms/Python + keon/algorithms), and the output rows carry the concept name in the `behavior` field.
- The `all_knobs` variant can emit explicit constraints, starter code and tests with the problem; the base variant pins everything to vague.
- Lean infrastructure from arxivlean (see [math-sft-data-pipelines.md](math-sft-data-pipelines.md)): a prover agent (K3) with `verify_lean`, `loogle` and `leanfinder`, Lean/Mathlib via lean-lsp-mcp, a gated construction pipeline where every gate requires an explicit keep from every earlier gate, and the rollouts record format with an SFT gate.

## Design choice: VeriBench's shallow embedding, with gates in place of the human curator

Three design points were considered:

| | Who defines semantics | What the LLM writes | Cost |
|---|---|---|---|
| Algo2Lean | a compiler from a typed Python-like subset (`.algo`) | only proofs | subset restriction; proofs step through generated PCs; a second trusted component (the compiler) |
| Anthropic/Theorem | ISA + OS semantics | proofs, and patches to the code when a proof fails | binary-level; not applicable to Python |
| **VeriBench / Verina** | the LLM (shallow embedding, Lean `def` over `List`/`Array`/`Int`) | impl + tests + pre/post + theorems + imperative twin + proofs | nothing is free: termination, invariants and cost must be built in; "compiles but `sorry`" and trivial specs dominate (theorem coverage ≤ 0.16 for Codex and Claude Code) |

Decision: **VeriBench's artifact shape, no language subset, differential testing as the gate on the implementation, and mechanical gates (mutation, no-`sorry`, no `partial`) in place of VeriBench's human curator.** What's gained: any Python the model can express in Lean is in scope; proofs are high-level (`simp`, `omega`, induction on lists) and reuse Mathlib's `List.Sorted`/`List.Perm` library; one Lean toolchain (arxivlean's). What's lost and must be rebuilt: a compiler no longer defines what the Lean means, so fidelity to the Python rests on the differential test; termination, intermediate states and running time become construction rules rather than compiler outputs.

VeriBench facts (verified from the `veribench@1.0` dataset in `brando90/harbor-datasets`, 884 tasks, Lean 4.22.0 + Mathlib):

- The task prompt mandates a file order: `import Mathlib`, docstring, namespace, functional implementation, `example : … := by native_decide` tests plus `#eval`, `def Pre`, property `def <name>_prop` / `theorem <name>_thm` pairs, `def Post_prop` as a conjunction of the props, `theorem main_correctness_thm : Pre → Post_prop`, imperative implementation with `Id.run do` and mutable state, imperative tests, equivalence theorem functional = imperative.
- Loops are **fuelled**: `binarySearchAux arr target fuel left right` with `fuel := arr.length.succ`, returning `none` when fuel runs out; the completeness lemma carries an explicit fuel-adequacy hypothesis (`right + 1 - left ≤ fuel`).
- The imperative twin is `forIn` over `List.replicate fuel 0` tokens with a factored-out step function `binarySearchStep : state → Id (ForInStep state)` on an explicit state tuple (`Nat × Nat × Option Nat`); the equivalence proof is induction on fuel relating the loop to the functional aux.
- Construction was o3 draft → human curator against a rubric → kernel; the human sign-off is what this plan replaces.
- Types: VeriBench's gold uses `List Nat` for Python `List[int]`; for our purposes Python `int` maps to `Int`, and the semantic judge must check the mapping (see gates).

## Construction rules (what the compiler used to provide)

- **Termination.** Two admissible forms: well-founded recursion (`termination_by` / `decreasing_by`, checked by the kernel at definition time — termination is then free), or VeriBench-style fuel with a required **fuel-adequacy theorem** (`∀ f ≥ F(n), impl_fuel f = impl_fuel (F n)`, i.e. the result stabilizes). `partial def`, `unsafe`, and `Classical.choice`-based escapes are rejected by the gate. Without this rule a fuelled definition hides non-termination as `none`, the same vacuity the compiler-based design had.
- **Intermediate states.** The imperative twin must factor its loop body into a named step function on an explicit state tuple (as VeriBench's gold does). A loop invariant is then three theorems: `inv_init : Inv init`, `step_preserves : Pre → Inv s → Inv (step s)`, `inv_exit : Inv s → ¬ guard s → Post s`. These are what "proofs about intermediate states" mean in a shallow embedding.
- **Running time.** No clocks exist, so one of: (a) a cost-instrumented twin returning `(result, cost)` with `cost_result : (implCost x).1 = impl x` and `running_time : (implCost x).2 ≤ f(n)`; (b) for fuelled definitions, the fuel-adequacy theorem at `F(n) = f(n)` *is* the running-time bound in iterations and costs nothing extra; (c) a `StateT Nat Id` twin with `modify (· + 1)` per charged operation when the cost model needs per-operation ticks. Default: (b) where the loop is fuelled, (a) otherwise.
- **Type mapping**, fixed in the prompt and checked by the judge: `int → Int`, `List[int] → List Int` (or `Array Int` for index-heavy code), `Optional[T] → Option T`, `str → String`, `dict → Std.HashMap` or association list, exceptions → `Except String α` or `Option`, classes → `structure`. Floats, I/O and reflection are out of scope; the rejection reason is recorded.

## Stages

Fits the existing slice/SLURM/vLLM shape: one job per slice, skip slices whose output exists.

1. **Select or steer for formalizability.** Filter on `behavior`: `sorts`, `searches`, `data_structures`, `dynamic_programming`, `graphs`, `maths`, `strings` are the core; skip `web_programming`, `computer_vision` and the like. Add one diversity profile to `synthetic_problem_generator.py` ("verifiable": pure function, typed signature over ints/lists/strings, no I/O or floats, the problem states 2–3 properties the output must satisfy). It's one more config, not a new generator.
2. **Specs from the problem, not the solution.** A spec derived from the solution is circular. `Pre`, the `_prop`s and `Post_prop` come from the problem statement and its tests, written against the signature only; the `all_knobs` tests are themselves a spec ("every test passes"), and "terminates and never throws" is a generic property provable for every problem.
3. **Lean implementation of the solution.** The LLM writes the functional implementation and the imperative twin from the Python, under the construction rules. Gate: compiles, no `partial`/`unsafe`, and **differential testing** — Python vs Lean (`#eval`, or compiled; Lean compiles to native) on generated inputs plus adversarial edge cases (empty, negatives, duplicates, boundaries). It is the only check that the Lean thing *is* the solution.
4. **Tiered properties**, so yield can be measured and the budget cut where it stops paying: T0 unit tests as `native_decide` examples; T1 property theorems + `Pre → Post_prop` **plus termination** (well-founded, or fuel adequacy); T2 the imperative twin's equivalence theorem and loop invariant (`inv_init`, `step_preserves`, `inv_exit`); T3 running time.
5. **Prove** with the arxivlean prover agent and tooling; the trajectory is the record.
6. **Patch loop.** When a proof fails on a real bug, the model patches the Python solution, the Lean is regenerated, and proving resumes (Anthropic's loop). Rejected and patched solutions are both kept: rejects go to pre-training with the rejection reason as a label.

**Gates**, each requiring an explicit keep from every earlier gate: compiles against the pinned toolchain; no `partial`/`unsafe`; differential test; no `sorry`; `#print axioms` shows only `propext`, `Quot.sound`, `Classical.choice`; termination theorem present (or `termination_by` in the definition); **spec non-triviality by mutation** — a buggy variant of the solution must be rejected by the spec, checked mechanically as a concrete counterexample `example : ¬ <prop> mutant input := by native_decide`; semantic-faithfulness judge in the `semantic_judge.md` pattern ("Lean states the same property, neither weaker nor stronger; the type mapping preserves the Python semantics; if unsure, discard"). The mutation gate targets VeriBench's failure mode where artifacts compile but say nothing.

## The concept taxonomy as a proof library

Every problem is grounded in one of 1,304 reference implementations. Formalize the references first (1,304 VeriBench-shape artifacts with T1–T3 proofs, a one-time bounded cost) as a Lake package, then problem-level proofs import those definitions and lemmas (`Sorted`, `Perm`, interval lemmas, invariant templates per algorithm family) alongside Mathlib. Anthropic measured 17% fewer tokens with a shared proof workspace and agents succeeding after solo failures; the taxonomy supplies that sharing structure. It also gives a curriculum: problem proofs within a concept should get cheaper as the concept's library fills in. Measure that in the pilot.

## Records

All five are kept. A, B and E are single-turn pairs (the `{"text", "token_count"}` shape); C and D are agent trajectories (the rollouts shape), so the SFT gate must accept both.

| record | teaches | shape | admitting gate |
|---|---|---|---|
| A: problem → `Pre`/`_prop`s/`Post_prop` | specification writing | pair | compiles · semantic judge · mutation check |
| B: Python solution → functional impl + imperative twin | code autoformalization | pair | compiles · no `partial` · differential test |
| C: (impl, spec) → proof trajectory | proving | trajectory | no `sorry` · axioms · termination |
| D: problem → full VeriBench artifact | end-to-end verified code generation | trajectory | all of the above |
| E: failed proof → patched solution → proof | verification-guided debugging | pair or short trajectory | patched solution passes C's gates and the original tests |

Running example (Lean is schematic in VeriBench's file order, not compiled). Concept `searches/binary_search.py`; problem: *given a non-decreasing list `a` of integers and an integer `t`, return the smallest index `i` with `a[i] ≥ t`, or `len(a)` if none.*

- **A.** Prompt: problem + the signature `lowerBound : List Int → Int → Nat`; the solution is not shown. Response:

  ```lean
  def Pre (a : List Int) (_t : Int) : Prop :=
    ∀ i j (hi : i < a.length) (hj : j < a.length), i ≤ j → a[i] ≤ a[j]
  def below_prop (a : List Int) (t : Int) : Prop :=
    ∀ i (h : i < a.length), i < lowerBound a t → a[i] < t
  def at_or_above_prop (a : List Int) (t : Int) : Prop :=
    ∀ h : lowerBound a t < a.length, t ≤ a[lowerBound a t]
  def in_range_prop (a : List Int) (t : Int) : Prop := lowerBound a t ≤ a.length
  def Post_prop (a : List Int) (t : Int) : Prop :=
    in_range_prop a t ∧ below_prop a t ∧ at_or_above_prop a t
  ```

  Mutation check: `below_prop` rejects the "upper bound" mutant — `example : ¬ below_prop' [5] 5 := by native_decide` where the mutant returns 1.
- **B.** Prompt: problem + the Python solution (`lo, hi = 0, len(a); while lo < hi: mid = (lo+hi)//2; if a[mid] < t: lo = mid+1 else: hi = mid; return lo`). Response, functional implementation by well-founded recursion and the imperative twin with a factored step:

  ```lean
  def lowerBoundAux (a : List Int) (t : Int) (lo hi : Nat) : Nat :=
    if h : lo < hi then
      let mid := lo + (hi - lo) / 2
      if a[mid]! < t then lowerBoundAux a t (mid + 1) hi else lowerBoundAux a t lo mid
    else lo
  termination_by hi - lo
  def lowerBound (a : List Int) (t : Int) : Nat := lowerBoundAux a t 0 a.length

  abbrev SearchState := Nat × Nat   -- (lo, hi)
  def step (a : List Int) (t : Int) (_ : Nat) (s : SearchState) : Id (ForInStep SearchState) :=
    if s.1 < s.2 then
      let mid := s.1 + (s.2 - s.1) / 2
      pure (.yield (if a[mid]! < t then (mid + 1, s.2) else (s.1, mid)))
    else pure (.done s)
  def lowerBoundImp (a : List Int) (t : Int) : Nat := Id.run do
    let s ← forIn (List.replicate (a.length + 1) 0) (0, a.length) (step a t)
    return s.1
  ```

  Metadata: compiles; differential test on 2,000 random sorted inputs plus edge cases (empty list, all-equal, `t` below/above every element, negatives), Python == Lean.
- **C.** Statements, one file per problem so the invariant is visibly reused:

  ```lean
  -- T1
  theorem main_correctness_thm (a : List Int) (t : Int) (hPre : Pre a t) : Post_prop a t
  -- termination is discharged by `termination_by` in the definition

  -- T2: equivalence and loop invariant over the factored step
  def Inv (a : List Int) (t : Int) (s : SearchState) : Prop :=
    s.1 ≤ s.2 ∧ s.2 ≤ a.length ∧ (∀ i (h : i < a.length), i < s.1 → a[i] < t)
      ∧ (∀ i (h : i < a.length), s.2 ≤ i → t ≤ a[i])
  theorem inv_init (a : List Int) (t : Int) : Inv a t (0, a.length)
  theorem step_preserves (a : List Int) (t : Int) (s : SearchState) (hPre : Pre a t)
      (h : Inv a t s) : ∀ s', step a t 0 s = pure (.yield s') → Inv a t s'
  theorem inv_exit (a : List Int) (t : Int) (s : SearchState) (h : Inv a t s)
      (hstop : ¬ s.1 < s.2) : Post_prop_at a t s.1
  theorem equivalence_thm (a : List Int) (t : Int) : lowerBound a t = lowerBoundImp a t

  -- T3: running time as fuel adequacy (the loop stabilizes after ⌈log₂ n⌉ + 1 iterations)
  theorem running_time (a : List Int) (t : Int) (f : Nat) (hf : Nat.log 2 a.length + 1 ≤ f) :
      (Id.run do let s ← forIn (List.replicate f 0) (0, a.length) (step a t); return s.1)
        = lowerBound a t
  ```

  The record is the prover's full trajectory: `verify_lean` attempts, `loogle`/`leanfinder` lookups, imports from the concept library, ending in a compiled file with no `sorry`.
- **D.** Same content as A + B + C in one trajectory, starting from the problem alone; the model also writes the code. The Lean artifact may diverge from the `code_solutions` output; the differential test is then against the problem's tests.
- **E.** Suppose the sampled solution had `if a[mid] <= t:`. Tests without an exact hit pass and the differential test passes (Python and Lean agree, both wrong), but the prover gets stuck at `⊢ a[i] < t` with `a[i] ≤ t` in hand. Prompt: problem + spec + implementation + the stuck goal. Response: diagnosis (advances past elements equal to `t`, computes the upper bound; counterexample `a=[5], t=5 → 1`, expected 0), patch `<`, re-run closes `main_correctness_thm`. Metadata: `bug_class = off-by-one on equality`, `found_by = proof failure`.

## Pilot

Details to be decided. Shape: 3 concepts × 1k problems (`sorts`, `searches`, `dynamic_programming`), run every stage, fill in the gate table, and measure per-concept proof cost over time (does the library effect show up?).

| gate | in | kept | drop reason breakdown |
|---|---|---|---|
| formalizable (`behavior` filter / verifiable profile) | | | |
| implementation compiles, no `partial`/`unsafe` | | | |
| differential test | | | |
| spec: compiles · judge · mutation | | | |
| T0 tests | | | |
| T1 `Pre → Post_prop` + termination | | | |
| T2 equivalence + invariant | | | |
| T3 running time | | | |
| patch loop (E rows produced) | | | |

## Risks and open questions

- **Fidelity rests on the differential test.** With no compiler, the Lean implementation can diverge from the Python in corner cases the random inputs miss (`Nat` vs `Int`, floor division of negatives, exceptions vs `Option`). Mitigations: fixed type mapping in the prompt, adversarial edge-case generators per type, and the judge's type-mapping check. Measure the residual by seeding known-divergent translations.
- **Type-mapping rejection rate** is unknown; acceptable, since rejects stay in pre-training, but the reason should be recorded.
- **Proof cost:** 27.8M problems × 10⁵–10⁸ proof tokens is not a plan; the pilot sets the budget, and the library effect decides how far it stretches. VeriBench's numbers (no-`sorry` rate ≤ 0.28 for frontier agents) say T1 yield will be low at first.
- **Trusted base:** the Lean kernel, the pinned Mathlib, and the LLM judge on spec faithfulness. Mutation checks and differential tests bound the judge; nothing else is trusted.
- **T2/T3 shape:** the factored-step rule and fuel-adequacy rule are conventions the generator must follow; decide after the pilot whether invariants are proposed by the prover or by a separate invariant stage (a new, trainable task on its own).
- **Toolchain:** pin to arxivlean's Lean/Mathlib (v4.29.0) rather than VeriBench's 4.22.0; `import Mathlib` in full is slow to elaborate, so the concept library should re-export a narrow import set.

## Related work

- [VeriBench](https://cs.stanford.edu/people/brando9/veribench/blog/veribench-launch) — 884 Python-to-Lean tasks (dataset in `brando90/harbor-datasets`), agentic with verifier feedback; defines the artifact shape this plan adopts and the failure modes the gates target (frontier agents compile everything but capture the right theorems ≤ 16% of the time).
- [Verina](https://github.com/sunblaze-ucb/verina) — 189 hand-curated Lean tasks (description, code, pre/post, proof, tests); best model 3.6% proof success single-shot.
- FVAPPS — thousands of machine-generated Lean problems from APPS with `sorry`'d theorems; scale without checked proofs.
- [BRIDGE](https://arxiv.org/abs/2511.21104) — code-first prompting across code/spec/theorem; SFT on its traces gives ~1.5× Lean pass rate over code-only SFT, evidence that records A–D are learnable.
- Anthropic/Theorem OSS-Fuzz proofs — tests-as-specs, patch-then-prove, and proof reuse; the three ideas this plan borrows.
- [Algo2Lean](https://github.com/lunjiah/algo2lean) — the alternative considered: compiler-defined semantics for a typed Python-like subset with named lines and cost clocks. Rejected for the subset restriction; its `tick`/`@name` ideas survive as the cost-twin and factored-step rules.
- The gap: nobody pairs a concept-grounded problem generator with VeriBench-shape artifacts, required termination and running-time theorems, and a patch loop at pipeline scale.
