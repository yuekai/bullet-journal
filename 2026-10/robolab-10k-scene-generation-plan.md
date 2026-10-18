---
title: RoboLab 10k-scene generation plan
description: Plan to scale RoboLab scene/task generation to 10k scenes by adapting TextWorld's layered pipeline, with generated 3D assets
date: 2026-10-17
---

A plan for generating 10,000 RoboLab scenes with tasks, worked out against the RoboLab paper (arXiv 2604.09860) and its repo. The idea: replace per-scene LLM generation with TextWorld's layered pipeline — logic, world generation, quest generation, text rendering — grounded in RoboLab's solvers, using generated 3D assets instead of scanned ones.

## RoboLab today

- RoboLab (NVIDIA) benchmarks *real-world-trained* policies (DROID fine-tunes) in high-fidelity IsaacLab simulation — the opposite of train-in-sim benchmarks. A **scene** is objects + poses; a **task** is a scene + a language instruction + executable success predicates; an **environment** binds a robot, observation/action spaces, and controlled perturbations (camera, lighting, background, object pose) at runtime.
- RoboLab-120's 120 tasks are hand-authored. The paper's LLM task generation measured only 57% fully-aligned on color and 60% on counting tasks: instruction and termination code are generated separately and judged for agreement afterward. That is the weakness this plan removes — both become renderings of one symbolic goal.
- Repo state (github.com/NVlabs/RoboLab): scene generation is real code (`robolab/scene_gen/llm_scene_gen/`: predicates, SpatialSolver, PhysicalSolver with a 2 cm stability threshold, FeedbackSystem) driven by an interactive Claude Code skill; task generation is only a skill (a prompt document) plus a post-hoc `tests/test_tasks_valid.py`. No batch drivers exist. Scene generation is text-seeded (theme + 312-object catalog from YCB/HOT3D/HOPE/HANDAL/VoMP): layouts are generated, meshes are pre-authored; nothing is image-conditioned.

## The plan

- **Logic layer (from TextWorld):** typed facts over catalog entities, with affordance predicates derived from catalog dimensions — `fits_in`, `stackable_on`, `graspable`, `reachable` — so chaining never proposes physically impossible goals. Rewrite the action rules from scratch (only take/put/insert survive; no rooms, cooking, or open/close); reuse `textworld.logic` and the chaining modules; drop Inform 7 — the compile targets are RoboLab `Task` classes + USDA scenes.
- **Scenes:** an LLM emits parametrized templates (object *classes* + relations, counts and radii as ranges); a seeded sampler instantiates each template 50–200×; SpatialSolver/PhysicalSolver solve poses; Isaac settles. Overgenerate 2–3× and **reject** (solver failure, >2 cm displacement, fell off support) instead of an LLM repair loop. Settle is the GPU bottleneck (~8 s/scene ⇒ ~44 GPU-hours sequential for 20k): shard workers or settle K cloned scenes per 300-step rollout; skip settling for flat-table scenes.
- **Tasks:** backward chaining from sampled goal facts guarantees solvability and yields a reference plan; convert the chain to a dependency DAG → RoboLab's sequential subtasks with parallel events (chains are total orders, but apple-then-orange = orange-then-apple); quest depth/breadth map onto DifficultyScore. Per template, execute the reference plan with scripted IK pick-place, upgrading "logically solvable" to "demonstrably solvable" and producing demos.
- **Language:** render the *specific* instruction variant symbolically from goal facts (ground truth by construction); LLM paraphrases default/vague, each verified symbolically. Color/size/count become logical facts, so distractors are constructed adversarially per competency axis rather than sampled.
- **Assets (decided): generated 3D assets are acceptable, including targets and containers.** EmbodiedGen-class tooling (text/image → sim-ready USD with part affordances and validated grasp poses) as primary backend; Infinigen-Sim parametrized assets where exact affordance geometry matters. Validate by rerunning RoboLab-120 with each real object swapped for a generated counterpart and checking that policy rankings against RoboArena Elo (Spearman ρ = 1.00 today) survive.
- **Artifacts:** predicates + seed is canonical; USD is a regenerable build product (also hedges Isaac version drift). Dedupe by layout signature (multiset of class + relation + coarse occupancy grid); QA = 100% automatic checks + 2–3% sampled LLM/VQA judging. LLM cost is trivial (~300 template calls for 10k scenes); GPU settle time and diversity bookkeeping are the real costs.

## Known issues to solve

- Boolean facts vs geometry: `in(pumpkin, bowl)` is logically valid and physically impossible — BEHAVIOR-1K's BDDL sampling failures are the precedent. Keep the KB dimension-aware and monitor acceptance rate per difficulty cell, since hard tasks fail instantiation most.
- Graspability/reachability: the Robotiq 2F-85's 85 mm stroke makes many VoMP containers anchors, not targets; RoboLab's own MNPE analysis shows success peaks ~0.5 m from the robot base.
- Reorientation ("make the mugs upright") has no TextWorld analogue — needs a new predicate with a geometric realizer.
- Spatial relations are continuous and frame-dependent: sample with margin, evaluate with tolerance in the robot/camera frame, reject near-boundary cases.
- Realism prior: keep the LLM (or hand-written theme priors) at template level so scenes stay natural rather than combinatorially weird.

## Related work and positioning

- **ALFWorld** — the precedent for aligning TextWorld with embodied tasks, but it inherited ALFRED's scenes rather than generating them.
- **GenManip (CVPR 2025)** — nearest neighbor: LLM-written task-oriented scene graphs, 10K GPT-4V-annotated Objaverse assets, topological placement, scripted-demo executability check, final-state→graph symmetric evaluation. No planner, so no solvability guarantees or difficulty knobs; the benchmark is 200 human-curated scenarios.
- **BEHAVIOR-1K/OmniGibson** — BDDL predicate initial/goal conditions sampled physically; the cautionary tale for grounding.
- **RoboCasa / RoboCasa365 (ICLR 2026)** — the generated-asset precedent at benchmark scale: 2,509→3,200 objects (majority Luma text-to-3D), 120→2,500 kitchens (50 Zillow-layout "digital cousins" × 50 styles), 365 tasks from LLM blueprints coded by hand, MimicGen 100K trajectories → 1,615 h synthetic data. MuJoCo/robosuite; trains in sim (the opposite thesis to RoboLab's).
- **EmbodiedGen V2** — text/image → policy-ready assets and task-driven worlds, USD export to Isaac Sim; reports 21.7→75.0% real-robot success for policies trained purely in generated worlds.
- The gap this plan fills: nobody combines planner-derived solvable goals + per-axis controlled distractors + generated assets + evaluation of real-world-trained policies.

## Open questions

- Does the generated-asset visual shift break RoboLab's RoboArena rank-correlation claim? The swap experiment above answers it either way.
- Which asset backend for the ~312-slot catalog: EmbodiedGen generation, curated Objaverse retrieval with colliders/mass, or Infinigen parametrized?
- Can tasks be derived purely from scene predicates (a `place-in` relation inverts to "take X out of Y") with no per-task LLM call at all?

## Sources

- RoboLab: [paper](https://arxiv.org/abs/2604.09860) · [repo](https://github.com/NVlabs/RoboLab) · [project page](https://research.nvidia.com/labs/srl/projects/robolab/)
- [GenManip](https://arxiv.org/abs/2506.10966) · [RoboCasa](https://arxiv.org/abs/2406.02523) · [RoboCasa365 (ICLR 2026)](https://proceedings.iclr.cc/paper_files/paper/2026/hash/a05003fdb1e9562ab0c0a9719ea4de10-Abstract-Conference.html) · [Infinigen-Sim](https://arxiv.org/abs/2505.10755) · [ALFWorld](https://arxiv.org/abs/2010.03768) · [EmbodiedGen](https://github.com/HorizonRobotics/EmbodiedGen)
