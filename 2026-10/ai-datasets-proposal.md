---
title: AI Datasets proposal
description: Draft of a three-aim proposal for NSF 26-512 (AI Datasets) — the economics of open data, agent-ready pipelines over existing scientific datasets, and verified knowledge graphs built from agent-scale outputs
date: 2026-10-24
---

**Program:** [NSF 26-512, Unlocking Dataset Value for AI-Enabled Scientific Discovery (AI Datasets)](https://www.nsf.gov/funding/opportunities/ai-datasets-unlocking-dataset-value-ai-enabled-scientific-discovery/nsf26-512/solicitation). Impact tier: up to $2M over 3 years. Full proposals due **Wed Nov 4, 2026, 5 pm local**; expect an ORSP internal deadline about a week earlier. Title must begin `AIDatasets:Impact:`. The Project Summary ends with a `Keywords:` line naming the directorates and communities served.

**What reviewers score, beyond intellectual merit and broader impacts:** (1) size, commitment and breadth of the communities that benefit; (2) novelty and transformative potential of the dataset enhancements; (3) security, integrity and governance, including the community contribution process and sustainment plan; (4) viability and ease of adoption. The Project Description must have four sections: vision and community benefit; research plan; dataset governance and integrity; dataset availability and infrastructure. Collecting de novo datasets is out of scope. Proposals are encouraged to use NAIRR, NSF data platforms and the Genesis Mission platform.

## Summary

Data is the scarce input to AI, and scientific data is where the gap is widest: public databases, the mathematical literature and the formal libraries exist, but agents cannot reliably find, join, analyze or verify what is in them, and AI now produces scientific results faster than any community can absorb them. We ask for an Impact award to (1) model the economics of a market in which data is the key resource, so that open scientific data has a quantified public value and a sustainable governance design; (2) make existing scientific datasets agent-ready through pipelines that generate verified, executable tasks over public databases and augment Mathlib from the open mathematical corpus; and (3) harmonize AI-generated results back into community datasets as verified, provenance-tracked knowledge graphs, piloted on the 722-paper OpenAI mathematics release and on one empirical dataset. Aims 2 and 3 share one method, agent-scale research: one agent per unit of a dataset, outputs merged into a graph, nothing entering the graph without a verifier's verdict.

## Motivation

- **Data is the resource.** Our model of competition among LLM developers finds that open data restores price competition and raises user welfare (consumer surplus 2.18 → 3.34 as the open-data flow goes from 0 to 1), and that most of the gain is better models rather than lower prices (quality +0.75 of the +1.16 total). Public investment in open scientific data therefore pays through model quality, not only through access.
- **Existing scientific data is not agent-ready.** A survey of 108 public scientific and economic databases (1,842 tables, 55,784 columns, 76 identifier systems shared across databases) found no machine-readable join keys, units, missing-value semantics or known artifacts for most tables, and found that naive sampling corrupts simple statistics (clustered 37-row ChEMBL pages inflated the correlation ratio between assay type and potency from 0.29 to 0.76). Several reference docs in the agent-tooling ecosystem were already stale (LINCS CLUE retired, GWAS Catalog v1 retired, NASA DONKI moved).
- **A large part of scientific data analysis is mathematics, and the formal canon has holes.** 167 of 566 undergraduate topics are missing from Mathlib (at `22c725c`); 11 open-LaTeX textbooks cover 90 of them and partially cover 19 more; a 105-book converted corpus covers 121 and partially 28.
- **AI-generated science is now a dataset that needs organizing.** On Oct 6–7, 2026 OpenAI released 722 manuscripts in 372 result families, 162 with a Lean-formalized main result; three were retracted within days and others were criticized for claiming more than the Lean proves ([summary](https://cellcog.ai/blog/openai-math-results), [Wikipedia](https://en.wikipedia.org/wiki/Release_of_722_mathematics_papers)). The [ten Astra results](https://openai.com/index/ten-advances-in-mathematics) ship with Lean certificates. No community process integrates these into Mathlib, the arXiv or the problem catalogs (Erdős problems, formalized OEIS conjectures).
- **Agent-scale research works, and its validation is the open problem.** OpenAI's [whole-brain CRISPR atlas analysis](https://openai.com/index/scaling-ai-research-for-complex-biological-data/) ran one agent per perturbation and merged the reports into a "reasoning atlas"; a single agent given the whole dataset cited 11 papers while the swarm cited 700+. The result was validated by expert preference and citation counts, not citation accuracy. See [Distributed agents beyond mouse brains](distributed-agents-beyond-mouse-brains.md).

## Proposed work

### Cross-cutting method: agent-scale research with verification gates

The unit of work is one agent per unit of a dataset (a database table, a theorem, a manuscript, a gene, a material, a transient), and the unit of output is a verified node in a graph. Datasets are chosen by four criteria: they decompose into thousands of semi-independent units; each unit has a long tail of weak signals that humans skip; interpreting a unit means synthesizing scattered literature; and the output is a ranked list for experts, not a final answer. The contrast with "one agent, deep" matters: a single long-running agent can do the per-unit work (an 8-day Claude Code session vetted one TESS candidate), but hand-picking which units get attention is exactly the triage-by-capacity the method removes (that search dropped 25 of 27 candidates "to keep the final count manageable").

The integrity contribution is the gate. Every artifact enters a community dataset only through a verifier that is independent of the producer: the Lean kernel where a statement is formal; a fresh-session LLM verifier with an explicit verdict schema where it is not (Danus: the fact is written to the graph iff the verifier returns `correct`; 18,520 verifier sessions to date); citation-accuracy checks on every literature claim; provenance (model, prompt, evidence, verifier verdict) on every node; and human adjudication of a prioritized list rather than of everything.

### Aim 1 — Economics and governance of open scientific data

Draws on the LLM-marketplace model (`~/llm-marketplace`): two tasks, two firms, users on a simplex with per-unit prices, usage logs as the training resource, and an exogenous open-data flow λ·Ū. Closed-only, the task leader keeps its users and their data, differentiation self-reinforces and prices stay high; open data lets rivals catch up and restores Bertrand pricing (price 0.71 at λ = 0, 0.23 at λ = 1). Work in the award:

- Extend the model so the value of a dataset to a developer depends on its structure (decomposability, verifiability), which the agent-scale ablation (11 vs 700+ citations) suggests gives open, well-structured data increasing returns.
- Characterize which datasets closed developers hoard and which they share, to tell a public program what to open first.
- Derive a governance and sustainment design for the datasets in Aims 2–3: who contributes, who verifies, what sustains the dataset after the award. This feeds Project Description sections 3 and 4 directly.

Effort: about 15–20%. Deliverables are a working paper and the governance model, not only the paper. The open-developer variant (a free model whose users' logs are the public dataset) is kept on the `open-developer` branch at `c244554` and is the closest thing in the model to this program's premise.

### Aim 2 — Making existing scientific datasets agent-ready

Two pipelines, each named by the dataset it enhances. The science-tasks platform supersedes the earlier genebench-max survey and the scientific-data skill; the survey is used here as the readiness baseline.

**2a. An executable task layer over public scientific databases.** The science-tasks pipeline (one agent per database-and-workflow dossier) writes, judges, builds and reviews tasks grounded in real data with real ground truth: family R archetypes R1–R6 (including truth fixed by the experimental design and causal estimands benchmarked by a trial), an estimand contract per task, tolerances calibrated by an ablation suite, independent checkers that test a property of the output rather than re-running the reference. Scale to date: 82 skills mapped to 9,564 workflow dossiers; a proposal judge with duplicate search; a build campaign of 64 concurrent builders, 24 h each, with an autonomous difficulty gate and two reviewer agents. Readiness is defined operationally: a dataset is AI-ready when each unit can be handed to an agent with the metadata it needs and the agent's output can be verified. The per-database readiness score is the task pass rate, and each failure is mapped to a metadata fix (join key, unit, missing-value code, artifact), which closes the loop with thrust 1 of the solicitation. This answers the solicitation's named topic, "automated platforms that discern the readiness of legacy datasets at scale."

**2b. Augmenting Mathlib from the open mathematical corpus.** A new formalization pipeline targets the measured Mathlib gaps: RepoProver (Meta's textbook formalizer, adapted here to papers and to the 11 open-LaTeX books; 791 of 791 theorems proven on Tropp's matrix-concentration monograph; 11 book runs live) plus the arxivlean gates (theorem extraction, self-containment, compile against Mathlib, semantic faithfulness, hidden-condition and prior-work checks; 3,269 of 11,048 papers survived). Deliverables are Mathlib contributions through Mathlib's own review process, which is the community contribution process the solicitation asks for, with the Lean kernel as the integrity gate.

The agent trajectories from both pipelines are released as a second community dataset, following the gated Hugging Face releases already made (research-lean-formalization-rollouts: 16,170 records + 19,581 undergrad records; research-math-rollouts: 33,488 records).

### Aim 3 — Harmonizing AI-generated results into community datasets

A content-addressed, provenance-tracked knowledge graph in the Danus fact-graph design: nodes are statements with evidence of three kinds (Lean certificate, independent verifier verdict, human exposition); edges link AI results to arXiv statements, Mathlib declarations and problem catalogs; retraction is a graph operation that keeps provenance. The same graph is where Aim 2b's formalizations land, so Aims 2 and 3 share one artifact. Two instantiations:

- **Mathematics.** Ingest the 722-paper release, the Astra Lean certificates, the Erdős problems database and the formalized OEIS conjectures. Classify each claim as formalized, verified, unverified, retracted, or stronger-than-formalized; measure the lag between an AI result and its appearance in Mathlib; feed verified-but-unformalized results to Aim 2b.
- **One empirical domain**, chosen by the four fit criteria with a UMich partner: one agent per unit of an existing public dataset produces an annotation atlas, every literature claim citation-checked, every mechanism proposal scored by an independent verifier, and the atlas delivered to the domain community as a prioritized list. Candidates are in Partners below. Generalization to further domains is stated as future work.

### Datasets and construction

| Existing dataset | Owner / license | Enhancement | Aim |
|---|---|---|---|
| Public scientific and economic databases (ChEMBL, UniProt, GTEx, gnomAD, ENCODE, Materials Project, SDSS, NASA, USGS, NOAA, Census, FRED, …; 108 surveyed) | Various; redistribution tiers already recorded | Executable task layer, readiness scores, metadata fixes contributed upstream | 2a |
| Mathlib | Lean community, Apache 2.0 | Formalizations of the 167 missing undergraduate topics and of arXiv theorems | 2b, 3 |
| arXiv math.* and open-LaTeX textbooks | arXiv license terms; open books | Theorem extraction and Lean statements | 2b |
| OpenAI 722-paper release and Astra Lean certificates | GitHub, Apache 2.0 | Claim classification, links to canon, retraction tracking | 3 |
| Erdős problems database, formalized OEIS conjectures | Public | Links from AI results to catalog entries | 3 |
| One empirical dataset (see Partners) | Public | Per-unit annotation atlas | 3 |

### Research questions

1. Under what conditions does open scientific data raise model quality and user welfare, and which datasets do closed developers hoard? (Aim 1)
2. Can readiness be measured by agent task success, and do metadata fixes chosen from failure modes raise it? (Aim 2a)
3. How much of the Mathlib gap can agent pipelines close under Mathlib's review, and at what faithfulness-gate cost? (Aim 2b)
4. What fraction of AI-generated mathematical claims are formalized, verified, or over-claimed, and how fast do verified results reach the canon? (Aim 3)
5. Does per-unit verification (citation accuracy, independent verdicts) change which agent-generated hypotheses experts rank highest, relative to preference-only validation? (Aim 3)

### Deliverables

- A governance and sustainment model for AI-enhanced scientific datasets, with the working paper behind it.
- The task layer and readiness scores for the chosen databases, with metadata fixes contributed upstream and the trajectories released under gated access.
- Mathlib contributions, merged through Mathlib review.
- The verified knowledge graph with its ingestion, verification and retraction tooling, open source, with the math and empirical instantiations populated.
- Annual releases on an NSF data platform or NAIRR-connected repository, plus Hugging Face mirrors.

## Partners and roles

- **PI (Statistics):** Aim 1 model, the verification and calibration design across Aims 2–3, and the readiness metric.
- **Co-PI or senior personnel for the empirical domain** (one of):
  - Wenhao Sun (MSE) and/or Bryan Goldsmith (ChemE): materials candidates from the Materials Project or OQMD, each needing a synthesizability and prior-report check; Goldsmith already runs agentic workflows for catalysis. Strong on all four criteria.
  - Joshua Welch (DCMB/CSE): public Perturb-seq and single-cell perturbation atlases; nearest analog to the mouse-brain work, BIO directorate.
  - Camille Avestruz (Physics, LSST DESC): Rubin/ZTF alert candidates. NSF facility, which the program will like, but literature synthesis is a smaller part of transient vetting, so a partial fit.
  - Avoid clinical datasets (Michigan Genomics Initiative PheWeb, ClinVar VUS) in an NSF proposal even though they are the closest structural analogs.
- **Systems:** Mosharaf Chowdhury (CSE; Curie, automated experimentation) for running thousands of agents; MIDAS and MICDE (Karthik Duraisamy's foundation-models-and-agents initiative) as institutional infrastructure for section 4.
- **External letters:** a Mathlib maintainer or the Lean FRO (Aims 2b and 3); two or three database maintainers for 2a; LLM360 / IFM as the data-release partner under the solicitation's industry-and-non-profit partnership clause.
- **Compute:** request NAIRR allocations; do not make the proposal depend on the MBZUAI cluster.

## Timeline and milestones

- **Year 1:** Aim 1 model extension and first governance draft; 2a task layer over 10 databases with readiness scores; 2b pipeline on the 11 books, first Mathlib PRs; 3 graph schema and ingestion of the 722-paper release with claim classification.
- **Year 2:** 2a scaled to 30+ databases with upstream metadata fixes; 2b arXiv theorems into the graph and Mathlib; 3 empirical-domain atlas over the full dataset with expert evaluation; first public release.
- **Year 3:** readiness re-measured after fixes; governance handed to the communities; sustainment plan executed; final releases and the working paper.

## Budget

Rough shape for a $2M, 3-year Impact award: PI and co-PI summer salary; one postdoc (verification and graph); two graduate students (2a/2b and 3); cloud and NAIRR compute for agent campaigns; subaward or senior-personnel support for the domain partner; travel including the NSF NAIRR community meeting the solicitation says to budget for; data hosting.

## Risks and mitigations

- **Aim 1 reads as theory in a dataset program.** Keep it to 15–20% effort and make its deliverable the governance and sustainment design the solicitation scores.
- **Aim 2 reads as model training.** Phrase every pipeline by the dataset it enhances; the trajectories are a byproduct release, not the goal.
- **Aim 3 reads as de novo data.** Anchor on the existing public releases (722 papers, Astra certificates) and on an existing empirical dataset; the graph integrates, it does not collect.
- **Judge leniency and design collapse** in the proposal campaign (369 of 381 approved; one hidden-perturbation design per skill), pilot yield (50 PRs from 60 builders, 25 of 33 too easy), and arxivlean's gate dropping about 40% of correct proofs. Disclose these as known gaps with the fixes already in the tech-debt lists.
- **Dataset ownership.** The databases belong to others; the proposal builds a layer over them and contributes fixes upstream.
- **Validation of agent-generated hypotheses.** Expert preference is not citation accuracy; the verification gates and a preference-vs-accuracy comparison are part of the research plan, not an afterthought.
- **Scope.** One empirical domain with a named partner, not a list of six.

## Open questions

- Which empirical domain and partner (Sun/Goldsmith, Welch, or Avestruz), and can a letter be obtained by the internal deadline?
- Impact or Flagship? Three aims of this weight read like a Flagship, but Flagship proposals are strongly encouraged to contact `aidatasets@nsf.gov` first; an email early in the week is still possible.
- Does the program count Mathlib and the arXiv as "scientific community datasets"? Worth asking the program officers in the same email.
- Which NSF data platform or NAIRR repository hosts the releases?
- Whether Aim 1's open-developer variant belongs in the proposal or stays on the branch.
