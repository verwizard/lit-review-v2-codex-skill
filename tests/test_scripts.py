from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
import unittest
import uuid
from contextlib import contextmanager
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from scripts.schema import CSV_SCHEMAS, OPTIONAL_FILES
from scripts.review_lint import refs_in


def write_csv(project: Path, filename: str, rows: list[dict[str, object]]) -> None:
    path = project / filename
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_SCHEMAS[filename])
        writer.writeheader()
        writer.writerows(rows)


def empty_row(filename: str) -> dict[str, object]:
    return {field: "" for field in CSV_SCHEMAS[filename]}


def create_fixture(
    project: Path,
    *,
    evidence_strength: str = "strong",
    evidence_checked: str = "Full fixture source checked.",
    include_evidence: bool = True,
    include_reference_map: bool = True,
    include_bibliometrics: bool = True,
    draft: str = "# Fixture review\n",
    metadata_overrides: dict[str, object] | None = None,
) -> None:
    project.mkdir(parents=True, exist_ok=True)

    screening = empty_row("screening.csv")
    screening.update(
        {
            "record_id": "R01",
            "study_id": "S01",
            "title": "Fixture study",
            "authors": "Fixture author",
            "year": "2026",
            "venue": "Fixture venue",
            "document_type": "journal paper",
            "candidate_source": "fixture",
            "retrieval_date": "2026-01-01",
            "pass_a_decision": "keep",
            "pass_b_decision": "keep",
            "final_decision": "keep",
        }
    )
    write_csv(project, "screening.csv", [screening])

    if include_evidence:
        evidence = empty_row("evidence_table.csv")
        evidence.update(
            {
                "record_id": "R01",
                "study_id": "S01",
                "ref_no": "[1]",
                "cite_key": "Fixture2026",
                "title": "Fixture study",
                "authors": "Fixture author",
                "year": "2026",
                "venue": "Fixture venue",
                "technical_route": "fixture route",
                "evidence_strength": evidence_strength,
                "evidence_checked": evidence_checked,
                "evidence_locator": "fixture locator",
                "methodological_quality": "moderate",
            }
        )
        write_csv(project, "evidence_table.csv", [evidence])
    else:
        write_csv(project, "evidence_table.csv", [])

    if include_reference_map:
        reference = empty_row("reference_map.csv")
        reference.update(
            {
                "ref_no": "[1]",
                "record_id": "R01",
                "study_id": "S01",
                "cite_key": "Fixture2026",
                "title": "Fixture study",
                "authors": "Fixture author",
                "year": "2026",
                "venue": "Fixture venue",
                "version_relation": "independent",
                "evidence_strength": evidence_strength,
                "methodological_quality": "moderate",
            }
        )
        write_csv(project, "reference_map.csv", [reference])
    else:
        write_csv(project, "reference_map.csv", [])

    for filename in CSV_SCHEMAS:
        if filename in {"screening.csv", "evidence_table.csv", "reference_map.csv"}:
            continue
        if filename in OPTIONAL_FILES and not include_bibliometrics:
            continue
        if filename == "search_log.csv":
            search = empty_row(filename)
            search.update(
                {
                    "search_id": "Q01",
                    "search_mode": "targeted",
                    "source": "fixture",
                    "query_or_seed": "fixture query",
                    "search_date": "2026-01-01",
                    "start_year": "2026",
                    "end_year": "2026",
                    "stopping_rule_note": "fixture stop",
                }
            )
            write_csv(project, filename, [search])
        else:
            write_csv(project, filename, [])

    metadata = {
        "name": project.name,
        "topic": "Fixture topic",
        "start_year": 2026,
        "end_year": 2026,
        "cutoff_date": "2026-12-31",
        "candidate_count": 1,
        "keep_count": 1,
        "exclude_count": 0,
        "strong_count": 1 if evidence_strength == "strong" else 0,
        "partial_count": 1 if evidence_strength == "partial" else 0,
    }
    metadata.update(metadata_overrides or {})
    (project / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (project / "review_draft.md").write_text(draft, encoding="utf-8")


def run_lint(project: Path) -> tuple[int, dict]:
    report_path = project / "test_lint_report.json"
    result = subprocess.run(
        [
            sys.executable,
            str(PACKAGE_ROOT / "scripts" / "review_lint.py"),
            str(project),
            "--output",
            str(report_path),
        ],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, json.loads(report_path.read_text(encoding="utf-8"))


@contextmanager
def temporary_directory():
    """Use a UUID directory for restricted Windows runtimes."""
    directory = PACKAGE_ROOT / f".test-tmp-{uuid.uuid4().hex}"
    directory.mkdir()
    try:
        yield str(directory)
    finally:
        shutil.rmtree(directory, ignore_errors=True)


class ReviewLintTests(unittest.TestCase):
    def test_reference_ranges_expand_and_unknown_range_refs_fail(self) -> None:
        self.assertEqual(refs_in("[1]–[3], [7]"), {1, 2, 3, 7})
        self.assertEqual(refs_in("[1-3], [7]"), {1, 2, 3, 7})
        with temporary_directory() as directory:
            project = Path(directory) / "range-fixture"
            create_fixture(project, draft="# Fixture review\nClaim [1]–[3].\n")
            code, report = run_lint(project)
        self.assertEqual(code, 1)
        self.assertTrue(
            any(
                issue["file"] == "review_draft.md"
                and "unknown refs" in issue["message"]
                for issue in report["issues"]
            )
        )

    def test_partial_evidence_requires_both_labels(self) -> None:
        with temporary_directory() as directory:
            incomplete = Path(directory) / "incomplete"
            create_fixture(
                incomplete,
                evidence_strength="partial",
                evidence_checked="not_verified: fixture details were not checked.",
            )
            code_incomplete, report_incomplete = run_lint(incomplete)

            complete = Path(directory) / "complete"
            create_fixture(
                complete,
                evidence_strength="partial",
                evidence_checked=(
                    "verified: fixture abstract checked. "
                    "not_verified: full table not checked."
                ),
            )
            code_complete, report_complete = run_lint(complete)

        self.assertEqual(code_incomplete, 0)
        self.assertTrue(
            any("partial evidence should separate" in issue["message"] for issue in report_incomplete["issues"])
        )
        self.assertEqual(code_complete, 0)
        self.assertFalse(
            any("partial evidence should separate" in issue["message"] for issue in report_complete["issues"])
        )

    def test_missing_evidence_mapping_is_an_error(self) -> None:
        with temporary_directory() as directory:
            project = Path(directory) / "missing-evidence"
            create_fixture(project, include_evidence=False)
            code, report = run_lint(project)
        self.assertEqual(code, 1)
        self.assertTrue(any("kept records missing evidence" in issue["message"] for issue in report["issues"]))

    def test_missing_reference_mapping_is_an_error(self) -> None:
        with temporary_directory() as directory:
            project = Path(directory) / "missing-reference"
            create_fixture(project, include_reference_map=False)
            code, report = run_lint(project)
        self.assertEqual(code, 1)
        self.assertTrue(
            any("kept records missing reference mapping" in issue["message"] for issue in report["issues"])
        )

    def test_legacy_project_without_bibliometrics_passes(self) -> None:
        with temporary_directory() as directory:
            project = Path(directory) / "legacy"
            create_fixture(project, include_bibliometrics=False)
            code, report = run_lint(project)
        self.assertEqual(code, 0)
        self.assertEqual(report["summary"], {"errors": 0, "warnings": 0})

    def test_metadata_count_mismatch_is_a_warning(self) -> None:
        with temporary_directory() as directory:
            project = Path(directory) / "metadata-mismatch"
            create_fixture(project, metadata_overrides={"candidate_count": 2})
            code, report = run_lint(project)
        self.assertEqual(code, 0)
        self.assertTrue(
            any(
                issue["file"] == "metadata.json" and "candidate_count=2" in issue["message"]
                for issue in report["issues"]
            )
        )


if __name__ == "__main__":
    unittest.main()
