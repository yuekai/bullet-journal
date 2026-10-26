---
title: Synthetic code-prompts data pipeline
description: How the code_prompts pipeline turns code snippets into synthetic programming problems, and where its 1,304-file concepts seed comes from
date: 2026-10-25
---

Reference notes on the `code_prompts` family of [LLM360/synthetic-data-bbq](https://github.com/LLM360/synthetic-data-bbq) (private), read at `main` @ `13a48aa`.

## `code_prompts` at a high level

It is a two-stage synthetic **programming-problem** factory:

1. **Make problems** — for each Python snippet of a 57.3 M-row code corpus, synthesize a *meta-prompt* that asks a model to invent one programming problem grounded in (a) a canonical "concept" file and (b) that snippet as style inspiration.
2. **Solve them** — the separate `code_solutions` prompt family later reads those problem statements back and samples solutions.

So `code_prompts` is prompt synthesis plus generation, not solution generation.

Four files carry it; everything else in `code_prompts/` (CLI, QUICKSTART, `usage_examples.py`, `custom_extensions.py`, `DELIVERY_SUMMARY.md`) is standalone scaffolding for the generator and is not on the production path.

| file | role |
|---|---|
| `code_prompts/synthetic_problem_generator.py` | builds each meta-prompt from a concept file + an inspiration window |
| `submit_all_array.py` | SLURM orchestration: one job per 5,000-row slice of the snippet corpus, skipping slices whose output file already exists |
| `vllm_sample.py` | the job: reads its slice, builds prompts, samples with vLLM |
| `process_data_filter.py` | drops degenerate generations, emits chunked training JSONL |

The flow per slice: read 5,000 `{"seq_id", "text"}` rows → drop snippets with ≤10 lines → cut 20–30 random *consecutive* lines from each survivor → hand out the concept files cyclically so each slice sees the whole taxonomy → sample one diversity config per prompt → render a five-section prompt (header, concept, whole reference implementation, inspiration window, task instructions ending in "output only the problem statement") → sample `gpt-oss-120b` at temperature 1.0, top_p 1.0, `max_tokens=8000`, reasoning effort high → write `queries_{start}_{end}.json`, a dict keyed by absolute corpus row index with `{seed, behavior, generation, token_count}` (where `behavior` is the *concept name*).

Filtering keeps generations with `100 < token_count < 7500`, strips the gpt-oss `analysis…assistantfinal` channel text, drops samples with leftover channel markers or a long "good luck" sign-off, then writes **`seed + generation`** as one `{"text", "token_count"}` row and shards it into 100,000-row chunks. The training example is therefore "meta-prompt → the problem it produced", i.e. data for a problem *generator*; only the downstream `code_solutions` stage consumes the problems themselves.

Measured on slices 0–30 M: 29,924,995 processed → **27,800,700 kept** (7.10 % drop), 134.9 B tokens, 4,852 tokens/doc, 279 chunks.

Two variant families reuse the same code: `code_prompts_all_knobs*` re-enables all 17 diversity knobs (detail level across vague/moderate/detailed, explicit constraints, domain contexts, starter code, tests), whereas the base variant pins `detail_level` to *vague* and forces every optional block off — only complexity, context type and "must use this approach" vary. `problems_code_prompts*` is a re-filter of the same raw output that keeps the bare problem statement, without reasoning and without the seed prefix.

## Where the programming-concepts seed comes from

There is **no single concepts file**. The canonical seed is a directory tree of **1,304 `.py` files in 66 top-level categories** that lives outside the repo; `vllm_sample.py` hardcodes its path, and the README describes it as `problem_sets/code_topics/merged`.

It is derived from two public GitHub checkouts that sit next to it in the same directory, both MIT:

| local dir | upstream | pinned commit |
|---|---|---|
| `Python/` | [TheAlgorithms/Python](https://github.com/TheAlgorithms/Python) | `ae68a78`, 2025-11-06 |
| `algorithms/` | [keon/algorithms](https://github.com/keon/algorithms) | `5991e05`, 2025-11-02 |

Curation, verified by comparing file hashes:

| stage | files |
|---|---|
| `Python/` upstream | 1,373 |
| → `python_cleaned/` | 964 |
| `algorithms/` upstream | 414 |
| → `algorithms_cleaned/` | 352 |
| **`merged/`** | **1,304** = 962 from TheAlgorithms + 342 from keon |

- **`python_cleaned` drops 418**: 221 `__init__.py`, 11 test files, **all 173 `project_euler/problem_*/sol*.py`**, `docs/conf.py`, and three `scripts/` maintainer utilities; it also flattens `linear_algebra/src/*` → `linear_algebra/*`. Project Euler is the notable exclusion — hundreds of one-shot numeric answers, the least teachable material in the repo.
- **`algorithms_cleaned`** is mostly a path rewrite: the keon repo nests everything under an `algorithms/` package, so that prefix is stripped.
- **`merged`** is the union with **TheAlgorithms winning on path collisions**: 10 `maths/`, `matrix/` and `strings/` modules exist at the same relative path in both repos and only the TheAlgorithms versions survive. Two further TheAlgorithms files are dropped as example/helper modules, and 8 single-module subdirectories are flattened (`tree/avl/avl.py` → `tree/avl.py`).

The taxonomy *is* the concept list: the generator reads the relative path (`data_structures/binary_tree/avl_tree.py` → category `data_structures`, concept `avl tree`) and pastes the whole file in as the reference implementation. Coverage therefore follows file counts — `maths` 203, `data_structures` 107, `strings` 94, `graphs` 60, `sorts` 50, `dynamic_programming` 49 — and a category's global weight reflects how many files its upstream repo had.

Open: the cleaned+merge step is not reproducible from the repo — there is no build script, manifest or recorded upstream commit, so the derivation is recoverable only by diffing the directories. The merged tree is a November 2025 snapshot of two moving repositories.