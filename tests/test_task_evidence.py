# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/eval-author-task-create/scripts"
sys.path.insert(0, str(SCRIPTS))
evidence = importlib.import_module("task_evidence")
pipeline = importlib.import_module("task_pipeline")


def write(path, value):
    path.write_text(json.dumps(value))
    return path


@pytest.fixture
def prepared(tmp_path, monkeypatch):
    # Generic receipt invariants use a synthetic runtime; native Gym is tested separately.
    import harbor.models.task.task

    monkeypatch.setattr(harbor.models.task.task, "Task", lambda path: SimpleNamespace(checksum="synthetic"))
    monkeypatch.setattr(evidence, "native_identity", lambda native, manifest: native["rollout_id"])
    task = tmp_path / "cover-read"
    task.mkdir()
    (task / "instruction.md").write_text("Read the record and return its total.")
    contract = {
        "task_id": "cover-read",
        "provider": "harbor",
        "native_run_id": "/rollout_id",
        "alternative_not_applicable": "This fixture has a single numeric output.",
        "side_effect_not_applicable": "This task only returns a value.",
        "cases": {},
    }
    for kind, reward in [("reference", 1), ("incorrect", 0), ("agent", 1)]:
        contract["cases"][kind] = {
            "kind": kind,
            "requirement": "Return the correct total.",
            "health": [{"pointer": "/error", "equals": None}],
            "checks": [{"pointer": "/reward", "min": reward, "max": reward}],
        }
    manifest = tmp_path / "manifest.json"
    contract_path = write(tmp_path / "contract.json", contract)
    evidence.prepare(task, contract_path, manifest)
    return task, contract_path, manifest


def execute(tmp_path, manifest, kind, run_id, *, reward=1, error=None, missing=False, command=None):
    result = tmp_path / f"{run_id}-native.json"
    receipt = tmp_path / f"{run_id}-receipt.json"
    trace = tmp_path / f"{run_id}-atif.json" if kind == "agent" else None
    payload = {"rollout_id": run_id, "reward": reward, "error": error}
    if missing:
        del payload["reward"]
    code = f"from pathlib import Path; Path({str(result)!r}).write_text({json.dumps(payload)!r})"
    if trace:
        code += f"; Path({str(trace)!r}).write_text({json.dumps({'session_id': run_id})!r})"
    evidence.run(manifest, kind, run_id, receipt, result, trace, command or [sys.executable, "-c", code])
    return receipt


def complete(tmp_path, manifest):
    return [
        execute(tmp_path, manifest, "reference", "reference"),
        execute(tmp_path, manifest, "incorrect", "incorrect", reward=0),
        execute(tmp_path, manifest, "agent", "repeat-1"),
        execute(tmp_path, manifest, "agent", "repeat-2"),
    ]


def reports(tmp_path):
    before = write(
        tmp_path / "before.json",
        {"uncovered_items": [{"name": "read", "kind": "tool", "reason": "not_covered_by_any_input_report"}]},
    )
    after = []
    for run_id in ("repeat-1", "repeat-2"):
        after.append(
            write(
                tmp_path / f"{run_id}-report.json",
                {
                    "covered": ["read"],
                    "uncovered": [],
                    "input_reports": [
                        {
                            "item_kind": "tool",
                            "covered": ["read"],
                            "subject": {
                                "task_id": "cover-read",
                                "run_id": run_id,
                                "trace": str(tmp_path / f"{run_id}-atif.json"),
                            },
                        }
                    ],
                },
            )
        )
    return before, after


def test_acceptance_requires_controls_and_exact_agent_evidence(tmp_path, prepared):
    _, _, manifest = prepared
    receipts = complete(tmp_path, manifest)
    before, after = reports(tmp_path)
    code, verdict = pipeline._verify(before, after, "read", receipts)
    assert code == 0 and verdict["accepted"] and verdict["coverage_closed"]
    with pytest.raises(pipeline.PipelineError, match="execution receipts"):
        pipeline._verify(before, after, "read")
    with pytest.raises(pipeline.PipelineError, match="every declared control"):
        pipeline._verify(before, after, "read", receipts[1:])
    payload = evidence.read(after[1])
    payload["covered"] = []
    payload["uncovered"] = ["read"]
    payload["input_reports"][0]["covered"] = []
    write(after[1], payload)
    code, verdict = pipeline._verify(before, after, "read", receipts)
    assert code == 1 and not verdict["accepted"] and verdict["task_validation"] == "passed"


@pytest.mark.parametrize(
    "mutation,message",
    [
        ("task", "task revision changed"),
        ("native", "native result digest"),
        ("trace", "trace is changed"),
        ("manifest", "manifest digest"),
        ("wrong_task", "subject.task_id"),
        ("wrong_trace", "subject.trace"),
        ("run_id", "must match all supplied"),
        ("mixed_runs", "exactly one agent run"),
    ],
)
def test_rejects_stale_or_unrelated_evidence(tmp_path, prepared, mutation, message):
    task, _, manifest = prepared
    receipts = complete(tmp_path, manifest)
    before, after = reports(tmp_path)
    if mutation == "task":
        (task / "instruction.md").write_text("Changed task")
    elif mutation == "native":
        (tmp_path / "repeat-1-native.json").write_text("{}")
    elif mutation == "trace":
        (tmp_path / "repeat-1-atif.json").write_text("{}")
    elif mutation == "manifest":
        manifest.write_text(manifest.read_text() + "\n")
    else:
        payload = evidence.read(after[0])
        subject = payload["input_reports"][0]["subject"]
        if mutation == "wrong_task":
            subject["task_id"] = "unrelated"
        elif mutation == "wrong_trace":
            subject["trace"] = str(tmp_path / "repeat-2-atif.json")
        elif mutation == "run_id":
            subject["run_id"] = "unrelated"
        else:
            payload["input_reports"].append({"subject": {**subject, "run_id": "unrelated"}})
        write(after[0], payload)
    with pytest.raises(pipeline.PipelineError, match=message):
        pipeline._verify(before, after, "read", receipts)


@pytest.mark.parametrize(
    "kwargs,status",
    [
        ({"reward": 0}, "behavior_failed"),
        ({"error": "setup failed"}, "infrastructure_error"),
        ({"missing": True}, "infrastructure_error"),
        ({"command": [sys.executable, "-c", "raise SystemExit(2)"]}, "infrastructure_error"),
    ],
)
def test_failed_behavior_is_distinct_from_missing_or_broken_evidence(tmp_path, prepared, kwargs, status):
    receipt = execute(tmp_path, prepared[2], "reference", "bad", **kwargs)
    assert evidence.read(receipt)["status"] == status
    with pytest.raises(evidence.EvidenceError, match="not passed"):
        evidence.verify_receipts([receipt], "cover-read")


def test_preexisting_results_cannot_be_adopted_as_fresh_execution(tmp_path, prepared):
    (tmp_path / "old-native.json").write_text("{}")
    with pytest.raises(evidence.EvidenceError, match="must be new"):
        execute(tmp_path, prepared[2], "reference", "old")


def test_repair_requires_fresh_proof_and_preserves_bounded_history(tmp_path, prepared):
    task, contract, manifest = prepared
    receipts = complete(tmp_path, manifest)
    for index in range(3):
        (task / "instruction.md").write_text(f"Clarified requirement {index}")
        next_manifest = tmp_path / f"manifest-{index}.json"
        evidence.prepare(task, contract, next_manifest, manifest, "instruction_ambiguity: clarify visible requirement")
        manifest = next_manifest
    with pytest.raises(evidence.EvidenceError, match="task revision changed"):
        evidence.verify_receipts(receipts, "cover-read")
    with pytest.raises(evidence.EvidenceError, match="budget exhausted"):
        evidence.prepare(task, contract, tmp_path / "fourth.json", manifest, "another repair")
    (tmp_path / "manifest.json").write_text("{}")
    with pytest.raises(evidence.EvidenceError, match="superseded manifest changed"):
        evidence.manifest_at(manifest)


def test_harbor_native_identity_checks_revision_and_exceptions():
    manifest = {"contract": {"provider": "harbor", "native_run_id": "/id"}, "harbor_task_checksum": "expected"}
    native = {"id": "trial", "task_checksum": "expected", "exception_info": None}
    assert evidence.native_identity(native, manifest) == "trial"
    for changed, match in [({"task_checksum": "wrong"}, "checksum"), ({"exception_info": {}}, "exception")]:
        with pytest.raises(evidence.EvidenceError, match=match):
            evidence.native_identity({**native, **changed}, manifest)


def test_duplicate_native_run_cannot_be_renamed_into_a_repeat(tmp_path, prepared):
    receipts = complete(tmp_path, prepared[2])
    result = tmp_path / "repeat-2-native.json"
    native = evidence.read(result)
    native["rollout_id"] = "repeat-1"
    write(result, native)
    receipt = evidence.read(receipts[-1])
    receipt["native_run_id"] = "repeat-1"
    receipt["result_sha256"] = evidence.digest(result)
    write(receipts[-1], receipt)
    with pytest.raises(evidence.EvidenceError, match="native run identity is changed or reused"):
        evidence.verify_receipts(receipts, "cover-read")


def test_task_edit_during_execution_invalidates_receipt(tmp_path, prepared):
    task, _, manifest = prepared
    receipt = execute(
        tmp_path,
        manifest,
        "reference",
        "mutation",
        command=[
            sys.executable,
            "-c",
            f'from pathlib import Path; Path({str(task / "instruction.md")!r}).write_text("changed")',
        ],
    )
    assert evidence.read(receipt)["status"] == "infrastructure_error"
    assert "task revision changed" in evidence.read(receipt)["error"]


def test_contract_demands_applicable_control_decisions(tmp_path, prepared):
    task, contract_path, _ = prepared
    contract = evidence.read(contract_path)
    del contract["alternative_not_applicable"]
    write(contract_path, contract)
    with pytest.raises(evidence.EvidenceError, match="include alternative case"):
        evidence.prepare(task, contract_path, tmp_path / "new.json")


def test_diagnostic_cannot_replace_reference_control(tmp_path, prepared):
    task, contract_path, _ = prepared
    contract = evidence.read(contract_path)
    contract["cases"]["probe"] = {**contract["cases"]["reference"], "kind": "diagnostic"}
    write(contract_path, contract)
    manifest = tmp_path / "with-diagnostic.json"
    evidence.prepare(task, contract_path, manifest)
    receipt = execute(tmp_path, manifest, "probe", "probe")
    with pytest.raises(evidence.EvidenceError, match="diagnostic or unknown"):
        evidence.verify_receipts([receipt], "cover-read")


def test_numeric_bands_and_missing_health_are_distinct():
    assert evidence.assertions({"score": 0.8}, [{"pointer": "/score", "min": 0.7, "max": 1}])
    assert not evidence.assertions({"score": True}, [{"pointer": "/score", "min": 0, "max": 1}])
    with pytest.raises(evidence.EvidenceError, match="missing result field"):
        evidence.assertions({}, [{"pointer": "/error", "equals": None}])
