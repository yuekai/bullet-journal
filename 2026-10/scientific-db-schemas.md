---
title: Scientific database schema survey
description: Schemas, join keys, data artifacts and sampled statistics for the 108 databases in UMich-FATML/claude-scientific-skills, collected as raw material for GeneBench-Pro-style task generation with CausalDS
date: 2026-10-07
---

## Purpose

The goal is to generate benchmark tasks like [GeneBench-Pro](https://huggingface.co/datasets/openai/genebench-pro-public-package) in every scientific domain, not just genomics. Each task is built from a graphical model of real data tables, which then generates synthetic datasets and questions, the way [CausalDS](https://github.com/andleb/causalds) does.

GeneBench-Pro problems stage 5–7 related tables joined on shared keys, plus a data dictionary. Their difficulty comes from messy-data judgment calls: who gets selected, what's missing, how good the measurements are, and what confounds what. So the survey records each table's join structure, units, categories, missing-value meaning and known data artifacts, not only its column names. Which databases cost money is in [scientific-skills-database-access-costs.md](scientific-skills-database-access-costs.md).

## Where it lives

`~/scientific-db-schemas` is a local git repo, managed with pixi and not pushed anywhere.
- **Docs:** its `AGENTS.md` maps into `docs/`: design decisions, collection procedure, tech debt and plans.
- **Checks:** `pixi run check` runs validation, a stale-output check and the tests, and it runs from the pre-commit hook.

The main paths:

| Path | Contents |
|---|---|
| `databases/<slug>.json` | One file per database, following `schema/database.schema.json` |
| `stats/<slug>/<table>.json` | Statistics from up to 370 sampled rows per table: missingness, quantiles, top values, Spearman matrix and correlation ratios |
| `crosswalk.json` | Identifier systems shared across databases, i.e. the cross-database join graph |
| `data_dictionary.tsv` | GeneBench-style dictionary of every column |
| `INDEX.md` | Coverage table and gap list |
| `collectors/<slug>.py` | The scripts that regenerate everything above |

Raw sampled rows are in the gitignored `cache/` (426 MB), so the stats can only be recomputed on the machine that holds it.

## Coverage

All 108 databases have a file:
- **1,842 tables and 55,784 columns.**
- **20,839 columns are continuous or binary,** which CausalDS can use as nodes today.
- **204,079 rows were sampled.**
- **76 identifier systems** link two or more databases.

**45,055 columns have an official or docs description.** One group's descriptions were written from memory of the docs and have been relabeled `inferred`. Other `docs` labels are as reported by the collecting agent.

**Sampling designs, per table:**

| Design | Tables |
|---|---:|
| Independent random draws | 246 |
| Clustered random pages (≤10 adjacent rows each) | 465 |
| Seeded or convenience samples | 62 |
| No rows | 1,069 |

Most of the tables with no rows are catalog-only tables. For example, SDSS lists 214 tables, of which 15 core ones were sampled. Treat correlations from clustered or convenience samples as rough. In ChEMBL, 37-row pages inflated the correlation ratio between assay type and potency (pChEMBL value) from 0.29 to 0.76.

## Gaps

- **No rows at all:**
  - DrugBank: the API is paid.
  - ZINC: captcha.
  - Addgene: no approved token.
  - COSMIC: license-restricted downloads, so schema from the download dictionaries only.
  - MouseMine: its query endpoint kept returning HTTP 429; retry later.
- **US Census:** anonymous data queries now need a key, so 11 of its 13 tables have no rows. Registering a free `CENSUS_API_KEY` would fill them.
- **EPA AQS:** every call except the status check returns HTTP 422 with the registered credentials, possibly because the key isn't active.
- **Semantic Scholar** ran keyless, so fewer rows.
- **NASA:** the shared DEMO_KEY ran out partway through.
- **Stale reference docs in the skills repo:**
  - LINCS: CLUE retired Jan 31, 2026; replaced by GEO GSE92742/GSE70138 files and SigCom LINCS.
  - GWAS Catalog: v1 retired; v2 used.
  - RegulomeDB: endpoint moved.
  - WHO GHO: its API returned HTTP 502, so the xMart OData service was used.
  - NASA DONKI: moved to CCMC on Sep 30, 2026.
- **Over the ~300-call budget:** five databases went over it through re-runs:
  - ENA (~700 calls)
  - RummaGEO (~610)
  - QuickGO (~560)
  - UCSC (~460)
  - MyVariant (~430)

  USGS also exhausted a per-IP water-data quota it shares with other users. Some `api_calls` values are estimates or whole-database totals recorded on one table.

## Data handling

- **Sample rows:** kept only where the license allows redistribution.
- **Restricted:** COSMIC, OMIM, DrugBank, DISGENET, KEGG, Alpha Vantage, OpenWeatherMap, Addgene, WHO, SIMBAD, FRED and AlphaGenome.
- **Unknown:** CORE and Semantic Scholar.
- **Personal data:** email addresses are redacted from sample rows and stats, and collectors drop personal contact fields.
- **Secret scan:** no API key value appears anywhere in the repo, including `cache/`.

## Open questions

- AlphaGenome's terms forbid using its outputs to train other models. Its stats summarize model outputs, so should they be excluded from model fitting, keeping only the schema?
- Should the repo be pushed to a private GitHub repo?
