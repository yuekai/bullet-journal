---
title: Scientific skills database access costs
description: Which of the 100+ databases in UMich-FATML/claude-scientific-skills a University of Michigan professor can use without paying, and which need keys, academic sign-up or paid licenses
date: 2026-10-01
---

This note sorts the databases in [UMich-FATML/claude-scientific-skills](https://github.com/UMich-FATML/claude-scientific-skills) by what it costs a University of Michigan faculty member to use them, as of 2026-10-01. It's based on each database's documentation in the repo (main branch on that date), plus the providers' own pages for the ones that aren't openly free.

The "100+" count is made up of 80 databases in the `database-lookup` skill, 18 literature sources in `paper-lookup`, and about 10 dedicated data skills. BioServices, Biopython and gget mostly wrap the same public APIs and weren't checked separately.

**Bottom line:** almost all are free. Only about 3 charge a fee for what the skill actually uses: DrugBank's API, the full DISGENET dataset, and Alpha Vantage above 25 requests a day. It wasn't checked whether the U-M Library licenses any of these.

## Paid, or the cost isn't clear

- **DrugBank:** the skill calls the API (`api.drugbank.com`), which needs a paid license. Academic downloads from the website are free once your application is approved (CC BY-NC license), and grant-funded academic use counts as non-commercial ([FAQ](https://dev.drugbank.com/guides/faqs)). The skill doesn't use that download route.
- **DISGENET:** the free Academic plan, open to anyone with an institutional email, covers only the expert-curated subset, but it does include the REST API. The full dataset (text-mined data, drugs, clinical-trial annotations) is in the Standard and Advanced plans, "contact us for pricing" ([plans](https://disgenet.com/plans)).
- **Alpha Vantage:** the free key allows 25 requests a day. Paid plans cost $49.99–$249.99 a month.
- **OpenWeatherMap:** has a free tier, but One Call 3.0 needs a credit card on file.
- **Genomic Intelligence:** the hosted demo server is free and needs no key. A full API key comes by emailing contact@genomicintelligence.ai, and no prices are published ([docs](https://docs.genomicintelligence.ai/mcp)).
- **Addgene API:** needs approval plus a separate license for each data type requested. Options for non-profits exist, but it couldn't be confirmed that they're free ([access options](https://developers.addgene.org/access-options/)).
- **Imaging Data Commons:** free through `idc-index`, the REST API and anonymous downloads. Only the BigQuery route needs Google Cloud billing.

## Free because you're an academic (sign up with your umich.edu email)

- **COSMIC:** free for academic use, account required ([licensing](https://cancer.sanger.ac.uk/cosmic/license)). The skill only supports downloads, not API queries.
- **OMIM:** free academic API key, by application.
- **KEGG:** no key needed; only commercial use needs a license.
- **LINCS L1000 (CLUE):** free academic account.
- **AlphaGenome:** free key for non-commercial use.
- **DISGENET:** the curated subset only (see above).

## Free, but you must register for a key (or give an email)

- **Key required:** FRED and Federal Reserve data (both use a FRED key), BEA, NOAA, EPA AQS, Data Commons, Materials Project, NASA (a `DEMO_KEY` works for light use), BioGRID, BRENDA, USPTO, and CORE.
- **Works without a key, but a free one raises the rate limit:** NCBI (Gene, Protein, Taxonomy, GEO, dbSNP, SRA, ClinVar, PubMed), OpenFDA, BLS, US Census, OpenAlex and Semantic Scholar.
- **Email address in the request:** Crossref and Unpaywall.

## Free, no account at all

- **Databases:** AlphaFold, BindingDB, cBioPortal (public instance), ChEBI, ChEMBL, ClinicalTrials.gov, ClinPGx, COD, DailyMed, ECB, EMDB, ENA, ENCODE, Ensembl, Eurostat, GDC/TCGA (public data only), Gene Ontology, gnomAD, GTEx, GWAS Catalog, HCA, HPO, Human Protein Atlas, InterPro, JASPAR, Metabolomics Workbench, Monarch, MouseMine, MyVariant, NASA Exoplanet Archive, NIST, Open Targets, PDB, PRIDE, PubChem, QuickGO, Reactome, RegulomeDB, RummaGEO, SDSS, SEC EDGAR (it only asks you to identify yourself in the request header), SIMBAD, STRING, UCSC, UniProt, US Treasury, USGS, WHO, World Bank, and ZINC.
- **Literature sources:** arXiv, bioRxiv, medRxiv, BioStudies, DOAJ, Europe PMC, Figshare, OpenCitations, PMC, PubTator, ROR and Zenodo.
- **Dedicated data skills:** DepMap, PrimeKG, NCATS ARAX, US Treasury Fiscal Data, OneKGPd and CELLxGENE Census. Hugging Face only needs a free token for gated datasets.

**ZINC caveat:** it's free, but the skill notes that automated requests were redirected to a human-verification page on 2026-09-30, so it may not work when an agent calls it.

## Open questions

- Whether the U-M Library licenses the DrugBank API or the full DISGENET dataset.
- Whether Addgene's non-profit API access is free.
