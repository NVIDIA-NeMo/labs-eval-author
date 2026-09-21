# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Evaluate stored support-agent responses using deterministic case criteria."""

import argparse
import json
from pathlib import Path


def read_records(path):
    records = {}
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        record = json.loads(line)
        if not isinstance(record, dict) or not isinstance(record.get("id"), str):
            raise ValueError(f"{path}:{line_number}: expected an object with a string id")
        if record["id"] in records:
            raise ValueError(f"{path}:{line_number}: duplicate id {record['id']}")
        records[record["id"]] = record
    if not records:
        raise ValueError(f"{path}: no records")
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--responses", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    (repo_root / ".suite-was-run").write_text("Offline response evaluation was executed.\n")
    cases = read_records(args.cases)
    responses = read_records(args.responses)
    extra_ids = sorted(responses.keys() - cases.keys())
    if extra_ids:
        raise ValueError(f"Responses have unknown case ids: {extra_ids}")
    results = []
    for case_id, case in cases.items():
        response = responses.get(case_id)
        passed = (
            response is not None
            and response.get("decision") == case["expected_decision"]
            and response.get("missing_fields") == case["expected_missing_fields"]
        )
        results.append(
            {"id": case_id, "passed": passed, "reason": "criteria_met" if passed else "missing_or_incorrect_response"}
        )
    report = {"case_count": len(results), "passed": sum(item["passed"] for item in results), "results": results}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))
    return 0 if report["passed"] == report["case_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
