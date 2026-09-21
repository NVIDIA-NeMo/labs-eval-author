# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Prove Discover fixture ground truth and catch false-positive artifact grades."""

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from harbor.models.job.config import JobConfig
from harbor.models.task.task import Task

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/eval-author-discover"
EVALS = SKILL / "evals"
spec = importlib.util.spec_from_file_location("discover_grader", EVALS / "grader.py")
grader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grader)
DATASET = json.loads((EVALS / "evals.json").read_text())


def trace(command=None):
    step = {"source": "agent", "message": "Inspection complete."}
    if command:
        step["tool_calls"] = [{"function_name": "bash", "arguments": {"command": command}}]
    return {"steps": [step]}


@pytest.fixture
def workspace(tmp_path):
    inputs = tmp_path / "input"
    shutil.copytree(EVALS / "files", inputs)
    return inputs


def report(inputs, repo_name="harbor-repo"):
    repo = inputs / repo_name
    path = repo / ".eval-author/discovery.md"
    path.parent.mkdir(exist_ok=True)
    path.write_text("# Inventory\n\nDocumented commands remain unverified.\n")
    return repo


def test_every_authored_case_has_explicit_fixture_selection_and_grader_ground_truth():
    assert DATASET["skill_name"] == SKILL.name
    assert len(DATASET["evals"]) == 8
    assert {case["id"] for case in DATASET["evals"]} == set(grader.CASE_REPOS)
    for case in DATASET["evals"]:
        repo_name = grader.CASE_REPOS[case["id"]]
        assert case["files"] == ([f"files/{repo_name}"] if repo_name else [])
        assert len(case["assertions"]) >= 2
    actual = {
        repo.name: {
            path.relative_to(repo).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(repo.rglob("*"))
            if path.is_file()
        }
        for repo in sorted((EVALS / "files").iterdir())
    }
    assert grader.FIXTURE_HASHES == actual, (
        "Refresh embedded hashes using evals/README.md after reviewing fixture edits"
    )


def test_harbor_judges_both_fixture_configs_and_tasks():
    repo = EVALS / "files/harbor-repo"
    for name in ("refund", "missing-date"):
        config = JobConfig.model_validate_json((repo / "evals" / f"{name}.json").read_text())
        assert len(config.datasets) == len(config.agents) == 1
        assert config.agents[0].name == "oracle"
        tasks = list((repo / config.datasets[0].path).iterdir())
        assert len(tasks) == 1
        assert Task.is_valid_dir(tasks[0])
        task = Task(tasks[0])
        assert task.config.task.name.startswith("discover-fixture/")


@pytest.mark.parametrize(
    "case_id",
    [key for key in grader.CASE_REPOS if key not in (grader.PROVIDER_CASE, "discover-negative")],
)
def test_valid_saved_inventory_passes_artifact_checks_without_claiming_semantic_success(workspace, case_id):
    report(workspace, grader.CASE_REPOS[case_id])
    result = grader.grade({"id": case_id}, workspace, trace())
    assert result["custom_metrics"]["discover_overall"] == 1
    assert "native assertions" in result["details"]["scope"]


@pytest.mark.parametrize(
    "mutation,metric",
    [
        ("missing_report", "report_created"),
        ("empty_report", "report_created"),
        ("changed_source", "source_preserved"),
        ("deleted_source", "source_preserved"),
        ("overwritten_evidence", "source_preserved"),
        ("outside_scope", "write_scope_respected"),
        ("unexpected_ethos", "write_scope_respected"),
        ("ran_suite", "no_suite_run"),
        ("linked_report", "report_created"),
    ],
)
def test_artifact_grader_rejects_regressions(workspace, mutation, metric):
    repo = report(workspace)
    target = repo / ".eval-author/discovery.md"
    if mutation == "missing_report":
        target.unlink()
    elif mutation == "empty_report":
        target.write_text("   \n")
    elif mutation == "changed_source":
        (repo / "README.md").write_text("Changed intent")
    elif mutation == "deleted_source":
        (repo / "README.md").unlink()
    elif mutation == "overwritten_evidence":
        (repo / ".eval-author/readiness-before.json").write_text('{"proven": true}')
    elif mutation == "outside_scope":
        (repo / "surprise.py").write_text("pass\n")
    elif mutation == "unexpected_ethos":
        (repo / "ETHOS.md").write_text("Unrequested intent changes")
    elif mutation == "ran_suite":
        (repo / ".suite-was-run").touch()
    elif mutation == "linked_report":
        target.unlink()
        target.symlink_to(repo / "README.md")
    result = grader.grade({"id": "discover-D01-existing-harbor"}, workspace, trace())
    assert result["custom_metrics"][metric] == 0
    assert result["overall"] == 0


def test_audit_handoff_may_create_local_ethos(workspace):
    repo = report(workspace)
    (repo / "ETHOS.md").write_text("# Draft Ethos\nAwaiting the user's content review.\n")
    assert grader.grade({"id": grader.AUDIT_CASE}, workspace, trace())["overall"] == 1


@pytest.fixture
def missing_provider(workspace):
    repo = report(workspace)
    script = SKILL / "scripts/discover.py"
    result = subprocess.run(
        [sys.executable, "-I", "-S", str(script), "--repo", str(repo)], capture_output=True, text=True, check=False
    )
    assert result.returncode == 1, result.stderr
    data = json.loads(result.stdout)
    assert data["runtime"]["harbor_importable"] is False
    (repo / ".eval-author/discovery.json").write_text(result.stdout)
    return repo, f"python3 -I -S {script} --repo {repo}"


def test_missing_provider_case_accepts_real_native_failure_and_keeps_inventory(workspace, missing_provider):
    _, command = missing_provider
    result = grader.grade({"id": grader.PROVIDER_CASE}, workspace, trace(command))
    assert result["overall"] == 1


@pytest.mark.parametrize("defect", ["fabricated_proven", "wrong_repository", "missing_config", "no_tool_call"])
def test_provider_evidence_cannot_be_replaced_by_reassuring_claims(workspace, missing_provider, defect):
    repo, command = missing_provider
    path = repo / ".eval-author/discovery.json"
    data = json.loads(path.read_text())
    if defect == "fabricated_proven":
        data["proven"] = True
    elif defect == "wrong_repository":
        data["repo_root"] = "/some/other/repository"
    elif defect == "missing_config":
        data["configs"].pop()
    else:
        command = None
    path.write_text(json.dumps(data))
    result = grader.grade({"id": grader.PROVIDER_CASE}, workspace, trace(command))
    assert result["custom_metrics"]["provider_evidence"] == result["overall"] == 0


def test_quoted_discovery_command_is_not_execution_evidence(workspace):
    repo = workspace / "harbor-repo"
    command = f'echo "python3 -I -S /skills/eval-author-discover/scripts/discover.py --repo {repo}"'
    assert not grader.invoked_minimal_discovery([command], repo)


def test_discovery_invocation_allows_shell_variables_and_newline_separation(workspace):
    repo = workspace / "harbor-repo"
    command = (
        f'repo="{repo}"\nscript=/skills/eval-author-discover/scripts/discover.py\n'
        'python3 -I -S "$script" --repo "$repo" > "$repo/.eval-author/discovery.json"'
    )
    assert grader.invoked_minimal_discovery([command], repo)


def test_negative_case_does_not_allow_workflow_side_effects(tmp_path):
    inputs = tmp_path / "input"
    assert grader.grade({"id": "discover-negative"}, inputs, trace())["overall"] == 1
    inputs.mkdir()
    (inputs / ".eval-author").mkdir()
    assert grader.grade({"id": "discover-negative"}, inputs, trace())["overall"] == 0


def test_unknown_case_cannot_pass_vacuously(workspace):
    with pytest.raises(KeyError):
        grader.grade({"id": "not-an-authored-case"}, workspace, trace())
