# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Integration checks against a separately installed, real Gym runtime."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GYM_PYTHON = os.environ.get("EVAL_AUTHOR_GYM_PYTHON")
pytestmark = pytest.mark.skipif(not GYM_PYTHON, reason="set EVAL_AUTHOR_GYM_PYTHON to an installed Gym v0.6.0+ runtime")


def scaffold_draft(tmp_path):
    assert GYM_PYTHON is not None
    proposals = tmp_path / ".eval-author/proposals"
    proposals.mkdir(parents=True)
    instruction = proposals / "cover-ledger-total-instruction.md"
    instruction.write_text("Use ledger_total to total the supplied ledger and report the amount.")
    report = tmp_path / "coverage.json"
    report.write_text(
        json.dumps(
            {"uncovered_items": [{"kind": "tool", "name": "ledger_total", "reason": "not_covered_by_any_input_report"}]}
        )
    )
    output = tmp_path / ".eval-author/task-drafts/cover-ledger-total"
    command = [
        sys.executable,
        str(ROOT / "skills/eval-author-task-create/scripts/task_pipeline.py"),
        "scaffold",
        "--provider",
        "gym",
        "--gym-python",
        GYM_PYTHON,
        "--report",
        str(report),
        "--target",
        "ledger_total",
        "--out",
        str(output),
        "--task-name",
        "example/cover-ledger-total",
        "--description",
        "Test ledger summation",
        "--author",
        "Eval Author test fixture",
        "--instruction-file",
        str(instruction),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    receipt = json.loads(result.stdout)
    return output, instruction, command, receipt


def test_native_proposal_scaffold_and_validation(tmp_path):
    assert GYM_PYTHON is not None
    output, instruction, command, receipt = scaffold_draft(tmp_path)
    assert receipt["provider"] == "gym" and receipt["written"]
    assert not receipt["runnable"]
    assert (output / "instruction.md").read_text() == instruction.read_text()
    row = json.loads((output / "environments/cover_ledger_total/data/example.jsonl").read_text())
    assert row["responses_create_params"]["input"][0]["content"] == instruction.read_text()
    before = (output / "draft.json").read_bytes()
    assert subprocess.run(command, capture_output=True).returncode != 0
    assert (output / "draft.json").read_bytes() == before
    validation_command = [
        str(Path(GYM_PYTHON).with_name("gym")),
        "env",
        "validate",
        "--manifest",
        str(output / "environments/cover_ledger_total/manifest.yaml"),
        "--json",
    ]
    validation = subprocess.run(validation_command, cwd=output, capture_output=True, text=True, timeout=60)
    assert validation.returncode == 0, validation.stdout + validation.stderr
    assert json.loads(validation.stdout)["datasets"][0]["rows"] == 1
    (output / "environments/cover_ledger_total/data/example.jsonl").unlink()
    validation = subprocess.run(validation_command, cwd=output, capture_output=True, text=True, timeout=60)
    assert validation.returncode != 0


def test_native_http_execution_controls(tmp_path):
    """Exercise real tool HTTP calls, native rollouts, and positive and negative controls."""
    assert GYM_PYTHON is not None
    draft, _, _, _ = scaffold_draft(tmp_path)
    resource_app = draft / "resources_servers/cover_ledger_total/app.py"
    resource_app.write_bytes((ROOT / "tests/fixtures/gym_ledger/app.py").read_bytes())
    (resource_app.parent / "tests/verifier_cases.jsonl").write_bytes(
        (ROOT / "tests/fixtures/gym_ledger/verifier_cases.jsonl").read_bytes()
    )
    dataset = draft / "environments/cover_ledger_total/data/example.jsonl"
    dataset.write_bytes((ROOT / "tests/fixtures/gym_ledger/data.jsonl").read_bytes())
    validation = subprocess.run(
        [
            str(Path(GYM_PYTHON).with_name("gym")),
            "env",
            "validate",
            "--manifest",
            str(draft / "environments/cover_ledger_total/manifest.yaml"),
            "--json",
        ],
        cwd=draft,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert validation.returncode == 0, validation.stdout + validation.stderr
    assert json.loads(validation.stdout)["datasets"][0]["rows"] == 2
    output = tmp_path / "controls"
    result = subprocess.run(
        [
            GYM_PYTHON,
            str(ROOT / "tests/fixtures/gym_ledger/smoke.py"),
            "--output",
            str(output),
            "--resources-app",
            str(resource_app),
            "--dataset",
            str(dataset),
        ],
        capture_output=True,
        text=True,
        timeout=90,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    summary = json.loads((output / "summary.json").read_text())
    assert summary["native_cli_rollouts"] == 4
    assert summary["verifier_cases"] == 6
    assert not summary["model_performance_measured"]
    quality = json.loads((output / "quality_summary.json").read_text())["run"]
    assert quality["ignored_checks"] == []
    assert quality["artifacts"]["records"] == 4
    # Scripted policies do not supply model captures; preserve the resulting unknown health.
    assert quality["verdicts"] == {"healthy": 0, "unhealthy": 0, "unobserved": 4}
    rows = [json.loads(line) for line in (output / "rollouts.jsonl").read_text().splitlines()]
    assert len(rows) == 8
    assert [row["reward"] for row in rows] == [1, 1, 1, 1, 0, 0, 0, 0]
    assert len({row["ng_trajectory"]["rollout_id"] for row in rows}) == 8
