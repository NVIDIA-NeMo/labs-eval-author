#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Route audit proposals, scaffold separate Harbor drafts, and verify coverage."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

_ACTIONABLE_REASON = "not_covered_by_any_input_report"
_DRAFT_PARTS = (".eval-author", "task-drafts")
_PROPOSAL_PARTS = (".eval-author", "proposals")
_SLUG_PREFIX = "cover-"
_MIN_VERIFY_REPORTS = 2


class PipelineError(ValueError):
    """A user-correctable pipeline input error."""


def _read_json(path: Path) -> dict[str, Any]:
    """Load one JSON object from ``path`` or raise ``PipelineError``."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PipelineError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise PipelineError(f"expected a JSON object: {path}")
    return payload


def task_slug_for_tool(tool_name: str) -> str:
    """Return the base Harbor artifact slug for one uncovered audit tool name."""
    normalized = tool_name.strip()
    if not normalized:
        raise PipelineError("tool name is empty")
    slug_body = re.sub(r"[^A-Za-z0-9]+", "-", normalized.replace(".", "-").replace(":", "-"))
    slug_body = slug_body.strip("-").lower()
    if not slug_body or not slug_body[0].isalpha():
        slug_body = f"tool-{slug_body}" if slug_body else "tool"
    return f"{_SLUG_PREFIX}{slug_body}"


def _assign_unique_task_slugs(gaps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return gaps with unique ``task_slug`` values, suffixing ``-2``, ``-3``, ... on collisions."""
    assigned: set[str] = set()
    enriched: list[dict[str, Any]] = []
    for gap in sorted(gaps, key=lambda item: str(item["name"])):
        base_slug = task_slug_for_tool(str(gap["name"]))
        task_slug = base_slug
        suffix = 2
        while task_slug in assigned:
            task_slug = f"{base_slug}-{suffix}"
            suffix += 1
        assigned.add(task_slug)
        enriched.append({**gap, "task_slug": task_slug, "paths": _artifact_paths(task_slug)})
    return enriched


def _task_slug_for_target(report: dict[str, Any], target: str) -> str:
    """Return the assigned task slug for one actionable uncovered tool in ``report``."""
    for gap in _actionable_tools(report):
        if gap["name"] == target:
            return gap["task_slug"]
    raise PipelineError(f"{target!r} is not an actionable uncovered tool")


def _artifact_paths(task_slug: str) -> dict[str, str]:
    """Return the canonical ``.eval-author/`` paths for one task slug."""
    return {
        "proposal": f".eval-author/proposals/{task_slug}-instruction.md",
        "draft": f".eval-author/task-drafts/{task_slug}",
        "measurements": f".eval-author/task-measurements/{task_slug}",
        "task_id": task_slug,
    }


def _gap_from_uncovered_item(item: dict[str, Any]) -> dict[str, Any]:
    """Build one actionable tool gap record from an aggregate ``uncovered_items`` entry."""
    generation = item.get("generation") or {}
    return {
        "name": item.get("name"),
        "kind": "tool",
        "reason": item.get("reason"),
        "description": item.get("description"),
        "focus": generation.get("focus"),
        "needed_tools": generation.get("needed_tools") or [],
        "evidence_required": generation.get("evidence_required") or [],
    }


def _actionable_tools(report: dict[str, Any]) -> list[dict[str, Any]]:
    """Return uncovered tool items that are eligible for task generation."""
    gaps: list[dict[str, Any]] = []
    for item in report.get("uncovered_items") or []:
        if not isinstance(item, dict):
            continue
        if item.get("kind") != "tool" or item.get("reason") != _ACTIONABLE_REASON:
            continue
        gaps.append(_gap_from_uncovered_item(item))
    return _assign_unique_task_slugs(gaps)


_PROPOSAL_SCHEMA = "nemo.eval_author.dataset_proposals.v1"
_METHODS = {"tool": "tool_calls", "capability": "capabilities", "failure_case": "failure_cases"}
_ACTIONS = {"new_scenario", "strengthen_existing", "retain_regression", "gather_evidence", "define_behavior"}
_BASES = {"observed_failure", "absent_scenario", "insufficient_evidence"}


def _report_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _strings(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(x, str) and x.strip() for x in value)


def _proposal_blockers(proposal: dict[str, Any]) -> list[str]:
    """Check design readiness, never infer task correctness or user authorization."""
    blockers = []
    if proposal["basis"] == "insufficient_evidence":
        blockers.append("inspect_evidence")
    if proposal["action"] not in {"new_scenario", "strengthen_existing"}:
        blockers.append(proposal["action"])
    for field in ("scenario", "expected_behavior", "verifier"):
        if not isinstance(proposal.get(field), str) or not proposal[field].strip():
            blockers.append(f"define_{field}")
    if not _strings(proposal.get("evidence")):
        blockers.append("inspect_evidence")
    if proposal["action"] == "strengthen_existing" and not proposal.get("existing_task"):
        blockers.append("identify_existing_task")
    if proposal.get("source_changes_required"):
        blockers.append("source_change_authorization_required")
    trigger = proposal.get("trigger")
    if proposal["kind"] == "failure_case" or trigger is not None:
        trigger = trigger or {}
        if not trigger.get("description") or not trigger.get("verification"):
            blockers.append("design_trigger_check")
        if trigger.get("status") not in {"observed", "proposed"}:
            blockers.append("establish_trigger")
        if trigger.get("status") == "observed" and not _strings(trigger.get("evidence")):
            blockers.append("inspect_trigger_evidence")
        if proposal["basis"] == "observed_failure" and trigger.get("status") != "observed":
            blockers.append("inspect_trigger_evidence")
    return list(dict.fromkeys(blockers))


def _build_proposals(report: dict[str, Any], findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Combine reviewed semantic findings with unresolved gaps, preserving report evidence."""
    inventory = {item["name"]: item["kind"] for item in report.get("uncovered_items", [])}
    for entry in report.get("input_reports", []):
        for name in entry.get("covered", []):
            inventory.setdefault(name, entry.get("item_kind"))
    proposals = []
    ids = set()
    reviewed = set()
    for finding in findings:
        if not isinstance(finding, dict):
            raise PipelineError("each finding must be an object")
        proposal = dict(finding)
        proposal_id = proposal.get("id")
        if not isinstance(proposal_id, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", proposal_id):
            raise PipelineError("finding id must be a lowercase slug")
        if proposal_id in ids:
            raise PipelineError(f"duplicate proposal id: {proposal_id}")
        ids.add(proposal_id)
        name, kind = proposal.get("name"), proposal.get("kind")
        if kind not in _METHODS or inventory.get(name) != kind:
            raise PipelineError(f"finding target must match an audit item and kind: {name!r}")
        if proposal.get("basis") not in _BASES or proposal.get("action") not in _ACTIONS:
            raise PipelineError(f"invalid basis or action: {proposal_id}")
        if "trigger" in proposal and not isinstance(proposal["trigger"], dict):
            raise PipelineError("trigger must be an object")
        if not isinstance(proposal.get("source_changes_required", False), bool):
            raise PipelineError("source_changes_required must be boolean")
        if proposal["basis"] == "observed_failure" and not _strings(proposal.get("evidence")):
            raise PipelineError("observed failure requires per-run evidence references")
        reviewed.add(name)
        proposals.append(proposal)
    for item in report.get("uncovered_items", []):
        if item["name"] in reviewed:
            continue
        proposal_id = "inspect-" + task_slug_for_tool(item["name"])
        while proposal_id in ids:
            proposal_id += "-2"
        ids.add(proposal_id)
        proposals.append(
            {
                "id": proposal_id,
                "name": item["name"],
                "kind": item["kind"],
                "basis": "insufficient_evidence",
                "action": "gather_evidence",
                "scenario": item.get("description"),
                "expected_behavior": None,
                "verifier": None,
                "evidence": [],
                "reason": item.get("reason"),
            }
        )
    for proposal in proposals:
        proposal["aggregate_covered"] = proposal["name"] in report.get("covered", [])
        proposal["blockers"] = _proposal_blockers(proposal)
        proposal["implementation_eligible"] = not proposal["blockers"]
        proposal["task_slug"] = "eval-" + proposal["id"]
        proposal["paths"] = _artifact_paths(proposal["task_slug"])
    return proposals


def _propose(report_path: Path, findings_path: Path, scope: str) -> dict[str, Any]:
    findings = _read_json(findings_path).get("findings")
    if not isinstance(findings, list):
        raise PipelineError("findings must be a list of reviewed findings")
    return {
        "schema": _PROPOSAL_SCHEMA,
        "report": str(report_path),
        "report_sha256": _report_digest(report_path),
        "scope": scope,
        "proposals": _build_proposals(_read_json(report_path), findings),
        "valid": True,
    }


def _load_proposals(path: Path, report_path: Path) -> dict[str, Any]:
    payload = _read_json(path)
    if payload.get("schema") != _PROPOSAL_SCHEMA or payload.get("scope") not in {"proposal-only", "implement"}:
        raise PipelineError("invalid proposal schema or scope")
    if payload.get("report_sha256") != _report_digest(report_path):
        raise PipelineError("proposals refer to a different audit report; review findings again")
    if not isinstance(payload.get("proposals"), list):
        raise PipelineError("proposals must be a list")
    # Recompute eligibility and paths; never trust persisted derived flags.
    payload["proposals"] = _build_proposals(_read_json(report_path), payload["proposals"])
    return payload


def _selected_proposal(path: Path, report_path: Path, target: str) -> dict[str, Any]:
    manifest = _load_proposals(path, report_path)
    for proposal in manifest["proposals"]:
        if proposal["id"] == target:
            if manifest["scope"] != "implement":
                raise PipelineError("proposal-only scope does not authorize implementation")
            if not proposal["implementation_eligible"]:
                raise PipelineError(f"proposal requires: {', '.join(proposal['blockers'])}")
            return proposal
    raise PipelineError(f"unknown proposal id: {target}")


def _select(report_path: Path, target: str | None, proposals_path: Path | None = None) -> dict[str, Any]:
    """Select reviewed proposals or use the backward-compatible tool-gap selector."""
    if proposals_path is not None:
        manifest = _load_proposals(proposals_path, report_path)
        proposals = manifest["proposals"]
        if target is not None:
            proposals = [p for p in proposals if p["id"] == target]
            if not proposals:
                raise PipelineError(f"unknown proposal id: {target}")
        eligible = [p for p in proposals if p["implementation_eligible"]]
        return {
            "schema": "nemo.eval_author.proposal_selection.v1",
            "valid": True,
            "scope": manifest["scope"],
            "proposal_count": len(proposals),
            "implementation_count": len(eligible),
            "actionable_proposals": eligible,
            "deferred_proposals": [p for p in proposals if not p["implementation_eligible"]],
            "next_action": "scaffold" if eligible and manifest["scope"] == "implement" else "report_proposals",
        }
    gaps = _actionable_tools(_read_json(report_path))
    if target is not None:
        gaps = [gap for gap in gaps if gap["name"] == target]
        if not gaps:
            raise PipelineError(f"{target!r} is not an actionable uncovered tool in {report_path}")
    return {
        "schema": "nemo.eval_author.task_gap_selection.v1",
        "report": str(report_path),
        "selection_scope": "tool_gaps_only",
        "actionable_count": len(gaps),
        "actionable_tools": gaps,
        "valid": True,
    }


def _require_draft_destination(path: Path) -> None:
    """Require ``path`` to live under ``.eval-author/task-drafts/``."""
    parts = path.resolve().parts
    for index in range(len(parts) - 1):
        if parts[index : index + 2] == _DRAFT_PARTS:
            return
    raise PipelineError("draft output must be under .eval-author/task-drafts/")


def _require_proposal_destination(path: Path) -> None:
    """Require ``path`` to live under ``.eval-author/proposals/``."""
    parts = path.resolve().parts
    for index in range(len(parts) - 1):
        if parts[index : index + 2] == _PROPOSAL_PARTS:
            return
    raise PipelineError("instruction file must be under .eval-author/proposals/")


def _require_task_slug_paths(*, task_slug: str, output: Path, task_name: str, instruction_file: Path) -> None:
    """Require draft, Harbor task name, and proposal filenames to match ``task_slug``."""
    if output.name != task_slug:
        raise PipelineError(f"draft directory must be named {task_slug!r} for the selected tool, got {output.name!r}")
    if Path(task_name).name != task_slug:
        raise PipelineError("draft directory name must match the final component of --task-name")
    expected_instruction = f"{task_slug}-instruction.md"
    if instruction_file.name != expected_instruction:
        raise PipelineError(f"instruction file must be named {expected_instruction!r}, got {instruction_file.name!r}")
    _require_proposal_destination(instruction_file)


def _scaffold(
    *,
    report_path: Path,
    target: str,
    output: Path,
    task_name: str,
    description: str,
    author: str,
    instruction_file: Path,
    proposals_path: Path | None = None,
) -> dict[str, Any]:
    """Initialize a Harbor-native draft and install the supplied instruction."""
    report = _read_json(report_path)
    proposal = _selected_proposal(proposals_path, report_path, target) if proposals_path else None
    task_slug = proposal["task_slug"] if proposal else _task_slug_for_target(report, target)
    if proposal and proposal.get("existing_task"):
        source = Path(proposal["existing_task"])
        if not source.is_dir():
            raise PipelineError(f"existing task is not a directory: {source}")
        if output.resolve() == source.resolve() or source.resolve() in output.resolve().parents:
            raise PipelineError("draft must be separate from the existing task")
    _require_draft_destination(output)
    _require_task_slug_paths(
        task_slug=task_slug,
        output=output,
        task_name=task_name,
        instruction_file=instruction_file,
    )
    if output.exists():
        raise PipelineError(f"draft output already exists: {output}")
    try:
        instruction = instruction_file.read_text(encoding="utf-8")
    except OSError as exc:
        raise PipelineError(f"cannot read instruction {instruction_file}: {exc}") from exc
    if not instruction.strip():
        raise PipelineError("instruction file is empty")
    harbor = shutil.which("harbor")
    if harbor is None:
        raise PipelineError("harbor executable is not available")

    output.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [
            harbor,
            "task",
            "init",
            task_name,
            "--tasks-dir",
            str(output.parent),
            "--description",
            description,
            "--author",
            author,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise PipelineError(f"harbor task init failed: {result.stderr or result.stdout}")
    if not output.is_dir():
        raise PipelineError(f"harbor did not create the expected draft: {output}")
    (output / "instruction.md").write_text(instruction, encoding="utf-8")
    return {
        "schema": "nemo.eval_author.harbor_task_draft.v1",
        **({"proposal": proposal} if proposal else {"target_tool": target}),
        "task_slug": task_slug,
        "paths": _artifact_paths(task_slug),
        "draft": str(output),
        "task_name": task_name,
        "scaffolder": "harbor task init",
        "valid": True,
        "written": True,
    }


def _run_ids_from_report(report: dict[str, Any], *, report_path: Path) -> list[str]:
    """Return ATIF ``subject.run_id`` values recorded in one aggregate coverage report."""
    input_reports = report.get("input_reports")
    if not isinstance(input_reports, list) or not input_reports:
        raise PipelineError(f"after report must include input_reports with subject.run_id: {report_path}")
    run_ids: list[str] = []
    for index, entry in enumerate(input_reports):
        if not isinstance(entry, dict):
            raise PipelineError(f"after report input_reports[{index}] must be an object: {report_path}")
        subject = entry.get("subject")
        if not isinstance(subject, dict):
            raise PipelineError(f"after report input_reports[{index}] must include subject: {report_path}")
        run_id = subject.get("run_id")
        if not isinstance(run_id, str) or not run_id.strip():
            raise PipelineError(
                f"after report input_reports[{index}].subject.run_id must be a non-empty string: {report_path}"
            )
        run_ids.append(run_id)
    return run_ids


def _verify(
    before_path: Path, after_paths: list[Path], target: str, proposals_path: Path | None = None
) -> tuple[int, dict[str, Any]]:
    """Accept only when ``target`` was an actionable gap before and covered in every repeat report."""
    before = _read_json(before_path)
    proposal = _selected_proposal(proposals_path, before_path, target) if proposals_path else None
    if proposal:
        target = proposal["name"]
    else:
        _task_slug_for_target(before, target)
    if len(after_paths) < _MIN_VERIFY_REPORTS:
        raise PipelineError(f"at least {_MIN_VERIFY_REPORTS} --after reports are required")
    resolved_paths = [path.resolve() for path in after_paths]
    if len(set(resolved_paths)) != len(resolved_paths):
        raise PipelineError("--after reports must be distinct")

    runs = []
    all_covered = True
    run_ids: list[str] = []
    for path in after_paths:
        report = _read_json(path)
        report_run_ids = _run_ids_from_report(report, report_path=path)
        if proposal:
            # An aggregate union of multiple trials must not hide a failing repeat.
            report_run_ids = list(dict.fromkeys(report_run_ids))
            subjects = {(e["subject"].get("task_id"), e["subject"]["run_id"]) for e in report["input_reports"]}
            if subjects != {(proposal["task_slug"], report_run_ids[0])}:
                raise PipelineError("each after report must contain one run of the selected draft")
        run_ids.extend(report_run_ids)
        covered = target in set(report.get("covered") or [])
        still_uncovered = target in set(report.get("uncovered") or [])
        if proposal:
            covered = covered and any(
                entry.get("method") == _METHODS[proposal["kind"]]
                and entry.get("item_kind") == proposal["kind"]
                and target in entry.get("covered", [])
                for entry in report["input_reports"]
            )
        passed = covered and not still_uncovered
        all_covered = all_covered and passed
        runs.append(
            {
                "report": str(path),
                "run_ids": report_run_ids,
                "covered": covered,
                "passed": passed,
            }
        )

    if len(set(run_ids)) != len(run_ids):
        raise PipelineError("--after reports must come from distinct ATIF subject.run_id values")

    payload = {
        "schema": "nemo.eval_author.task_gap_verification.v1",
        "target_tool": target,
        "before": str(before_path),
        "repeat_count": len(runs),
        "runs": runs,
        "accepted": all_covered,
        "valid": True,
    }
    if proposal:
        payload.pop("accepted")
        payload.pop("target_tool")
        payload.update(
            {
                "schema": "nemo.eval_author.proposal_verification.v1",
                "proposal_id": proposal["id"],
                "target": target,
                "kind": proposal["kind"],
                "coverage_closed": all_covered,
                "task_correctness": "not_assessed",
                "agent_performance": "not_assessed",
            }
        )
    return (0 if all_covered else 1), payload


def _parser() -> argparse.ArgumentParser:
    """Build the proposal, selection, scaffolding, and verification CLI."""
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    propose = subparsers.add_parser("propose", help="validate reviewed findings and emit dataset proposals")
    propose.add_argument("--report", type=Path, required=True)
    propose.add_argument("--findings", type=Path, required=True)
    propose.add_argument("--scope", choices=["proposal-only", "implement"], default="proposal-only")

    select = subparsers.add_parser("select", help="list actionable uncovered tool gaps")
    select.add_argument("--report", type=Path, required=True)
    select.add_argument("--target")
    select.add_argument("--proposals", type=Path)

    scaffold = subparsers.add_parser("scaffold", help="initialize a Harbor-native task draft")
    scaffold.add_argument("--report", type=Path, required=True)
    scaffold.add_argument("--target", required=True)
    scaffold.add_argument("--proposals", type=Path)
    scaffold.add_argument("--out", type=Path, required=True)
    scaffold.add_argument("--task-name", required=True)
    scaffold.add_argument("--description", required=True)
    scaffold.add_argument("--author", required=True)
    scaffold.add_argument("--instruction-file", type=Path, required=True)

    verify = subparsers.add_parser("verify", help="require two distinct repeats to close one gap")
    verify.add_argument("--before", type=Path, required=True)
    verify.add_argument("--after", type=Path, action="append", required=True)
    verify.add_argument("--target", required=True)
    verify.add_argument("--proposals", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run one pipeline subcommand and print a JSON verdict on stdout."""
    args = _parser().parse_args(argv)
    try:
        if args.command == "propose":
            payload = _propose(args.report, args.findings, args.scope)
            exit_code = 0
        elif args.command == "select":
            payload = _select(args.report, args.target, args.proposals)
            exit_code = 0
        elif args.command == "scaffold":
            payload = _scaffold(
                report_path=args.report,
                target=args.target,
                output=args.out,
                task_name=args.task_name,
                description=args.description,
                author=args.author,
                instruction_file=args.instruction_file,
                proposals_path=args.proposals,
            )
            exit_code = 0
        else:
            exit_code, payload = _verify(args.before, args.after, args.target, args.proposals)
    except PipelineError as exc:
        payload = {"valid": False, "error": str(exc)}
        exit_code = 1
    print(json.dumps(payload, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
