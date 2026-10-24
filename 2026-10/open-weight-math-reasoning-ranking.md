---
title: Best open-weight models for math research
description: Ranking GLM 5.3 and Kimi K3 as the two best open-weight models for mathematical research capability, read from the grader's comments in the P05 strategy test rather than from the pass/fail column
date: 2026-10-23
---

## Question

Which open-weight model has the best mathematical problem-solving and research capability, according to the [P05 strategy test report](assets/p05-strategy-report-20261022.html) (run 21–22 October 2026)?

## What the report measured

Five open-weight models — Kimi K3, DeepSeek V4.1 Flash (1017), Qwen 3.8, GLM 5.3, Nemotron 3.5 Super — got 20 calls each, no tools and no web, on problem 5 of First Proof batch 3: for a hyperfield with multivalued addition, does 0 ∈ x⊞y⊞z imply 0 ∈ x³⊞y³⊞z³⊞−xyz⊞−xyz⊞−xyz? The answer is **No**, and Claude Opus 5.5 graded every reply blind against the author's solution, where the author's counterexample is a *countable* hyperfield built through infinitely many choices and every hyperfield of size ≤ 13 was computer-checked to satisfy the implication.

- **0 of 92 open-weight replies were graded Viable.** 80 of 92 answered Yes, the wrong answer.
- All 12 replies that answered No rested on a counterexample the grader refuted.
- The only Viable reply in the study came from GPT-6 Astra, a closed model, 1 of 1 call at default reasoning: an infinite projective plane on powers of t built from a set whose positive differences are all distinct with 13 ∉ D.

So no open-weight model solved it, and there is no winner by the study's own success criterion. The ranking below is therefore over the **12 correct-answer replies**, scored by how substantively they engaged the real proof, taken from the grader's written reasons for each.

## Ranking

1. **GLM 5.3 — best replies overall.** Its 17-element hyperfield reply is the only open-weight reply in the batch the grader could *not* refute: it was graded Not determinable, because the author rules out every hyperfield of size ≤ 13 and leaves 17 open. Reaching that boundary required reading the computer-check remark, concluding a counterexample must be larger, and picking a size deliberately just outside the verified range; its quotient-hyperfield framing lemma was called correct, and it failed only by never producing the table. Its fusion-calculus reply is one of just two in the set the grader says *"roughly [reduces to] the content of the author's fusion-tract counterexample"*, with steps 1–3 carrying no complaint; the gap is a real, nameable piece of the author's construction (no fission). It answered No 5 times, more than any other model, with 5 distinct constructions rather than resampling one idea.
2. **Kimi K3 — deepest single engagement.** Its forest/Euler-count reply is the only reply the grader maps onto the author's own propositions by name (`fusion_counter`, `leaf_count`), and it independently reproduced the count B = n + 2c. It lost on a substantive point — the hyperfield it builds cannot exist, since 1⊞1 = ∅ and hyperfield sums are never empty — and the grader notes the missing control is a substantial part of the proof, not a routine step. Its other reply was the quaternion trap, and only 2 of its 20 calls reached a correct answer at all.

## Why the rest failed

Nine of the twelve used a **non-commutative** multiplicative group (quaternions, A₄, skew fields) or an addition table that is not even commutative; the grader says each time that the question's hyperfields have an abelian ℍ^× and that every commutative field satisfies the identity, so no such route can work. This is a definitional blind spot rather than hard mathematics, and it accounts for all four DeepSeek V4.1 Flash replies and one of Kimi's two. Qwen 3.8 is the hardest to judge: one correct-answer reply, its computation called muddled, and 19 of 20 calls answered Yes.

Every open-weight model hunted small explicit finite structures (4, 5, 7, 17 elements) and none tried the infinite construction that actually won, which is the real capability gap the report exposes: a gap in research taste, not arithmetic.

## Caveats

The grader's reasons are published only for the 12 No-replies, so they sample each model's better attempts and say nothing about the 80 Yes-replies. With 1–5 graded items per model, the tail of the ranking is within noise, and the top of it rests on one unrefuted reply plus two near-misses on the author's own method.