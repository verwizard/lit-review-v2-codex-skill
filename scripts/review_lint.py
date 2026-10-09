#!/usr/bin/env python3
"""Check structural and citation consistency in a lit-review-v2 project."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

try:
    from schema import CSV_SCHEMAS, OPTIONAL_FILES, REQUIRED_FILES
except ImportError:  # pragma: no cover - supports python -m scripts.review_lint
    from .schema import CSV_SCHEMAS, OPTIONAL_FILES, REQUIRED_FILES

REF_RE = re.compile(r"\[(\d+)\]")
RANGE_RE = re.compile(r"\[(\d+)\]\s*[–—-]\s*\[(\d+)\]|\[(\d+)\s*[–—-]\s*(\d+)\]")


def cell(row: dict, column: str) -> str:
    """Return a stripped CSV value even if a malformed row has an empty cell."""
    return (row.get(column) or "").strip()


def read_rows(path: Path, fields: list[str], issues: list[dict]) -> list[dict]:
    if not path.exists():
        issues.append({"severity": "error", "file": path.name, "message": "missing required file"})
        return []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            actual = reader.fieldnames or []
            missing = [field for field in fields if field not in actual]
            if missing:
                issues.append({"severity": "error", "file": path.name, "message": f"missing columns: {missing}"})
            return list(reader)
    except (OSError, UnicodeError, csv.Error) as exc:
        issues.append({"severity": "error", "file": path.name, "message": f"cannot read CSV: {exc}"})
        return []


def unique_check(rows: list[dict], column: str, filename: str, issues: list[dict]) -> None:
    values = [cell(row, column) for row in rows if cell(row, column)]
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    if duplicates:
        issues.append({"severity": "error", "file": filename, "message": f"duplicate {column}: {sorted(duplicates)}"})


def refs_in(text: str) -> set[int]:
    text = text or ""
    values: set[int] = set()
    for match in RANGE_RE.finditer(text):
        start = int(match.group(1) or match.group(3))
        end = int(match.group(2) or match.group(4))
        if start <= end and end - start <= 100:
            values.update(range(start, end + 1))
        else:
            values.update((start, end))
    values.update(int(value) for value in REF_RE.findall(text))
    return values


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir")
    parser.add_argument("--output", help="Report path; defaults to review_lint_report.json in the project")
    args = parser.parse_args(argv)

    project = Path(args.project_dir).expanduser().resolve()
    issues: list[dict] = []
    rows: dict[str, list[dict]] = {}
    for filename, fields in CSV_SCHEMAS.items():
        if filename in OPTIONAL_FILES and not (project / filename).exists():
            rows[filename] = []
            continue
        rows[filename] = read_rows(project / filename, fields, issues)
    for filename in ("metadata.json", "review_draft.md"):
        if not (project / filename).exists():
            issues.append({"severity": "error", "file": filename, "message": "missing required file"})

    screening = rows["screening.csv"]
    evidence = rows["evidence_table.csv"]
    reference_map = rows["reference_map.csv"]
    claims = rows["claim_registry.csv"]
    bibliometrics = rows.get("bibliometrics.csv", [])

    unique_check(screening, "record_id", "screening.csv", issues)
    unique_check(evidence, "record_id", "evidence_table.csv", issues)
    unique_check(reference_map, "ref_no", "reference_map.csv", issues)
    unique_check(claims, "claim_id", "claim_registry.csv", issues)
    unique_check(bibliometrics, "record_id", "bibliometrics.csv", issues)

    for row in screening:
        decision = cell(row, "final_decision")
        if decision not in {"keep", "exclude"}:
            issues.append({"severity": "error", "file": "screening.csv", "message": f"{cell(row, 'record_id')} has invalid final_decision: {decision}"})

    keep_ids = {cell(row, "record_id") for row in screening if cell(row, "final_decision") == "keep"}
    evidence_ids = {cell(row, "record_id") for row in evidence if cell(row, "record_id")}
    missing_evidence = sorted(keep_ids - evidence_ids)
    if missing_evidence:
        issues.append({"severity": "error", "file": "evidence_table.csv", "message": f"kept records missing evidence: {missing_evidence}"})

    unknown_evidence = sorted(evidence_ids - keep_ids)
    if unknown_evidence:
        issues.append({"severity": "error", "file": "evidence_table.csv", "message": f"evidence for non-kept records: {unknown_evidence}"})

    map_ids = {cell(row, "record_id") for row in reference_map if cell(row, "record_id")}
    unknown_map = sorted(map_ids - keep_ids)
    if unknown_map:
        issues.append({"severity": "error", "file": "reference_map.csv", "message": f"references for non-kept records: {unknown_map}"})
    missing_map = sorted(keep_ids - map_ids)
    if missing_map:
        issues.append({"severity": "error", "file": "reference_map.csv", "message": f"kept records missing reference mapping: {missing_map}"})

    if screening and not rows["search_log.csv"]:
        issues.append({"severity": "warning", "file": "search_log.csv", "message": "screening has candidates but search_log.csv is empty"})
    for row in screening:
        if not cell(row, "candidate_source"):
            issues.append({"severity": "warning", "file": "screening.csv", "message": f"{cell(row, 'record_id')} has no candidate_source"})

    for row in screening:
        if cell(row, "final_decision") == "exclude" and not cell(row, "screening_reason"):
            issues.append({"severity": "warning", "file": "screening.csv", "message": f"{cell(row, 'record_id')} excluded without a screening reason"})

    for row in evidence:
        if cell(row, "evidence_strength") == "partial":
            checked = cell(row, "evidence_checked").lower()
            if "verified" not in checked or "not_verified" not in checked:
                issues.append({"severity": "warning", "file": "evidence_table.csv", "message": f"{cell(row, 'record_id')} partial evidence should separate verified and not_verified"})
        if not cell(row, "evidence_locator"):
            issues.append({"severity": "warning", "file": "evidence_table.csv", "message": f"{cell(row, 'record_id')} has no evidence_locator"})

    ref_numbers: set[int] = set()
    for row in reference_map:
        match = re.fullmatch(r"\[(\d+)\]", cell(row, "ref_no"))
        if match:
            ref_numbers.add(int(match.group(1)))
        elif cell(row, "ref_no"):
            issues.append({"severity": "error", "file": "reference_map.csv", "message": f"invalid ref_no: {row.get('ref_no')}"})

    map_by_record = {cell(row, "record_id"): cell(row, "ref_no") for row in reference_map if cell(row, "record_id")}
    for row in evidence:
        record_id = cell(row, "record_id")
        mapped_ref = map_by_record.get(record_id)
        if mapped_ref is None:
            issues.append({"severity": "error", "file": "reference_map.csv", "message": f"{record_id} missing from reference_map"})
        elif mapped_ref != cell(row, "ref_no"):
            issues.append({"severity": "error", "file": "reference_map.csv", "message": f"{record_id} ref_no mismatch: evidence={cell(row, 'ref_no')}, map={mapped_ref}"})

    for row in rows["comparison_matrix.csv"]:
        for column in ("ref_a", "ref_b"):
            unknown = sorted(refs_in(cell(row, column)) - ref_numbers)
            if unknown:
                issues.append({"severity": "error", "file": "comparison_matrix.csv", "message": f"{cell(row, 'comparison_id')} has unknown {column}: {unknown}"})

    for row in claims:
        mentioned = refs_in(" ".join(cell(row, key) for key in ("supporting_refs", "contradicting_refs", "evidence_locators")))
        unknown = sorted(mentioned - ref_numbers)
        if unknown:
            issues.append({"severity": "error", "file": "claim_registry.csv", "message": f"{row.get('claim_id', '')} cites unknown refs: {unknown}"})

    if bibliometrics:
        bio_ids = {cell(row, "record_id") for row in bibliometrics if cell(row, "record_id")}
        unknown_bio = sorted(bio_ids - keep_ids)
        if unknown_bio:
            issues.append({"severity": "error", "file": "bibliometrics.csv", "message": f"bibliometrics for non-kept records: {unknown_bio}"})
        missing_bio = sorted(keep_ids - bio_ids)
        if missing_bio:
            issues.append({"severity": "warning", "file": "bibliometrics.csv", "message": f"kept records missing bibliometrics: {missing_bio}"})
        for row in bibliometrics:
            status = cell(row, "bibliometric_status")
            if status not in {"verified", "partial", "not_verified", "not_applicable"}:
                issues.append({"severity": "error", "file": "bibliometrics.csv", "message": f"{cell(row, 'record_id')} has invalid bibliometric_status: {status}"})
            citation = cell(row, "citation_count")
            if citation and (not citation.isdigit() or int(citation) < 0):
                issues.append({"severity": "error", "file": "bibliometrics.csv", "message": f"{cell(row, 'record_id')} has invalid citation_count: {citation}"})
            if citation and not cell(row, "citation_as_of"):
                issues.append({"severity": "warning", "file": "bibliometrics.csv", "message": f"{cell(row, 'record_id')} has citation_count without citation_as_of"})

    draft_path = project / "review_draft.md"
    if draft_path.exists():
        try:
            cited = refs_in(draft_path.read_text(encoding="utf-8"))
            unknown = sorted(cited - ref_numbers)
            if unknown:
                issues.append({"severity": "error", "file": "review_draft.md", "message": f"draft cites unknown refs: {unknown}"})
        except (OSError, UnicodeError) as exc:
            issues.append({"severity": "error", "file": "review_draft.md", "message": f"cannot read draft: {exc}"})

    metadata_path = project / "metadata.json"
    if metadata_path.exists():
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            expected = {
                "candidate_count": len(screening),
                "keep_count": len(keep_ids),
                "exclude_count": sum(1 for row in screening if cell(row, "final_decision") == "exclude"),
                "strong_count": sum(1 for row in evidence if cell(row, "evidence_strength") == "strong"),
                "partial_count": sum(1 for row in evidence if cell(row, "evidence_strength") == "partial"),
            }
            for key, actual in expected.items():
                declared = metadata.get(key)
                if isinstance(declared, int) and declared not in (0, actual):
                    issues.append({"severity": "warning", "file": "metadata.json", "message": f"{key}={declared} but current rows imply {actual}"})
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            issues.append({"severity": "error", "file": "metadata.json", "message": f"invalid JSON: {exc}"})

    errors = sum(1 for issue in issues if issue["severity"] == "error")
    warnings = sum(1 for issue in issues if issue["severity"] == "warning")
    report = {
        "project_dir": str(project),
        "status": "pass" if errors == 0 else "fail",
        "summary": {"errors": errors, "warnings": warnings},
        "checks": {
            "screening_rows": len(screening),
            "evidence_rows": len(evidence),
            "reference_rows": len(reference_map),
            "claim_rows": len(claims),
            "required_files": len(REQUIRED_FILES),
        },
        "issues": issues,
    }
    report_path = Path(args.output).expanduser().resolve() if args.output else project / "review_lint_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
