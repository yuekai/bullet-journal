---
title: How Danus makes incremental progress
description: How Danus (frenzymath's agent system for mathematical proof search) breaks a hard open problem into verified facts, how agents are steered, and whether they are handed easier versions of the problem
date: 2026-10-02
---

[Danus](https://github.com/frenzymath/Danus) takes one hard problem per project and makes progress by growing a **fact graph**: a shared set of small statements, each with a proof that cites earlier facts by id. This note is based on the kimi-orchestrator deployment on m2 (`~/Danus`): its docs (`docs/concepts.md`), its agent instructions (`agents/contracts/worker.md`, `.agents/skills/elaboration/SKILL.md`, `agents/contracts/main_agent.md`), and the run records of the linalg project `p3b-worst-case-vs-ideal-gmres`.

## The unit of progress: a verified fact

- A fact enters the graph only through `fact_submit`, and only if a fresh verifier instance returns `correct`. The verifier is an LLM (kimi), not a formal proof checker.
- A worker submits a claim, gets back a verdict with repair hints, revises, and resubmits until it passes. Every verdict is recorded in shared memory, so workers learn from each other's rejections.
- Proofs may build only on facts. Shared but unchecked findings (`global_memory`) are for awareness only, never building blocks.
- The final answer is just one more fact, resting on that chain. Scale: p3a ended with 705 facts. The Danus README describes a run with 3,157 facts, of which only 664 supported the final theorem; the rest were abandoned lines of attack.

## Workers are explicitly told to go step by step

- **Verify intermediate lemmas first.** Workers must verify every intermediate lemma before building on it. The contract calls this the single biggest correctness safeguard.
- **Publish failures.** Dead ends and obstacles go into shared memory so other workers skip them.
- **Pick techniques adaptively each round.** Options include easy immediate consequences, toy examples, counterexamples, several different ways to split the theorem into subgoals, and literature search on arXiv.
- **Hard problems are not a reason to stop.** Workers keep going until the target is a verified fact or they are told to stop.
- **Small submissions, also for practical reasons.** In p3b, oversized proofs timed out at the verifier (504s). The main agent then told workers to submit each lemma on its own (under ~10 KB of proof text) and to prove big theorems as short "assembly" facts that mostly cite earlier ones.

## Steering: summarize, consult, assign

Workers don't plan the whole attack. About every two hours, and only when there is new state, the main agent does three things:

1. **Summarize (elaborate).** It writes a fixed-template summary of the project: the verdict, closed parts, dead routes, the main blocker, and the missing "bridge" lemmas.
2. **Consult.** It sends that summary to a strong model; this deployment used GPT-5.5-pro through a paid API, at about $19 for p3b's first two rounds.
3. **Assign.** It shares the reply with every worker as `master_guidance` and writes each worker a `TASK.md` naming its piece of the problem. Workers that finish their piece pick the highest-leverage open direction on their own.

## Are agents given easier versions of the problem?

Not as a replacement, but they do work on easier versions as stepping stones.

- **The goal itself is fixed.** The summary skill forbids weakening it: no redefining, simplifying, restricting to a special case, or swapping in an easier stand-in. If the goal looks false, the agent must say so and still keep it fixed.
- **Special cases come from the breakdown.** p3b's goal is the maximal ratio of ideal to worst-case GMRES for every matrix size n and step count k, plus a description of the matrices that attain it. The second strategy round:
  - proved the ratio is unbounded at (n,k)=(4,3), using an explicit certificate the strong model supplied;
  - assigned separate workers to the k=2 frontier, the n=3, k=2 case, the asymptotics, and the boundary where equality holds.
- **One of those cases closed.** A worker later proved the ratio equals 1 at (3,2), the first complete cell of the k=2 table.

## Caveat

"Verified" means one LLM verifier accepted each step. No human or formal system has checked it. Results such as the p2a paper's claim of super-polynomial growth for Gaussian elimination with complete pivoting need a human read before anyone relies on them.
