---
title: RealBench — vericoding with a harness-owned bridge
description: Design for a code-verification benchmark that improves on VeriBench — the agent writes Rust plus spec plus proof in one loop, while the harness derives the formal model (Charon+Aeneas → Lean) and owns the gold spec
date: 2026-10-28
---

Design discussion for a benchmark to replace [VeriBench](https://huggingface.co/datasets/brando/veribench) as the thing evaluated when measuring end-to-end code verification. Working draft lives at `~/veribench2/DESIGN.md`; relates to the [verified code synthetic data plan](verified-code-synthetic-data-plan.md), which consumes the same look.

## The defect being fixed

VeriBench pairs a Python program with a hand-written Lean artifact and verifies *the artifact*. Its own paper concedes the point ("verifies the translated Lean 4 artifact rather than the original Python source code"), and it deliberately uses a shallow embedding rather than formalising source semantics. The sharper statement: **the Python solution is not VeriBench's source of truth — the gold Lean file is.** Scoring is theorem coverage against that file, judged by an LLM (r=0.70 vs humans), so the benchmark measures *formalization similarity to a human translation*, not verification. Petting the fidelity gap properly requires a **mechanical, shared, versioned bridge**, never a per-task human rewrite; the rule that follows is that **trusted mass must be O(1) in the number of tasks**.

## Decided design

- **The agent writes program, spec and proof together**, one submission, one loop: edit Rust → re-run the bridge → read the derived model → write spec and proof → proof fails → change the program. Not staged into codegen/specgen/proofgen, because co-evolution measures a harder ability: WybeCoder reports 74% on VERINA with co-evolved code+invariants+proofs against 10–22% for staged proof generation.
- **The harness owns `⟦·⟧`.** The model is *generated per submission* from the agent's own program and is read-only on disk, regenerable only by changing the program and re-running the tool. If the agent can write or edit the model, the benchmark has VeriBench's hole plus a new one.
- **Gold spec `G` is a predicate on implementations**, `(Inputs → Outputs) → Prop`, harness-owned and hidden from the agent (otherwise spec synthesis is copy-paste). For single-valued problems it is *derived*, not authored: `G := fun f => ∀ x ∈ domain, f x = ⟦C_ref⟧ x`. Hand-written `G` is reserved for the multi-valued minority (ties, any-valid-ordering).
- **Adequacy is one ladder, not several metrics**: mutants refuted → `S_a ⟦C_ref⟧` → `S_a ⟹ G` (soundness) → `G ⟹ S_a` (completeness). Rung 2 is implied by rung 4 whenever `G ⟦C_ref⟧`, so the pointwise check is the cheap substitute when no `G` exists.
- **Gates vs scores**: compiling and passing the ported tests is a gate, not a score. Scored quantities are proof discharge (no `sorry`/`axiom`/`unsafe`/`implemented_by`, all-`Ok`, no `div`), two-sided adequacy, and a refutation family — give a buggy program and demand a counterexample witness that execution can check, with no judge anywhere in the accept path.
- **Refinement, not correctness.** Proving `impl ≈ ⟦C_ref⟧` buys bug-compatibility with the reference, not intent-fidelity. Say "refinement" in the paper.

## Language choice: Rust + Charon/Aeneas → Lean 4

The scarce resource is the **functionalizing compiler**, not the prover. Aeneas emits pure functional Lean *terms*, which is what lets `⟦C_ref⟧` exist and be quantified over; that one property carries derived `G` and the accepts-good half of adequacy.

- **Python** has no such bridge at all — that absence *is* VeriBench's hole. Building one is the months-long follow-up project.
- **OCaml** loses on one requirement: Cameleer emits WhyML *programs* (`let`), not logic-level `function`s, so two translations cannot be equated without first writing a spec against each. Deeper reason: Aeneas's functionalisation is sound *because the borrow checker licenses it*, and OCaml's refs/arrays/interior mutation are unconstrained. `OLang` does give a term-level denotation in Rocq but is a 2025 research artifact with no automation. OCaml would win if gold specs were accepted as hand-authored: strings translate (Aeneas cannot do `String` or string literals), SMT gives seconds-per-cycle latency, and Gospel's Ortac→Cameleer→CFML ladder is the best difficulty-tier design in this space.
- **C** via `clightgen`+VST has the best semantics and is a trap for a v1 timeline.
- **Lean** because Aeneas's author calls it "our main backend today", it is the most mature alongside HOL4, it ships `progress`/`step`/`scalar_tac` for monadic programs, encodes `U32` as `{x : Nat // x ≤ U32.max}` and `assert!` as `massert` (giving panic-freedom as an obligation), and Mathlib supplies `List.Perm`/`List.Sorted`/`Finset` for stating specs.

## Corrected requirement: uniform, not universal

An earlier draft required the bridge to work for *all* code in the source language. That is **wrong and had to be retracted**: no Rust→prover bridge is universal (Aeneas, Verus, Creusot, Prusti, hax, rocq-of-rust all have subsets), so a universality criterion discriminates between nothing. The requirement that matters is **uniformity** — a deterministic function of source with no per-program human modelling, *within a declared and published subset*.

The constraint lands asymmetrically: `C_ref` is authored in-subset by the benchmark author and confirmed by a bridge-acceptance gate (no human at agent time); `C_a` is free-form, so the subset must be **published to the agent** and rejections counted as `translation_rejected`, distinct from proof failure. Subset size is therefore a *measured* number ("of N candidate tasks, M were bridge-accepted"), not a claimed one.

## Corpus cost

Charon/Aeneas reject: `String` and string literals, `std::collections::HashMap` (no model at all), `vec![]`, `Drop`, GATs, `dyn Trait`, HRTB, `unsafe`, raw pointers, interior mutability, concurrency, I/O, `return` in nested loops, outer `break`/`continue`, `&mut` at a generic type. Calls into modelled-but-absent stdlib emit `FunsExternal.lean` templates that a human must fill — the O(1) trusted boundary, to be hash-pinned per task.

⇒ v1 filter is `i64`/`u64`/`bool`/`Vec<T>`/`&[T]`/`Vec<u8>` only. Loses roughly a third of HumanEval (strings, dicts; dict tasks are recoverable as `Vec<(K,V)>`, strings are not) and **all of MBPP** (references print rather than return, use `math` and `str.format`).

## Open questions

- 20-task pilot before authoring anything: bridge + `lake build` latency per loop iteration (go/no-go for co-evolution), legibility of the derived model, proof-to-code ratio on trivial functions, whether agents state `Sorted`/`Perm` unaided.
- Whether to publish the subset in each problem card (keeps "write verifier-friendly code" as a labelled skill) or pre-constrain signatures so idiomatic and submissive code coincide (cleaner proof-reading numbers).
- Authoring cost of hand-written `G` per task — if it is 10 minutes rather than an hour, Rust+Verus (identity bridge, full corpus, no kernel) becomes competitive.
- Saturation: HumanEval/MBPP are the most memorised and easiest verification targets (Dafny vericoding at 82%, DafnyBench 68%→96% in a year). Use as easy tier only; headline on real-repo functions.