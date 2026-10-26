---
title: How Danus builds its fact graph
description: The data model behind Danus's fact graph (node shape, content addressing, cascade revocation), why it is not a concept graph, and which kinds of statement splitting it permits — conditional reductions with named assumptions yes, weakening the goal no
date: 2026-10-26
---

Danus's "knowledge graph" is a **fact graph**: a DAG whose nodes are verifier-accepted mathematical statements. This note was read off the public release at [frenzymath/Danus](https://github.com/frenzymath/Danus) (shallow clone, no deployment), chiefly `danus/core/DATA_MODEL.md`, `danus/core/factgraph.py`, `docs/concepts.md`, `docs/security-and-trust.md`, `agents/contracts/verifier.md`, `.agents/skills/elaboration/SKILL.md` and the worker skills under `agents/skills/worker/`. Compare [How Danus makes incremental progress](how-danus-makes-incremental-progress.md), which covers the runtime and steering loop of our own deployment and two of the same questions from deployment evidence rather than from the data model.

## The node is a proof record, not a concept

Each fact is one markdown file `fact_graph/facts/<fact_id>.md` with six frontmatter fields plus `## statement`, `## proof` and an optional `## intuition`:

```yaml
fact_id: 0056a49384644046          # content-addressed, bare hex
problem_id: KMMP
author: KMMP_pro3
predecessors: [7b6dd3df2e88fff5]   # the DAG edges: facts this proof cites
glossary_introduces: {X: ..., K_F: ...}   # symbols this fact defines
external_refs: [{key, authors, title, arxiv, cited_for}]   # mutable, not hashed
```

- **Edges.** `predecessors` are the ids the proof actually uses. A worker records them at submission, so the edge set is the proof's citation set, nothing inferred.
- **Id.** `SHA256(problem_id, sorted(predecessors), sorted(glossary_introduces), normalized(statement), normalized(proof))[:16]`. Consequences fall out for free: same content dedups, a node is immutable (any edit is a new id), and the graph cannot cycle — the DAG property is not enforced by a check.
- **Revocation** is the repair mechanism. `revoke` moves the fact and every descendant to `_revoked/`, appends to `revocation_log.jsonl`, and `add` later refuses a revoked predecessor. This is how the nilpotent-definition error in one README case study was contained.
- **Self-containment** is checked by a glossary-coverage lint over four layers (global glossary → project glossary → cited predecessors' glossaries → this fact's), which is what keeps a node readable without the run's history.
- **Read access** is a derived BM25 index rebuilt on demand from `facts/*.md` (`fact_search`), never a stored second copy.

## The only write path

Three tiers of memory, decreasing in trust: per-worker `local memory` (rough notes) → project-shared `global memory` (typed findings, including dead ends and verification traces) → the fact graph. A finding is promoted only by this cycle: a worker calls `fact_submit` with statement + proof + cited ids, a **cold-start** verifier instance (fresh per submission, writes nothing) returns `correct` iff zero critical errors and zero gaps, otherwise repair hints which are logged back into global memory, and only on acceptance does the worker write the node. The main agent has no `fact_submit` tool, so the orchestrator structurally cannot inject a claim. There is deliberately no `promote()` function in the library: promotion is agent behavior, not code.

## How splitting happens — and what it may not do

There is no symbolic splitter. Decomposition lives in prose artifacts: the main agent's `elaboration` (a fixed five-section synthesis whose **interface contract table** lists, per proof stage, input required / output claimed / available facts / missing verification on the actual construction / failure mode / status, plus **missing bridge lemmas**), and the worker skill `propose-subgoal-decomposition-plans` (several materially different ordered subgoal plans, screened by `direct-proving`, each motivated by prior examples, counterexamples and dead ends).

**Adding assumptions is the central move.** The elaboration status vocabulary defines `SUBSTANTIAL` as "a conditional package exists, but at least one input/output hypothesis is unmatched on the actual construction", so a fact of the form *if H then C* is a normal, desirable node. What is banned is passing off an assumption as established: verifier **P3** demands a 16-hex `fact_id` in the *same paragraph* for any step that assumes a reduction or narrowing, **P3-supplement** inlines cited facts and flags inherited conditional premises transitively, and **P6** rejects statements that say "under the standard hypotheses" without listing them.

**Weakening the goal is not allowed.** The elaboration skill states the fixed goal must not be redefined, simplified, restricted to a special case, or replaced by an easier proxy; the paper writers are likewise told not to strengthen, weaken or restate a theorem. When a step cannot be cashed out the answer is a label, not a hedge: `FALSE AS STATED`, `OBSOLETE`, `SUBSTANTIAL`, or in the human summary `CONDITIONAL` / `OPEN` with the missing inference named.

Relaxation does appear, but only as scaffolding that is expected to be discarded or demoted:

- **Toy examples** that satisfy both the assumptions and the conclusion, used to see where each assumption bites.
- **Counterexamples** that keep the assumptions and break the conclusion, kept in shared memory so siblings skip the route.
- **Proxy problems** — in the YTD case study the rational form of the problem was solved first and then adapted to the integral version.
- **Conditional scaffolding clusters** — in the 3,157-fact run only 664 facts form the theorem's supporting closure; the rest are alternative attacks, unproved-conditional packages the final proof never cites, and an independent re-derivation of one bound.

## Caveat

"Verified" means a cold-start LLM judged the proof, with no formal proof assistant anywhere in the loop, and the cascade repair is only as good as whoever notices a bad definition. A human read is still owed before relying on a headline result.