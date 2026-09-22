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


def test_native_proposal_scaffold_and_discovery(tmp_path):
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
    discovery = subprocess.run(
        [
            sys.executable,
            str(ROOT / "skills/eval-author-discover/scripts/discover.py"),
            "--provider",
            "gym",
            "--gym-python",
            GYM_PYTHON,
            "--repo",
            str(output),
        ],
        capture_output=True,
        text=True,
    )
    evidence = json.loads(discovery.stdout)
    assert evidence["manifests"][0]["validation"] == "manifest_validated", evidence
    assert evidence["manifests"][0]["validation_evidence"]["evidence"]["datasets"][0]["rows"] == 1
    assert not evidence["runnable"] and discovery.returncode == 1
    # Static validation must also fail when the dataset goes missing.
    (output / "environments/cover_ledger_total/data/example.jsonl").unlink()
    discovery = subprocess.run(
        [
            sys.executable,
            str(ROOT / "skills/eval-author-discover/scripts/discover.py"),
            "--provider",
            "gym",
            "--gym-python",
            GYM_PYTHON,
            "--repo",
            str(output),
        ],
        capture_output=True,
        text=True,
    )
    assert json.loads(discovery.stdout)["manifests"][0]["validation"] == "failed"


def test_native_config_validation_preserves_missing_model_requirements(tmp_path, monkeypatch):
    assert GYM_PYTHON is not None
    variable = "EVAL_AUTHOR_TEST_MISSING_MODEL_KEY"
    monkeypatch.delenv(variable, raising=False)
    config = tmp_path / "config.yaml"
    config.write_text(
        "policy_model:\n  responses_api_models:\n    openai_model:\n"
        "      entrypoint: app.py\n      api_key: ${oc.env:" + variable + "}\n"
    )
    result = subprocess.run(
        [
            GYM_PYTHON,
            str(ROOT / "skills/eval-author-discover/scripts/providers/gym/validate.py"),
            "--repo",
            str(tmp_path),
            "--config",
            str(config),
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    evidence = json.loads(result.stdout)
    assert result.returncode == 1 and evidence["status"] == "failed"
    assert "runtime_readiness" not in evidence


def test_native_http_controls_loader_and_audit_gaps(tmp_path):
    """Exercise real tool HTTP calls, retained Gym traces, and unchanged coverage semantics."""
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
    audit = tmp_path / "audit.md"
    specification = {
        "schema": "nemo.eval_author.audit.v1",
        "agent": "scripted-control",
        "status": "draft",
        "items": [
            {
                "kind": "tool",
                "name": name,
                "description": name,
                "expected_use": "When requested by the synthetic ledger task",
                "expected_failure_behavior": "Report the failure without claiming completion",
                "evidence_required": [{"kind": "tool_call", "tool": name, "description": "Recorded tool call"}],
            }
            for name in ("ledger_total", "ledger_refund")
        ],
    }
    audit.write_text(
        "<!-- BEGIN:nemo-eval-author-audit:v1 -->\n```yaml\n"
        + json.dumps(specification)
        + "\n```\n<!-- END:nemo-eval-author-audit:v1 -->\n"
    )
    scripts = ROOT / "skills"

    def invoke(script, *args):
        result = subprocess.run(
            [sys.executable, str(script), *map(str, args)], capture_output=True, text=True, timeout=60
        )
        assert result.returncode == 0, result.stdout + result.stderr
        return json.loads(result.stdout)

    # Include every attempt, including failed controls; never condition coverage on reward.
    for source in (output / "rollouts.jsonl", output / "cli-rollouts.jsonl"):
        source_rows = [json.loads(line) for line in source.read_text().splitlines()]
        for row_number in range(1, len(source_rows) + 1):
            normalized = tmp_path / f"normalized-{source.stem}-{row_number}"
            invoke(
                scripts / "gym-to-atif/scripts/load_gym_trace.py",
                "--input",
                source,
                "--row",
                row_number,
                "--output-dir",
                normalized,
            )
            receipt = json.loads((normalized / "loading.json").read_text())
            assert receipt["selected_line"] == row_number and not receipt["atif_emitted"]
            trace = json.loads((normalized / "trace.normalized.json").read_text())
            assert trace["id"] == source_rows[row_number - 1]["ng_trajectory"]["rollout_id"]
            # Scripted endpoint supplies no captured model bodies; unresolved references stay explicit.
            assert trace["attributes"].get("gym_loader_gaps")
            atif = tmp_path / f"atif-{source.stem}-{row_number}"
            invoke(
                scripts / "gym-to-atif/scripts/gym_to_atif.py",
                "--input",
                source,
                "--row",
                row_number,
                "--output-dir",
                atif,
            )
            invoke(
                scripts / "eval-author-audit/scripts/audit_spec/measure.py",
                "--audit",
                audit,
                "--trace",
                atif / "trace.atif.json",
                "--out-dir",
                tmp_path / "measurements",
                "--task-id",
                "ledger",
                "--run-id",
                f"control-{source.stem}-{row_number}",
            )
    report = tmp_path / "coverage-report.json"
    invoke(
        scripts / "eval-author-audit/scripts/audit_spec/report.py",
        "--audit",
        audit,
        "--coverage-dir",
        tmp_path / "measurements",
        "--out",
        report,
    )
    aggregate = json.loads(report.read_text())
    assert {item["name"] for item in aggregate["uncovered_items"]} == {"ledger_refund"}
    selected = invoke(scripts / "eval-author-task-create/scripts/task_pipeline.py", "select", "--report", report)
    assert [item["name"] for item in selected["actionable_tools"]] == ["ledger_refund"]
