# Lit Review v2 workflow

## Project brief

Capture these fields before searching:

- topic and research questions;
- start and end years plus a cutoff date;
- eligible document types;
- technical focus or a request to infer routes from the candidate set;
- inclusion and exclusion criteria;
- search mode (`targeted` by default);
- output format and optional project location;
- supplied PDFs, DOI records, or seed references.

The default mode is a targeted evidence review. Record the source of every candidate family and a practical stopping rule. Do not report a fabricated total hit count when a search engine or venue page does not expose one.

## Screening

Pass A answers whether the paper is directly relevant and has a minimum evidence basis. Pass B verifies publication type, year, method, empirical results, duplicate or precursor relationships, and what can actually be checked. Keep one row per candidate and explain every exclusion. A preprint-only item, challenge report, review, or duplicate can be excluded when the protocol says so.

## Evidence extraction

For every kept paper, record:

1. data and split;
2. method and training or adaptation protocol;
3. comparators and baselines;
4. metrics and key results;
5. limitations and review relevance;
6. what was checked and where it appears.

Use `strong` when the relevant method and result were checked in an accessible full source. Use `partial` when only a bounded portion was checked. For partial rows, write both labels in `evidence_checked` or the claim notes:

```text
verified:
The result and dataset stated on the abstract page.

not_verified:
The full ablation table and training-data details.
```

## Synthesis

Register claims before writing the draft. A claim should state its boundary conditions and list supporting and contradicting references. Use route-level matrices to describe shared technical ideas, advantages, limits, applicability, and heterogeneity. Use `comparison_matrix.csv` only when the protocols are comparable enough to support the intended comparison.

## Example starting prompt

```text
Use $lit-review-v2 to start a targeted evidence review.

Topic: [topic]
Years: [start–end]
Document types: journal / conference
Focus: [focus, or infer the main technical routes]
Inclusion: directly relevant, clear method, empirical result
Exclusion: review/commentary, duplicate, weakly related, no verifiable result
Search mode: targeted
Output format: Markdown
Project location: [optional; defaults to the current workspace]

Build the candidate set and source log, run two-stage screening, fill the evidence table for kept papers, mark partial evidence with verified/not_verified, record evidence locators, synthesize routes and conflicts, register claims, write the numbered draft, and run review lint. Do not present the result as a systematic review.
```

## Publication-ready pass

After the evidence-backed draft is complete, a separate editing pass can add a formal title, abstract, keywords, consistent headings, complete references, and a required citation style. It must preserve the reference map and must not add conclusions unsupported by the evidence table or claim registry.
