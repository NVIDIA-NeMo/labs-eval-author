# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

_PLUGIN = Path(__file__).resolve().parents[1]
_SCRIPT = _PLUGIN / "skills" / "eval-author-task-create" / "scripts" / "task_pipeline.py"
_needs_harbor = pytest.mark.skipif(shutil.which("harbor") is None, reason="Harbor is not installed")


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    """Invoke ``task_pipeline.py`` with ``args`` and return the completed process."""
    return subprocess.run(
        [sys.executable, str(_SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _coverage_input_report(*, run_id: str, covered: list[str]) -> dict[str, Any]:
    """Build one aggregate ``input_reports`` entry for verify tests."""
    return {
        "path": f".eval-author/task-measurements/run={run_id}/tool_calls/coverage.json",
        "method": "tool_calls",
        "item_kind": "tool",
        "item_kind_count": max(len(covered), 1),
        "subject": {
            "trace": f".harbor/runs/trial/{run_id}/agent/trajectory.json",
            "trace_format": "atif",
            "task_id": "cover-read",
            "run_id": run_id,
        },
        "covered": covered,
        "covered_count": len(covered),
    }


def _write_report(
    path: Path,
    *,
    covered: list[str],
    uncovered: list[str],
    run_id: str | None = None,
) -> None:
    """Write a minimal aggregate coverage report JSON file for tests."""
    items = [
        {
            "name": name,
            "kind": "tool",
            "reason": "not_covered_by_any_input_report",
            "description": f"Use {name}.",
            "generation": {
                "focus": f"Exercise {name}.",
                "needed_tools": [name],
                "evidence_required": [{"kind": "tool_call", "tool": name}],
            },
        }
        for name in uncovered
    ]
    _write_report_with_items(path, covered=covered, uncovered_items=items, run_id=run_id)


def _write_report_with_items(
    path: Path,
    *,
    covered: list[str],
    uncovered_items: list[dict[str, Any]],
    run_id: str | None = None,
) -> None:
    """Write an aggregate coverage report with explicit ``uncovered_items`` entries."""
    uncovered = [str(item["name"]) for item in uncovered_items]
    payload: dict[str, Any] = {"covered": covered, "uncovered": uncovered, "uncovered_items": uncovered_items}
    if run_id is not None:
        payload["input_reports"] = [_coverage_input_report(run_id=run_id, covered=covered)]
    path.write_text(json.dumps(payload), encoding="utf-8")


def _load_task_pipeline_module():
    """Load ``task_pipeline.py`` as a module without putting scripts/ on ``sys.path``."""
    spec = importlib.util.spec_from_file_location("eval_author_task_pipeline", _SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load task pipeline module from {_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_task_slug_for_tool_is_deterministic() -> None:
    """Base slugs are stable for common runtime tool names."""
    task_slug_for_tool = _load_task_pipeline_module().task_slug_for_tool

    assert task_slug_for_tool("read") == "cover-read"
    assert task_slug_for_tool("customer.lookup") == "cover-customer-lookup"


def test_select_returns_task_slug_and_paths(tmp_path: Path) -> None:
    """Select attaches canonical artifact paths for one actionable tool gap."""
    report = tmp_path / "report.json"
    _write_report(report, covered=["write"], uncovered=["read"])
    payload = json.loads(_run("select", "--report", str(report)).stdout)
    assert payload["valid"] is True
    assert payload["actionable_tools"] == [
        {
            "description": "Use read.",
            "evidence_required": [{"kind": "tool_call", "tool": "read"}],
            "focus": "Exercise read.",
            "kind": "tool",
            "name": "read",
            "needed_tools": ["read"],
            "paths": {
                "draft": ".eval-author/task-drafts/cover-read",
                "measurements": ".eval-author/task-measurements/cover-read",
                "proposal": ".eval-author/proposals/cover-read-instruction.md",
                "task_id": "cover-read",
            },
            "reason": "not_covered_by_any_input_report",
            "task_slug": "cover-read",
        }
    ]


def test_select_assigns_deduped_slugs_for_colliding_tool_names(tmp_path: Path) -> None:
    """Colliding base and final slugs receive deterministic ``-2``, ``-3``, ... suffixes."""
    report = tmp_path / "report.json"
    _write_report(report, covered=[], uncovered=["server:foo", "server.foo"])
    payload = json.loads(_run("select", "--report", str(report)).stdout)
    slugs = {gap["name"]: gap["task_slug"] for gap in payload["actionable_tools"]}
    assert slugs == {
        "server.foo": "cover-server-foo",
        "server:foo": "cover-server-foo-2",
    }

    report_three = tmp_path / "report-three.json"
    _write_report(report_three, covered=[], uncovered=["server:foo", "server.foo-2", "server.foo"])
    payload_three = json.loads(_run("select", "--report", str(report_three)).stdout)
    slugs_three = {gap["name"]: gap["task_slug"] for gap in payload_three["actionable_tools"]}
    assert slugs_three == {
        "server.foo": "cover-server-foo",
        "server.foo-2": "cover-server-foo-2",
        "server:foo": "cover-server-foo-3",
    }


@_needs_harbor
def test_scaffold_uses_harbor_native_task_layout(tmp_path: Path) -> None:
    """Scaffold installs the proposal into a Harbor-native task draft layout."""
    report = tmp_path / "report.json"
    _write_report(report, covered=["write"], uncovered=["read"])
    proposals = tmp_path / ".eval-author" / "proposals"
    proposals.mkdir(parents=True)
    instruction = proposals / "cover-read-instruction.md"
    instruction.write_text("Read seed.txt and report its content.\n", encoding="utf-8")
    draft = tmp_path / ".eval-author" / "task-drafts" / "cover-read"

    result = _run(
        "scaffold",
        "--report",
        str(report),
        "--target",
        "read",
        "--out",
        str(draft),
        "--task-name",
        "example/cover-read",
        "--description",
        "Read a fixture file.",
        "--author",
        "Test Author",
        "--instruction-file",
        str(instruction),
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["task_slug"] == "cover-read"
    assert payload["paths"]["proposal"] == ".eval-author/proposals/cover-read-instruction.md"
    assert (draft / "instruction.md").read_text(encoding="utf-8") == instruction.read_text(encoding="utf-8")
    task_toml = (draft / "task.toml").read_text(encoding="utf-8")
    assert 'schema_version = "1.3"' in task_toml
    assert 'name = "example/cover-read"' in task_toml
    assert (draft / "environment" / "Dockerfile").is_file()
    assert (draft / "solution" / "solve.sh").is_file()
    assert (draft / "tests" / "test.sh").is_file()


def test_scaffold_rejects_mismatched_proposal_filename(tmp_path: Path) -> None:
    """Scaffold rejects proposal filenames that do not match the assigned task slug."""
    report = tmp_path / "report.json"
    _write_report(report, covered=["write"], uncovered=["read"])
    proposals = tmp_path / ".eval-author" / "proposals"
    proposals.mkdir(parents=True)
    instruction = proposals / "read-file-instruction.md"
    instruction.write_text("Read seed.txt and report its content.\n", encoding="utf-8")
    draft = tmp_path / ".eval-author" / "task-drafts" / "cover-read"

    result = _run(
        "scaffold",
        "--report",
        str(report),
        "--target",
        "read",
        "--out",
        str(draft),
        "--task-name",
        "example/cover-read",
        "--description",
        "Read a fixture file.",
        "--author",
        "Test Author",
        "--instruction-file",
        str(instruction),
    )
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["valid"] is False
    assert "cover-read-instruction.md" in payload["error"]


def test_verify_rejects_single_after_report(tmp_path: Path) -> None:
    """Verify requires at least two after-reports."""
    before = tmp_path / "before.json"
    first = tmp_path / "first.json"
    _write_report(before, covered=["write"], uncovered=["read"])
    _write_report(first, covered=["read"], uncovered=[])

    result = _run(
        "verify",
        "--before",
        str(before),
        "--after",
        str(first),
        "--target",
        "read",
    )
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["valid"] is False
    assert "at least 2 --after reports are required" in payload["error"]


def test_verify_rejects_duplicate_after_reports(tmp_path: Path) -> None:
    """Verify rejects duplicate after-report paths."""
    before = tmp_path / "before.json"
    first = tmp_path / "first.json"
    _write_report(before, covered=["write"], uncovered=["read"])
    _write_report(first, covered=["read"], uncovered=[])

    result = _run(
        "verify",
        "--before",
        str(before),
        "--after",
        str(first),
        "--after",
        str(first),
        "--target",
        "read",
    )
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["valid"] is False
    assert "distinct" in payload["error"]


def test_verify_rejects_copied_after_reports_with_same_run_id(tmp_path: Path) -> None:
    """Verify rejects two paths that record the same ATIF subject.run_id."""
    before = tmp_path / "before.json"
    first = tmp_path / "repeat-1-report.json"
    second = tmp_path / "repeat-1-copy-report.json"
    _write_report(before, covered=["write"], uncovered=["read"])
    _write_report(first, covered=["read"], uncovered=[], run_id="repeat-1")
    second.write_text(first.read_text(encoding="utf-8"), encoding="utf-8")

    result = _run(
        "verify",
        "--before",
        str(before),
        "--after",
        str(first),
        "--after",
        str(second),
        "--target",
        "read",
    )
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["valid"] is False
    assert "distinct ATIF subject.run_id" in payload["error"]


def test_verify_rejects_non_actionable_uncovered_item(tmp_path: Path) -> None:
    """Verify rejects targets that are uncovered but not actionable tool gaps."""
    before = tmp_path / "before.json"
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    _write_report_with_items(
        before,
        covered=["write"],
        uncovered_items=[
            {
                "name": "read",
                "kind": "tool",
                "reason": "not_covered_by_any_input_report",
                "description": "Use read.",
                "generation": {
                    "focus": "Exercise read.",
                    "needed_tools": ["read"],
                    "evidence_required": [{"kind": "tool_call", "tool": "read"}],
                },
            },
            {
                "name": "account_recovery",
                "kind": "capability",
                "reason": "not_measured_by_any_method",
                "description": "Recover account access.",
                "generation": {
                    "focus": "Exercise capability account_recovery.",
                    "needed_tools": ["read"],
                    "evidence_required": [],
                },
            },
        ],
    )
    _write_report(first, covered=["read"], uncovered=[], run_id="repeat-1")
    _write_report(second, covered=["read"], uncovered=[], run_id="repeat-1")

    result = _run(
        "verify",
        "--before",
        str(before),
        "--after",
        str(first),
        "--after",
        str(second),
        "--target",
        "account_recovery",
    )
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["valid"] is False
    assert "not an actionable uncovered tool" in payload["error"]


def test_verify_requires_every_repeat_to_cover_target(tmp_path: Path) -> None:
    """Verify accepts only when every distinct after-report covers the target tool."""
    before = tmp_path / "before.json"
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    _write_report(before, covered=["write"], uncovered=["read"])
    _write_report(first, covered=["read"], uncovered=[], run_id="repeat-1")
    _write_report(second, covered=["read"], uncovered=[], run_id="repeat-2")

    result = _run(
        "verify",
        "--before",
        str(before),
        "--after",
        str(first),
        "--after",
        str(second),
        "--target",
        "read",
    )
    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["accepted"] is True
    assert payload["repeat_count"] == 2

    _write_report(second, covered=[], uncovered=["read"], run_id="repeat-2")
    failed = _run(
        "verify",
        "--before",
        str(before),
        "--after",
        str(first),
        "--after",
        str(second),
        "--target",
        "read",
    )
    assert failed.returncode == 1
    assert json.loads(failed.stdout)["accepted"] is False


def _proposal_inputs(tmp_path: Path, *, kind: str = "capability", covered: bool = False):
    """Synthetic event-planner findings; no customer traces or credentials."""
    report = tmp_path / "report.json"
    name = "accurate_user_communication" if covered else "fixture_generalization"
    if kind == "failure_case":
        name = "rejection_preserves_reservation"
    payload = {
        "covered": ["submit_itinerary"] + ([name] if covered else []),
        "uncovered_items": []
        if covered
        else [
            {
                "name": name,
                "kind": kind,
                "reason": "not_covered_by_any_input_report",
                "description": "Exercise the intended outcome.",
            }
        ],
        "input_reports": [{"item_kind": kind, "covered": [name] if covered else []}],
    }
    report.write_text(json.dumps(payload))
    finding = {
        "id": "planner-outcome",
        "name": name,
        "kind": kind,
        "basis": "observed_failure" if covered else "absent_scenario",
        "action": "strengthen_existing" if covered else "new_scenario",
        "scenario": "Check offsite explanation." if covered else "Use a changed world and tighter budget.",
        "expected_behavior": "Explain accepted times accurately." if covered else "Reserve a feasible itinerary.",
        "verifier": "Compare claims to accepted minutes." if covered else "Validate against changed world constraints.",
        "evidence": ["synthetic/run-a/step-18: says 9 AM for minute 900"] if covered else ["reviewed starter fixtures"],
    }
    if covered:
        source = tmp_path / "offsite"
        source.mkdir()
        (source / "instruction.md").write_text("Original offsite scenario")
        finding["existing_task"] = str(source)
    return report, finding


def _proposal_manifest(tmp_path: Path, report: Path, findings: list[dict], *, scope: str = "implement") -> Path:
    inputs = tmp_path / "findings.json"
    inputs.write_text(json.dumps({"findings": findings}))
    result = _run("propose", "--report", str(report), "--findings", str(inputs), "--scope", scope)
    assert result.returncode == 0, result.stdout + result.stderr
    manifest = tmp_path / "proposals.json"
    manifest.write_text(result.stdout)
    return manifest


def test_full_tool_coverage_routes_capability_gap(tmp_path: Path) -> None:
    report, finding = _proposal_inputs(tmp_path)
    manifest = _proposal_manifest(tmp_path, report, [finding])
    legacy = json.loads(_run("select", "--report", str(report)).stdout)
    selected = json.loads(_run("select", "--report", str(report), "--proposals", str(manifest)).stdout)
    assert legacy["actionable_count"] == 0
    assert legacy["selection_scope"] == "tool_gaps_only"
    assert selected["implementation_count"] == 1
    assert selected["next_action"] == "scaffold"
    assert selected["actionable_proposals"][0]["kind"] == "capability"
    assert selected["actionable_proposals"][0]["scenario"] == finding["scenario"]


def test_observed_failure_on_covered_capability_prefers_revision(tmp_path: Path) -> None:
    report, finding = _proposal_inputs(tmp_path, covered=True)
    manifest = _proposal_manifest(tmp_path, report, [finding])
    proposal = json.loads(manifest.read_text())["proposals"][0]
    assert proposal["aggregate_covered"] is True
    assert proposal["basis"] == "observed_failure"
    assert proposal["action"] == "strengthen_existing"
    assert proposal["implementation_eligible"] is True
    assert proposal["evidence"] == finding["evidence"]


@pytest.mark.parametrize(
    "status,evidence,eligible",
    [
        ("unverified", [], False),
        ("observed", [], False),
        ("observed", ["submit_itinerary valid=false; reservation snapshots unchanged"], True),
        ("proposed", [], False),
    ],
)
def test_observed_failure_requires_its_trigger(tmp_path: Path, status: str, evidence: list, eligible: bool) -> None:
    report, finding = _proposal_inputs(tmp_path, kind="failure_case")
    finding.update(
        basis="observed_failure",
        trigger={
            "description": "Reservation submission rejected",
            "status": status,
            "evidence": evidence,
            "verification": "Require valid=false and compare reservation snapshots before and after.",
        },
    )
    manifest = _proposal_manifest(tmp_path, report, [finding])
    proposal = json.loads(manifest.read_text())["proposals"][0]
    assert proposal["implementation_eligible"] is eligible
    # Unknown-route errors are not supplied as evidence of reservation rejection.
    if not eligible:
        assert proposal["blockers"]


def test_proposed_trigger_supports_design_without_claiming_observation(tmp_path: Path) -> None:
    report, finding = _proposal_inputs(tmp_path, kind="failure_case")
    finding["trigger"] = {
        "description": "Submit a genuinely conflicting seeded plan under unchanged rules.",
        "status": "proposed",
        "evidence": [],
        "verification": "Require domain rejection before checking state preservation.",
    }
    proposal = json.loads(_proposal_manifest(tmp_path, report, [finding]).read_text())["proposals"][0]
    assert proposal["implementation_eligible"] is True
    assert proposal["basis"] == "absent_scenario"
    assert proposal["trigger"]["status"] == "proposed"
    assert proposal["aggregate_covered"] is False


def test_missing_evidence_and_undefined_behavior_remain_explicit(tmp_path: Path) -> None:
    report, finding = _proposal_inputs(tmp_path, kind="failure_case")
    finding.update(action="define_behavior", expected_behavior=None, verifier=None)
    manifest = _proposal_manifest(tmp_path, report, [finding])
    proposal = json.loads(manifest.read_text())["proposals"][0]
    assert proposal["implementation_eligible"] is False
    assert "define_expected_behavior" in proposal["blockers"]
    assert "design_trigger_check" in proposal["blockers"]
    assert proposal["expected_behavior"] is None
    unresolved = json.loads(_proposal_manifest(tmp_path, report, []).read_text())["proposals"][0]
    assert unresolved["basis"] == "insufficient_evidence"
    assert unresolved["reason"] == "not_covered_by_any_input_report"
    assert unresolved["action"] == "gather_evidence"


def _scaffold_proposal(module, tmp_path: Path, report: Path, manifest: Path):
    instruction = tmp_path / ".eval-author/proposals/eval-planner-outcome-instruction.md"
    instruction.parent.mkdir(parents=True, exist_ok=True)
    instruction.write_text("Plan the requested event and explain the reservation.")
    return module._scaffold(
        report_path=report,
        proposals_path=manifest,
        target="planner-outcome",
        output=tmp_path / ".eval-author/task-drafts/eval-planner-outcome",
        task_name="example/eval-planner-outcome",
        description="Exercise planner outcome",
        author="Test",
        instruction_file=instruction,
    )


def test_proposal_only_cannot_scaffold_or_call_provider(tmp_path: Path, monkeypatch) -> None:
    module = _load_task_pipeline_module()
    report, finding = _proposal_inputs(tmp_path)
    findings = tmp_path / "findings.json"
    findings.write_text(json.dumps({"findings": [finding]}))
    initial = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    monkeypatch.setattr(module.subprocess, "run", lambda *a, **k: pytest.fail("must not execute providers"))
    payload = module._propose(report, findings, "proposal-only")
    assert {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()} == initial
    manifest = tmp_path / "proposals.json"
    manifest.write_text(json.dumps(payload))
    assert module._select(report, None, manifest)["next_action"] == "report_proposals"
    with pytest.raises(module.PipelineError, match="proposal-only"):
        _scaffold_proposal(module, tmp_path, report, manifest)
    assert not (tmp_path / ".eval-author/task-drafts").exists()


@pytest.mark.parametrize("revision", [False, True])
def test_authorized_non_tool_scaffold_preserves_original(tmp_path: Path, monkeypatch, revision: bool) -> None:
    module = _load_task_pipeline_module()
    report, finding = _proposal_inputs(tmp_path, covered=revision)
    manifest = _proposal_manifest(tmp_path, report, [finding])
    draft = tmp_path / ".eval-author/task-drafts/eval-planner-outcome"
    original = Path(finding["existing_task"]) / "instruction.md" if revision else None
    before = original.read_bytes() if original else None
    calls = []

    def init(command, **kwargs):
        calls.append(command)
        draft.mkdir()
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(module.shutil, "which", lambda _: "/fake/harbor")
    monkeypatch.setattr(module.subprocess, "run", init)
    result = _scaffold_proposal(module, tmp_path, report, manifest)
    assert result["proposal"]["kind"] == "capability"
    assert calls[0][1:3] == ["task", "init"]
    assert (draft / "instruction.md").is_file()
    if original:
        assert original.read_bytes() == before
    with pytest.raises(module.PipelineError, match="already exists"):
        _scaffold_proposal(module, tmp_path, report, manifest)
    assert len(calls) == 1


def test_forged_readiness_and_changed_report_are_rejected(tmp_path: Path) -> None:
    module = _load_task_pipeline_module()
    report, finding = _proposal_inputs(tmp_path)
    finding.update(expected_behavior=None, source_changes_required=True)
    manifest = _proposal_manifest(tmp_path, report, [finding])
    payload = json.loads(manifest.read_text())
    payload["proposals"][0].update(implementation_eligible=True, blockers=[])
    manifest.write_text(json.dumps(payload))
    with pytest.raises(module.PipelineError, match="define_expected_behavior.*source_change_authorization_required"):
        _scaffold_proposal(module, tmp_path, report, manifest)
    report.write_text(report.read_text() + "\n")
    with pytest.raises(module.PipelineError, match="different audit report"):
        module._select(report, None, manifest)


@pytest.mark.parametrize("kind", ["capability", "failure_case"])
def test_verify_uses_outcome_method_and_separates_results(tmp_path: Path, kind: str) -> None:
    module = _load_task_pipeline_module()
    report, finding = _proposal_inputs(tmp_path, kind=kind, covered=kind == "capability")
    if kind == "failure_case":
        finding["trigger"] = {
            "description": "Domain rejection",
            "status": "proposed",
            "evidence": [],
            "verification": "Inspect valid=false response before grading recovery",
        }
    manifest = _proposal_manifest(tmp_path, report, [finding])
    after = []
    for i in range(2):
        path = tmp_path / f"repeat-{i}.json"
        entry = _coverage_input_report(run_id=f"repeat-{i}", covered=[finding["name"]])
        entry["subject"]["task_id"] = "eval-planner-outcome"
        entry.update(method=module._METHODS[kind], item_kind=kind)
        path.write_text(json.dumps({"covered": [finding["name"]], "input_reports": [entry]}))
        after.append(path)
    code, result = module._verify(report, after, finding["id"], manifest)
    assert code == 0
    assert result["coverage_closed"] is True
    assert result["task_correctness"] == result["agent_performance"] == "not_assessed"
    assert "accepted" not in result
    # A tool-only measurement cannot prove a capability/failure outcome.
    payload = json.loads(after[1].read_text())
    payload["input_reports"][0].update(method="tool_calls", item_kind="tool")
    after[1].write_text(json.dumps(payload))
    code, result = module._verify(report, after, finding["id"], manifest)
    assert code == 1
    assert result["coverage_closed"] is False
    # Nor can unioning a failing run with a passing run prove repetition.
    payload["input_reports"].append(_coverage_input_report(run_id="hidden-run", covered=[finding["name"]]))
    after[1].write_text(json.dumps(payload))
    with pytest.raises(module.PipelineError, match="one run of the selected draft"):
        module._verify(report, after, finding["id"], manifest)
