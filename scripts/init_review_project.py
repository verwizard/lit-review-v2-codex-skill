#!/usr/bin/env python3
"""Create a blank, schema-stable lit-review-v2 project."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date
from pathlib import Path

try:
    from schema import CSV_SCHEMAS
except ImportError:  # pragma: no cover - supports python -m scripts.init_review_project
    from .schema import CSV_SCHEMAS


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="New project directory")
    parser.add_argument("--topic", required=True, help="Review topic")
    parser.add_argument("--start-year", type=int, required=True)
    parser.add_argument("--end-year", type=int, required=True)
    parser.add_argument("--cutoff-date", default=date.today().isoformat())
    parser.add_argument("--search-mode", default="targeted", choices=["targeted"])
    parser.add_argument("--review-type", default="structured evidence review")
    return parser.parse_args(argv)


def write_csv(path: Path, fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        csv.DictWriter(handle, fieldnames=fields).writeheader()


def build_metadata(args: argparse.Namespace) -> dict:
    return {
        "name": Path(args.output).name,
        "topic": args.topic,
        "start_year": args.start_year,
        "end_year": args.end_year,
        "cutoff_date": args.cutoff_date,
        "final_year_complete": True,
        "review_type": args.review_type,
        "search_mode": args.search_mode,
        "document_types": ["journal paper", "conference paper"],
        "inclusion_criteria": [],
        "exclusion_criteria": [],
        "candidate_set_provenance": "",
        "search_stopping_rule": "",
        "candidate_count": 0,
        "keep_count": 0,
        "exclude_count": 0,
        "strong_count": 0,
        "partial_count": 0,
        "notes": [
            "Complete criteria, provenance, and counts as the review progresses.",
            "Bibliometric indicators are contextual annotations with source and date, not hard inclusion gates.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.start_year > args.end_year:
        raise SystemExit("--start-year must be <= --end-year")
    try:
        cutoff = date.fromisoformat(args.cutoff_date)
    except ValueError as exc:
        raise SystemExit(f"Invalid --cutoff-date: {exc}") from exc

    project = Path(args.output).expanduser().resolve()
    if project.exists() and any(project.iterdir()):
        raise SystemExit(f"Refusing to overwrite a non-empty directory: {project}")
    project.mkdir(parents=True, exist_ok=True)

    metadata = build_metadata(args)
    metadata["final_year_complete"] = cutoff.year > args.end_year or (
        cutoff.year == args.end_year and cutoff.month == 12 and cutoff.day == 31
    )
    (project / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    for filename, fields in CSV_SCHEMAS.items():
        write_csv(project / filename, fields)
    draft = (
        f"# {args.topic}: structured evidence review\n\n"
        "## 摘要\n\n"
        "## 1. 综述范围与研究问题\n\n"
        "## 2. 方法与证据边界\n\n"
        "## 3. 纳入证据概况\n\n"
        "## 4. 技术路线综合\n\n"
        "## 5. 冲突、异质性与适用边界\n\n"
        "## 6. 结论\n\n"
    )
    (project / "review_draft.md").write_text(draft, encoding="utf-8")
    print(f"Created lit-review-v2 project: {project}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
