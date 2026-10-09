---
name: lit-review-v2
description: "Build targeted, evidence-traceable literature reviews from a research topic, paper set, DOI list, or existing review. Use when the work needs screening, evidence tables, claim-to-source traceability, route synthesis, conflict analysis, or review lint; do not present a targeted review as a systematic review."
metadata:
  short-description: "Evidence-traceable targeted literature reviews"
---

# Lit Review v2

Use this skill for a structured evidence review whose important claims can be traced to specific papers and evidence locations. It supports a new review, a review started from supplied papers or DOI records, and an incremental update after a previous search cutoff.

## Invocation

Invoke explicitly as `$lit-review-v2`. The older phrase `$lit-review v2` is the source workflow's informal name; use the hyphenated skill name when installing or invoking this package.

## Required boundaries

- Call the result a **targeted evidence review** when the candidate set comes from curated seeds, targeted web searches, or selected venues. Do not claim systematic-review coverage, PRISMA counts, or database-exhaustive retrieval unless the user supplies a reproducible systematic-search protocol and its complete records.
- Never invent a paper, DOI, result, dataset, quotation, or evidence locator. If only an abstract, metadata page, or partial PDF was checked, label the record `partial` and separate `verified` from `not_verified` content.
- Do not rank results across papers solely because they report the same metric. Check dataset, split, adaptation protocol, extra training data, label budget, ensemble use, model scale, and compute constraints first.
- Keep evidence strength separate from methodological quality. A paper can be well designed but only partially verifiable from the available source.

## Workflow

1. Define the topic, years, document types, focus, inclusion criteria, exclusion criteria, search mode, cutoff date, output format, and project location. If required scope information is missing, ask the user concise questions before starting the file-backed review. If the user does not specify a project location, create the project under the current workspace using a topic-derived directory name and tell the user where it was created. If the user supplies PDFs, DOI records, or a reference list, treat them as the seed candidate set.
2. Create or update the project with `scripts/init_review_project.py` when a file-backed project is useful. Record candidate provenance and every search/update family in `search_log.csv`.
3. Run Pass A for topical relevance and a minimum evidence requirement. Run Pass B for document type, method clarity, experimental results, duplicate/version relations, and evidence availability. Preserve a reason for every exclusion in `screening.csv`.
4. Read each kept paper far enough to fill `evidence_table.csv`: dataset, method, comparators, outcomes, key findings, limitations, review relevance, evidence strength, direction, checked content, and an `evidence_locator` such as `p. 6, Table 3`.
5. Register synthesis claims in `claim_registry.csv` before writing narrative. Record supporting and contradicting references, boundary conditions, confidence, partial dependence, and locators. Use `comparison_matrix.csv` for cross-paper comparisons that pass protocol checks.
6. Synthesize technical routes and conflicts in `evidence_matrix_by_route.csv` and `conflict_matrix.csv`. Preserve heterogeneity instead of forcing a single ranking.
7. Write `review_draft.md` with numbered citations that resolve through `reference_map.csv`. Run `scripts/review_lint.py` and fix structural or citation issues before delivery.

Read [references/workflow.md](references/workflow.md) for the operating procedure and [references/schemas.md](references/schemas.md) for the project fields. [references/installation.md](references/installation.md) explains package use and script commands. Use the scripts only when a file-backed project or deterministic lint is useful; ordinary inline answers do not need empty CSV files.

## Deliverables

The standard project contains:

- `metadata.json` and `search_log.csv` for scope, provenance, and stopping rules;
- `screening.csv` for two-stage decisions and reasons;
- `evidence_table.csv` for paper-level evidence;
- `reference_map.csv`, `claim_registry.csv`, and `claim_confidence.csv` for traceable synthesis;
- `comparison_matrix.csv`, `conflict_matrix.csv`, and `evidence_matrix_by_route.csv` for valid comparisons and route-level synthesis;
- `coverage_audit.csv` for coverage and concentration checks;
- `bibliometrics.csv` for optional, dated venue and citation annotations (created for new projects; legacy projects may omit it);
- `review_draft.md` for the narrative draft;
- `review_lint_report.json` for the final consistency report.

When the user requests bilingual terminology, write technical terms in the narrative as `English term（中文术语）` on first and subsequent uses where clarity benefits; preserve official paper titles and venue names.

## Inputs for an update

For an existing project, preserve old `ref_no` values, search only after the supplied cutoff, append new eligible studies, and update the screening, evidence, claim, route, conflict, and draft files together. Mark 2026 or any other incomplete year as incomplete in metadata and prose.
