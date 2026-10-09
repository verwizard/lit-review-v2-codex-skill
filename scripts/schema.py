"""Shared CSV schemas for lit-review-v2 project files."""

CSV_SCHEMAS = {
    "screening.csv": [
        "record_id", "study_id", "title", "authors", "year", "venue", "document_type",
        "doi", "source_url", "candidate_source", "retrieval_date", "version_relation",
        "pass_a_decision", "pass_a_reason", "pass_b_decision", "screening_reason",
        "full_text_status", "final_decision",
    ],
    "evidence_table.csv": [
        "record_id", "study_id", "ref_no", "cite_key", "title", "authors", "year", "venue",
        "doi", "technical_route", "research_question", "study_type", "datasets", "method",
        "comparators", "outcomes", "key_findings", "limitations", "review_relevance",
        "evidence_strength", "evidence_direction", "evidence_checked", "evidence_locator",
        "methodological_quality", "quality_flags", "comparison_validity", "citable_claim",
        "source_url",
    ],
    "reference_map.csv": [
        "ref_no", "record_id", "study_id", "cite_key", "title", "authors", "year", "venue",
        "doi", "version_relation", "evidence_strength", "methodological_quality", "source_url",
    ],
    "claim_registry.csv": [
        "claim_id", "claim_type", "claim", "supporting_refs", "contradicting_refs",
        "boundary_conditions", "confidence", "partial_dependency", "sensitivity_without_partial",
        "evidence_locators", "draft_section",
    ],
    "search_log.csv": [
        "search_id", "search_mode", "source", "query_or_seed", "search_date", "start_year",
        "end_year", "filters", "hit_count", "records_exported_or_added", "stopping_rule_note", "notes",
    ],
    "comparison_matrix.csv": [
        "comparison_id", "ref_a", "ref_b", "target_outcome", "dataset", "split", "metric",
        "adaptation_protocol", "extra_data_comparable", "model_scale_comparable",
        "comparison_validity", "reason",
    ],
    "conflict_matrix.csv": [
        "conflict_id", "question", "evidence_for", "evidence_against_or_boundary",
        "comparison_validity", "likely_heterogeneity", "synthesis", "confidence",
    ],
    "evidence_matrix_by_route.csv": [
        "route_id", "technical_route", "included_refs", "shared_technical_idea",
        "synthesized_evidence", "main_metrics", "advantages", "limitations",
        "applicability_boundary", "main_heterogeneity", "confidence",
    ],
    "claim_confidence.csv": [
        "claim_id", "claim", "supporting_refs", "confidence", "partial_dependency",
        "sensitivity_without_partial",
    ],
    "coverage_audit.csv": [
        "dimension", "value", "n_records", "n_keep", "n_strong", "n_partial", "share_keep", "flag", "notes",
    ],
    "bibliometrics.csv": [
        "record_id", "study_id", "ref_no", "venue", "venue_type",
        "journal_impact_factor", "impact_factor_year", "impact_factor_source",
        "cas_quartile", "cas_quartile_year", "cas_quartile_source",
        "conference_tier", "conference_tier_source", "citation_count",
        "citation_source", "citation_as_of", "bibliometric_status", "notes",
    ],
}

OPTIONAL_FILES = ("bibliometrics.csv",)
REQUIRED_FILES = tuple(name for name in CSV_SCHEMAS if name not in OPTIONAL_FILES) + ("metadata.json", "review_draft.md")
