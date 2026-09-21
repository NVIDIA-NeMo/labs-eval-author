# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Check credential isolation, incomplete evidence, and paired live metrics without APIs."""

import importlib
import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def live(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "tools"))
    monkeypatch.setenv("SKILL_EVAL_LLM_MODEL", "fixture/chat")
    monkeypatch.setenv("SKILL_EVAL_EMBEDDING_MODEL", "fixture/embedding")
    monkeypatch.delenv("SKILL_EVAL_AGENT_MODEL", raising=False)
    return importlib.import_module("collect_live_skill_evaluations")


@pytest.fixture
def repo(tmp_path):
    repo = tmp_path / "repo"
    for name in ("eval-author", "another-skill"):
        path = repo / "skills" / name
        path.mkdir(parents=True)
        (path / "SKILL.md").write_text("# Fixture\n")
    evals = repo / "skills/eval-author/evals"
    evals.mkdir()
    (evals / "evals.json").write_text(
        json.dumps(
            {"skill_name": "eval-author", "evals": [{"id": "one", "prompt": "Task", "expected_output": "Answer"}]}
        )
    )
    for args in (
        ["init", "-b", "test"],
        ["add", "."],
        ["-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-m", "fixture"],
    ):
        subprocess.run(["git", *args], cwd=repo, capture_output=True, check=True)
    return repo


def tier2(validator="Context Deduplication"):
    return {
        "results": [
            {
                "validator": validator,
                "status": "passed",
                "passed": True,
                "incomplete_scans": [],
                "summary": {"errors": 0, "critical_count": 0, "high_count": 0, "medium_count": 0, "low_count": 0},
                "findings": [],
                "legacy": {"messages": ["PRIVATE-SENTINEL"]},
            }
        ]
    }


def tier3():
    arm = {"execution_status": "succeeded", "execution_errors": [], "expected_attempts": 1, "scored_attempts": 1}
    return {
        "execution_status": "succeeded",
        "execution_errors": [],
        "agents": {
            "opencode": {
                "execution_status": "succeeded",
                "conditions": {"with_skill": arm.copy(), "without_skill": arm.copy()},
                # Native dimension_scores() returns score/source objects, not scalars.
                "dimensions_with_skill": {
                    dimension: {"score": 0.8, "sources": {"PRIVATE-SENTINEL": 1}}
                    for dimension in ("security", "correctness", "discoverability", "effectiveness", "efficiency")
                },
                "dimensions_without_skill": {
                    dimension: {"score": 0.9, "sources": {"PRIVATE-SENTINEL": 1}}
                    for dimension in ("security", "correctness", "discoverability", "effectiveness", "efficiency")
                },
                "pass_at_k": {
                    "with_skill": {"passed_cases": 0, "total_cases": 1, "k": 1},
                    "without_skill": {"passed_cases": 1, "total_cases": 1, "k": 1},
                },
                "trajectory": "PRIVATE-SENTINEL",
            }
        },
    }


def test_tier2_distinguishes_duplicate_findings_from_missing_provider_evidence(live):
    report = tier2()
    row = report["results"][0]
    row.update(passed=False, status="failed", findings=[{"check_name": "duplicate"}])
    row["summary"].update(high_count=1, errors=1)
    assert live.summarize_tier2(report, 1, "Context Deduplication")["status"] == "failed"
    row["findings"][0]["check_name"] = "llm_error"
    assert live.summarize_tier2(report, 1, "Context Deduplication")["status"] == "incomplete"
    row["findings"] = []
    row["summary"]["high_count"] = 0
    assert live.summarize_tier2(report, 1, "Context Deduplication")["status"] == "incomplete"


def test_negative_lift_is_a_completed_experiment_not_an_execution_failure(live):
    result = live.summarize_tier3(tier3(), 0, 1)
    assert result["status"] == "completed"
    assert result["pass_rate_lift"] == -1
    assert result["dimension_lift"]["correctness"] == pytest.approx(-0.1)
    assert "PRIVATE-SENTINEL" not in json.dumps(result)


@pytest.mark.parametrize(
    "message,reason",
    [
        (
            "opencode runtime preflight failed: Docker compose command failed: docker compose build.",
            "docker_build_failed",
        ),
        ("opencode runtime preflight failed: invalid response", "agent_runtime_preflight_failed"),
        ("opencode runtime preflight failed: Docker compose command failed", "docker_runtime_failed"),
        ("opencode runtime preflight failed: NonZeroAgentExitCodeError", "agent_command_failed"),
        ("NonZeroAgentExitCodeError: OpenCode emitted error event(s)", "agent_api_failed"),
        ("NonZeroAgentExitCodeError: apt-get update", "agent_install_failed"),
        ("NonZeroAgentExitCodeError: nvm install 22", "agent_install_failed"),
        ("opencode runtime preflight failed: AgentSetupTimeoutError", "agent_install_timeout"),
        ("opencode runtime preflight failed: AgentTimeoutError", "agent_execution_timeout"),
        ("opencode runtime preflight failed: no agent artifacts", "agent_artifacts_missing"),
        ("unknown failure", "execution_incomplete"),
    ],
)
def test_failed_execution_exports_only_fixed_diagnostic_categories(live, message, reason):
    result = live.summarize_tier3(
        {"execution_status": "failed", "execution_errors": [message + " PRIVATE-SENTINEL"]}, 1, 4
    )
    assert result == {"status": "incomplete", "reason": reason}


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -1, 2, True, "secret"])
def test_invalid_live_scores_cannot_be_published(live, value):
    report = tier3()
    report["agents"]["opencode"]["dimensions_with_skill"]["security"]["score"] = value
    with pytest.raises(ValueError):
        live.summarize_tier3(report, 0, 1)


def test_missing_baseline_and_changed_denominator_do_not_produce_lift(live):
    with pytest.raises(ValueError):
        live.summarize_tier3(tier3(), 0, 2)
    report = tier3()
    report["agents"]["opencode"]["conditions"]["without_skill"]["scored_attempts"] = 0
    with pytest.raises(ValueError):
        live.summarize_tier3(report, 0, 1)
    assert live.summarize_tier3(tier3(), 1, 1)["status"] == "incomplete"


def test_plan_and_missing_key_never_execute(live, repo, tmp_path, monkeypatch):
    def no_execute(*args, **kwargs):
        pytest.fail("plan or missing credentials launched a process")

    monkeypatch.setattr(live, "execute", no_execute)
    monkeypatch.delenv("INFERENCE_HUB_API_KEY", raising=False)
    report = live.collect(repo, tmp_path / "missing", run=True)
    assert sum(r["reason"] == "missing_dataset" for r in report["observations"]) == 1
    assert sum(r["reason"] == "missing_provider_key" for r in report["observations"]) == 4
    monkeypatch.setenv("INFERENCE_HUB_API_KEY", "PRIVATE-SENTINEL")
    report = live.collect(repo, tmp_path / "plan")
    assert report["mode"] == "plan"
    assert "PRIVATE-SENTINEL" not in (tmp_path / "plan/live-skillevaluator-summary.json").read_text()


def test_hub_configuration_ignores_ambient_providers_and_preserves_model_namespaces(live, monkeypatch):
    monkeypatch.setenv("INFERENCE_HUB_API_KEY", "hub-fixture-key")
    for key in ("OPENAI_API_KEY", "NVIDIA_API_KEY", "HUB_METADATA_API_KEY", "SKILL_EVAL_LLM_API_KEY"):
        monkeypatch.setenv(key, "UNRELATED-SECRET")
    for key in ("OPENAI_BASE_URL", "SKILL_EVAL_LLM_BASE_URL", "SKILL_EVAL_EMBEDDING_BASE_URL"):
        monkeypatch.setenv(key, "https://api.openai.com/v1")
    monkeypatch.setenv("SKILL_EVAL_AGENT_MODEL", "openai/hub-model")
    models, env, missing = live.configuration("inference_hub")
    assert not missing
    assert models["agent"] == "openai/openai/hub-model"
    assert env["SKILL_EVAL_LLM_BASE_URL"] == env["SKILL_EVAL_EMBEDDING_BASE_URL"] == live.HUB_BASE_URL
    assert env["SKILL_EVAL_LLM_API_KEY"] == env["SKILL_EVAL_EMBEDDING_API_KEY"] == "hub-fixture-key"
    assert "UNRELATED-SECRET" not in json.dumps(env)
    for provider in ("openai", "nv_build"):
        with pytest.raises(ValueError, match="only NVIDIA Inference Hub"):
            live.configuration(provider)


@pytest.mark.parametrize("value", [None, "", "   "])
def test_hub_defaults_apply_to_unset_or_blank_model_variables(live, monkeypatch, value):
    for key in ("SKILL_EVAL_LLM_MODEL", "SKILL_EVAL_EMBEDDING_MODEL", "SKILL_EVAL_AGENT_MODEL"):
        if value is None:
            monkeypatch.delenv(key, raising=False)
        else:
            monkeypatch.setenv(key, value)
    models, env, _ = live.configuration("inference_hub")
    assert models == {
        "chat": "azure/openai/gpt-5.6-luna",
        "embedding": "azure/openai/text-embedding-3-small",
        "agent": "openai/azure/openai/gpt-5.6-luna",
    }
    assert env["SKILL_EVAL_LLM_BASE_URL"] == env["SKILL_EVAL_EMBEDDING_BASE_URL"] == live.HUB_BASE_URL


@pytest.mark.parametrize("latest_alias", [False, True])
def test_live_collection_is_bounded_and_retains_every_skill(live, repo, tmp_path, monkeypatch, latest_alias):
    monkeypatch.setenv("INFERENCE_HUB_API_KEY", "test-credential")
    monkeypatch.setenv("OPENAI_API_KEY", "UNRELATED-SECRET")
    monkeypatch.setenv("SKILL_EVAL_LLM_BASE_URL", "https://unintended.example")
    ambient_home = tmp_path / "ambient-home"
    ambient_home.mkdir()
    (ambient_home / ".docker").mkdir()
    (ambient_home / ".docker/config.json").write_text('{"auths":{"private":"UNRELATED-SECRET"}}')
    monkeypatch.setenv("HOME", str(ambient_home))
    calls = []

    def execute(argv, cwd, env, log, timeout):
        calls.append(argv)
        child_home = Path(env["HOME"])
        assert child_home.is_dir() and not child_home.is_relative_to(repo)
        assert child_home != ambient_home and child_home.stat().st_mode & 0o777 == 0o700
        assert not (child_home / ".docker/config.json").exists()
        assert "OPENAI_API_KEY" not in env and "NVIDIA_API_KEY" not in env
        assert env["SKILL_EVAL_LLM_BASE_URL"] == live.HUB_BASE_URL
        assert env["SKILL_EVAL_EMBEDDING_BASE_URL"] == live.HUB_BASE_URL
        assert env["SKILL_EVAL_LLM_API_KEY"] == "test-credential"
        assert env["SKILL_EVAL_EMBEDDING_API_KEY"] == "test-credential"
        assert env["SKILL_EVAL_LLM_PROVIDER"] == "openai-compatible"
        assert env["SKILL_EVAL_EMBEDDING_PROVIDER"] == "openai-compatible"
        assert "--autopilot" not in argv and "--skip-baseline" not in argv and "--copy-repo" not in argv
        if argv[1:3] == ["tier3", "validate"]:
            return 0, None
        if "evaluate" in argv:
            assert argv[argv.index("--n-attempts") + 1] == "1"
            assert argv[argv.index("--agent-model") + 1] == "opencode=openai/fixture/chat"
            assert argv[argv.index("--grading-mode") + 1] == "default"
            assert argv[argv.index("--skill-workspace-mode") + 1] == "isolated"
            assert "--include-skills" not in argv
            path = Path(argv[argv.index("--results-dir") + 1]) / "eval-author/run/result.json"
            data = tier3()
        else:
            path = Path(argv[-1]) / "result.json"
            data = tier2("Similarity Check" if argv[1] == "similarity-check" else "Context Deduplication")
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(data))
        if "evaluate" in argv and latest_alias:
            (path.parent.parent / "latest").symlink_to(path.parent.name, target_is_directory=True)
        return 0, None

    monkeypatch.setattr(live, "execute", execute)
    report = live.collect(repo, tmp_path / "live", run=True)
    assert report["counts"] == {"passed": 3, "skipped": 1, "completed": 1}
    assert len(calls) == 5
    assert "PRIVATE-SENTINEL" not in (tmp_path / "live/live-skillevaluator-summary.json").read_text()
    assert "correctness" in (tmp_path / "live/live-skillevaluator-summary.md").read_text()
    with pytest.raises(FileExistsError):
        live.collect(repo, tmp_path / "live", run=True)


@pytest.mark.parametrize("layout", ["two_runs", "linked_run", "linked_report"])
def test_ambiguous_or_linked_tier3_reports_are_not_published(live, repo, tmp_path, monkeypatch, layout):
    monkeypatch.setenv("INFERENCE_HUB_API_KEY", "test-credential")

    def execute(argv, cwd, env, log, timeout):
        if "evaluate" in argv:
            root = Path(argv[argv.index("--results-dir") + 1]) / "eval-author"
            root.mkdir(parents=True)
            external = tmp_path / "external"
            external.mkdir()
            (external / "result.json").write_text(json.dumps(tier3()))
            if layout == "linked_run":
                (root / "run").symlink_to(external, target_is_directory=True)
            else:
                run = root / "run"
                run.mkdir()
                if layout == "linked_report":
                    (run / "result.json").symlink_to(external / "result.json")
                else:
                    (run / "result.json").write_text(json.dumps(tier3()))
                    (root / "second-run").mkdir()
                    (root / "second-run/result.json").write_text(json.dumps(tier3()))
        return 0, None

    monkeypatch.setattr(live, "execute", execute)
    report = live.collect(repo, tmp_path / "live", run=True, tier="3", skill_name="eval-author")
    row = next(row for row in report["observations"] if row["tier"] == 3 and row["skill"] == "eval-author")
    assert row["status"] == "incomplete"
    assert row["reason"] == "report_missing_or_ambiguous"
    assert "arms" not in row


def test_timeouts_and_bad_reports_are_incomplete_and_do_not_stop_collection(live, repo, tmp_path, monkeypatch):
    monkeypatch.setenv("INFERENCE_HUB_API_KEY", "test-credential")

    def execute(argv, cwd, env, log, timeout):
        if argv[1] == "similarity-check":
            path = Path(argv[-1]) / "result.json"
            path.parent.mkdir(parents=True)
            path.write_text('{"results": [null]}')
            return 0, None
        return -9, "timeout"

    monkeypatch.setattr(live, "execute", execute)
    report = live.collect(repo, tmp_path / "broken", run=True, tier="2")
    assert report["counts"] == {"incomplete": 3, "skipped": 2}


def test_input_mutation_invalidates_evidence_and_stops_further_calls(live, repo, tmp_path, monkeypatch):
    monkeypatch.setenv("INFERENCE_HUB_API_KEY", "test-credential")
    calls = []

    def execute(*args):
        calls.append(args)
        (repo / "skills/eval-author/SKILL.md").write_text("changed")
        return -9, "timeout"

    monkeypatch.setattr(live, "execute", execute)
    report = live.collect(repo, tmp_path / "mutated", run=True)
    assert len(calls) == 1
    assert all(r["reason"] in ("skill_changed_during_run", "missing_dataset") for r in report["observations"])
    with pytest.raises(ValueError, match="clean"):
        live.collect(repo, tmp_path / "dirty", run=True)


def test_live_workflow_runs_automatically_and_is_advisory():
    workflow = yaml.safe_load((ROOT / ".github/workflows/skill-evaluation-live.yml").read_text())
    ci = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())
    assert set(workflow[True]) == {"push", "pull_request", "workflow_dispatch"}
    for event in ("push", "pull_request"):
        assert workflow[True][event] == ci[True][event]
    assert workflow[True]["workflow_dispatch"]["inputs"]["run_live"]["default"] is False
    assert workflow[True]["workflow_dispatch"]["inputs"]["tier"]["default"] == "both"
    assert workflow["concurrency"] == ci["concurrency"]
    for job in workflow["jobs"].values():
        assert job["continue-on-error"] is True
        assert "github.event.pull_request.head.repo.full_name == github.repository" in job["if"]
    plan = workflow["jobs"]["plan"]
    assert "environment" not in plan and "secrets." not in json.dumps(plan)
    job = workflow["jobs"]["live"]
    assert all(
        guard in job["if"]
        for guard in ("refs/heads/main", "SKILL_EVALUATION_LIVE_ENABLED", "inputs.run_live", "workflow_dispatch")
    )
    assert job["environment"] == "skill-evaluator" and job["continue-on-error"]
    assert not ci["jobs"]["test"].get("needs")
    upload = job["steps"][-1]
    assert upload["if"] == "always()" and upload["with"]["path"].endswith("live-skillevaluator-summary.*")
    assert workflow["permissions"] == {"contents": "read"}
    assert "provider" not in workflow[True]["workflow_dispatch"]["inputs"]
    evaluation = next(step for step in job["steps"] if step.get("name") == "Run advisory evaluations")
    # Installation/checksum failures must prevent secret-bearing execution.
    assert "if" not in evaluation  # GitHub's default success() gate.
    assert evaluation["env"]["INFERENCE_HUB_API_KEY"] == "${{ secrets.INFERENCE_HUB_API_KEY }}"
    assert workflow["env"]["EVALUATION_TIER"] == (
        "${{ github.event_name == 'pull_request' && '2' || inputs.tier || 'both' }}"
    )
    # Plan and execution must inherit the same policy; no step/job override may
    # accidentally re-enable Tier 3 on PRs.
    for configured_job in workflow["jobs"].values():
        assert "EVALUATION_TIER" not in configured_job.get("env", {})
        for step in configured_job["steps"]:
            assert "EVALUATION_TIER" not in step.get("env", {})
    compose = next(step for step in job["steps"] if step.get("name") == "Install verified Docker Compose runtime")
    assert compose["if"] == "env.EVALUATION_TIER != '2'"
    assert evaluation["env"]["EVALUATION_SKILL"] == "${{ inputs.skill || 'all' }}"
    assert not {"OPENAI_API_KEY", "NVIDIA_API_KEY", "HUB_METADATA_API_KEY"}.intersection(evaluation["env"])


def test_seed_datasets_are_bounded_and_have_negative_cases(live):
    for name in ("eval-author", "mlflow-to-atif"):
        skill = ROOT / "skills" / name
        assert live.dataset_cases(skill) == 4
        cases = json.loads((skill / "evals/evals.json").read_text())["evals"]
        assert sum(c["expected_skill"] is None for c in cases) == 1
        for case in cases:
            for filename in case["files"]:
                assert (skill / "evals" / filename).is_file()


@pytest.mark.parametrize("failure", ["findings", "nested_execution", "timeout", "validation", "missing_report"])
def test_failure_details_survive_in_artifact_summary_and_console(live, repo, tmp_path, monkeypatch, capsys, failure):
    monkeypatch.setenv("INFERENCE_HUB_API_KEY", "fixture-secret-123")

    def execute(argv, cwd, env, log, timeout):
        log.write_text("Actionable failure: connection reset; Bearer fixture-secret-123\n")
        if "validate" in argv:
            return (1 if failure == "validation" else 0), None
        if failure == "timeout":
            return -9, "timeout"
        if failure == "missing_report":
            return 1, None
        if failure == "findings":
            data = tier2()
            row = data["results"][0]
            row.update(status="failed", passed=False)
            row["summary"].update(errors=1, high_count=1)
            row["findings"] = [
                {
                    "check_name": "duplicate",
                    "severity": "high",
                    "file_path": "SKILL.md",
                    "line_number": 42,
                    "message": "Repeated routing instructions <script>bad</script>",
                    "details": "Authorization: Bearer fixture-secret-123",
                    "unrelated_payload": "DO-NOT-EXPORT",
                }
            ]
            path = Path(argv[-1]) / "result.json"
        else:
            data = tier3()
            data["execution_status"] = "failed"
            arm = data["agents"]["opencode"]["conditions"]["without_skill"]
            arm.update(
                execution_status="failed",
                scored_attempts=0,
                execution_errors=["GraderTimeoutError: case one; token=other-secret"],
            )
            path = Path(argv[argv.index("--results-dir") + 1]) / "eval-author/run/result.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(data))
        return 1, None

    monkeypatch.setattr(live, "execute", execute)
    output = tmp_path / "diagnostics"
    report = live.collect(repo, output, run=True, tier="2" if failure == "findings" else "3", skill_name="eval-author")
    row = next(r for r in report["observations"] if r["skill"] == "eval-author" and r["status"] != "skipped")
    published = (output / "live-skillevaluator-summary.json").read_text()
    markdown = (output / "live-skillevaluator-summary.md").read_text()
    console = capsys.readouterr().out
    for text in (published, markdown, console):
        assert "fixture-secret-123" not in text and "other-secret" not in text
        assert "DO-NOT-EXPORT" not in text
        assert "PRIVATE-SENTINEL" not in text
        assert "diagnostics" in text
    if failure == "findings":
        assert "Repeated routing instructions" in published and "SKILL.md" in published
        assert "<script>" not in markdown
        assert row["status"] == "failed"
    elif failure == "nested_execution":
        assert "GraderTimeoutError" in published and "without_skill" in published
        assert "scored_attempts: 0" in published
    else:
        assert "connection reset" in published
        assert row["status"] == "incomplete"


def test_diagnostics_redact_before_truncation_and_ignore_linked_logs(live, tmp_path, monkeypatch):
    import live_evaluation_diagnostics as diagnostic

    secret = 'fixture-secret-"unicode-\u2603'
    monkeypatch.setenv("INFERENCE_HUB_API_KEY", secret)
    report = {"execution_errors": ["x" * 11995 + secret + " trailing error"]}
    result = diagnostic.diagnostics(report, None)
    assert "fixture-secret" not in result and "[diagnostics truncated]" in result
    outside = tmp_path / "outside.log"
    outside.write_text("DO-NOT-EXPORT")
    target = tmp_path / "check"
    target.mkdir()
    (target / "console.log").symlink_to(outside)
    assert "DO-NOT-EXPORT" not in diagnostic.diagnostics({}, target)
    text = diagnostic.redact('password="unknown secret" https://user:pass@example.com/?key=xyz Bearer unknown-token')
    assert all(value not in text for value in ("unknown secret", "user:pass", "xyz", "unknown-token"))


def test_progress_heartbeat_does_not_stream_raw_logs(live, tmp_path, monkeypatch, capsys):
    class Event:
        calls = 0

        def wait(self, seconds):
            assert seconds == 30
            self.calls += 1
            return self.calls > 1

        def set(self):
            pass

    monkeypatch.setattr(live.threading, "Event", Event)

    # Use a synchronous thread double to make the heartbeat deterministic.
    class Thread:
        def __init__(self, target, daemon):
            self.target = target

        def start(self):
            self.target()

        def join(self):
            pass

    monkeypatch.setattr(live.threading, "Thread", Thread)
    monkeypatch.setattr(live, "execute", lambda *args: (1, None))
    assert live.execute_with_progress([], tmp_path, {}, tmp_path / "console.log", 1800) == (1, None)
    text = capsys.readouterr().out
    assert "starting" in text and "running" in text and "finished" in text and "1800s" in text


@pytest.mark.parametrize("fixture,exit_code", [("valid.json", 0), ("missing-instruction.json", 1)])
def test_converter_seed_evidence_matches_expected_behavior(tmp_path, fixture, exit_code):
    skill = ROOT / "skills/mlflow-to-atif"
    output = tmp_path / "converted"
    result = subprocess.run(
        [
            sys.executable,
            str(skill / "scripts/convert_mlflow_to_atif.py"),
            "--input",
            str(skill / "evals/files" / fixture),
            "--output-dir",
            str(output),
            "--agent-name",
            "fixture-agent",
            "--agent-version",
            "1.0",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == exit_code, result.stderr
    trajectories = list(output.glob("*.atif.json"))
    if exit_code:
        assert not trajectories
    else:
        assert len(trajectories) == 1
        assert json.loads(trajectories[0].read_text())["schema_version"] == "ATIF-v1.7"
        assert output.stat().st_mode & 0o777 == 0o700
        assert trajectories[0].stat().st_mode & 0o777 == 0o600


def discover_dataset(repo, cases=8):
    """Build a reviewed-group fixture without depending on authored case text."""
    for name in ("eval-author-discover", "eval-author-audit"):
        skill = repo / "skills" / name
        skill.mkdir(parents=True, exist_ok=True)
        (skill / "SKILL.md").write_text("# Fixture\n")
    skill = repo / "skills/eval-author-discover"
    (skill / "evals").mkdir(exist_ok=True)
    (skill / "evals/config.yml").write_text((ROOT / "skills/eval-author-discover/evals/config.yml").read_text())
    (skill / "evals/evals.json").write_text(
        json.dumps(
            {
                "skill_name": skill.name,
                "evals": [
                    {"id": f"case-{index}", "prompt": "Discover", "expected_output": "Evidence"}
                    for index in range(cases)
                ],
            }
        )
    )
    subprocess.run(["git", "add", "."], cwd=repo, capture_output=True, check=True)
    subprocess.run(
        ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-m", "discover fixture"],
        cwd=repo,
        capture_output=True,
        check=True,
    )
    return skill


def discover_rewards(live, run_dir, cases=8):
    """Match the pinned evaluator's retained reward and aggregate schema."""
    report = tier3()
    agent = report["agents"]["opencode"]
    for arm, dirname in (("with_skill", "with-skill"), ("without_skill", "without-skill")):
        agent["conditions"][arm].update(expected_attempts=cases, scored_attempts=cases)
        agent["pass_at_k"][arm].update(passed_cases=cases, total_cases=cases)
        sums = dict.fromkeys(live.DISCOVER_METRICS, 0)
        for index in range(cases):
            metrics = dict.fromkeys(live.DISCOVER_METRICS, 1)
            if arm == "with_skill" and index == 0:
                # Native pass@1 remains 100%; the artifact check independently fails.
                metrics.update(provider_evidence=0, discover_overall=0)
            for key, value in metrics.items():
                sums[key] += value
            reward = {
                "entry_id": f"case-{index}",
                "trial_id": f"trial-{index}",
                "custom_metrics": metrics,
                "custom_details": {"private": "PRIVATE-SENTINEL"},
            }
            path = run_dir / "opencode" / dirname / "trials" / f"trial-{index}" / "reward.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(reward))
        agent["custom_" + arm] = {key: round(value / cases, 4) for key, value in sums.items()}
    return report


def test_discover_profile_does_not_expand_other_datasets(live, repo):
    skill = discover_dataset(repo)
    assert live.dataset_cases(skill) == 8
    other = repo / "skills/another-skill"
    (other / "evals").mkdir()
    data = json.loads((skill / "evals/evals.json").read_text())
    data["skill_name"] = other.name
    (other / "evals/evals.json").write_text(json.dumps(data))
    with pytest.raises(ValueError, match="one to 4"):
        live.dataset_cases(other)
    data["skill_name"] = skill.name
    data["evals"].append({"id": "ninth", "prompt": "Task", "expected_output": "Evidence"})
    (skill / "evals/evals.json").write_text(json.dumps(data))
    with pytest.raises(ValueError, match="one to 8"):
        live.dataset_cases(skill)


@pytest.mark.parametrize("missing_metric", [False, True])
def test_discover_collection_uses_group_and_reports_custom_evidence(live, repo, tmp_path, monkeypatch, missing_metric):
    discover_dataset(repo)
    monkeypatch.setenv("INFERENCE_HUB_API_KEY", "test-credential")
    calls = []

    def execute(argv, cwd, env, log, timeout):
        calls.append(argv)
        if "validate" in argv:
            return 0, None
        assert argv[argv.index("--grading-mode") + 1] == "default_plus_custom"
        assert argv[argv.index("--skill-workspace-mode") + 1] == "group"
        for option in ("--n-attempts", "--n-concurrent", "--max-agents"):
            assert argv[argv.index(option) + 1] == "1"
        assert "--skip-baseline" not in argv and "--copy-repo" not in argv
        included = [argv[index + 1] for index, value in enumerate(argv) if value == "--include-skills"]
        assert included == [str(repo / "skills" / name) for name in ("eval-author", "eval-author-audit")]
        run_dir = Path(argv[argv.index("--results-dir") + 1]) / "eval-author-discover/run"
        data = discover_rewards(live, run_dir)
        if missing_metric:
            path = run_dir / "opencode/without-skill/trials/trial-7/reward.json"
            reward = json.loads(path.read_text())
            del reward["custom_metrics"]["provider_evidence"]
            path.write_text(json.dumps(reward))
        (run_dir / "result.json").write_text(json.dumps(data))
        return 0, None

    monkeypatch.setattr(live, "execute", execute)
    output = tmp_path / "discover-live"
    report = live.collect(repo, output, run=True, tier="3", skill_name="eval-author-discover")
    row = next(row for row in report["observations"] if row["skill"] == "eval-author-discover" and row["tier"] == 3)
    assert len(calls) == 2
    assert row["cases"] == 8
    assert set(row["input_digests"]) == {"eval-author-discover", "eval-author", "eval-author-audit"}
    assert row["workspace_digest"] == live.sha(json.dumps(row["input_digests"], sort_keys=True).encode())
    if missing_metric:
        assert row["status"] == "incomplete" and row["reason"] == "custom_evidence_incomplete"
        assert "arms" not in row and "deterministic_evidence" not in row
    else:
        assert row["status"] == "completed"
        assert row["arms"]["with_skill"]["pass_rate"] == 1
        assert row["deterministic_evidence"]["arms"]["with_skill"]["passed_cases"] == 7
        assert row["deterministic_evidence"]["arms"]["without_skill"]["passed_cases"] == 8
        assert row["deterministic_evidence"]["pass_rate_lift"] == -0.125
        per_case = row["deterministic_evidence"]["arms"]["with_skill"]["per_case"]
        assert list(per_case) == sorted(f"case-{index}" for index in range(8))
        assert per_case["case-0"] == {
            "passed": False,
            "metrics": dict.fromkeys(live.DISCOVER_METRICS, 1) | {"provider_evidence": 0, "discover_overall": 0},
        }
        assert all(per_case[f"case-{index}"]["passed"] for index in range(1, 8))
        markdown = (output / "live-skillevaluator-summary.md").read_text()
        assert "separate from native pass rate" in markdown
        assert "With skill artifact failures: <code>case-0</code>" in markdown
        assert "Without skill artifact failures: none" in markdown
    assert "PRIVATE-SENTINEL" not in (output / "live-skillevaluator-summary.json").read_text()


@pytest.mark.parametrize("damage", ["missing", "duplicate", "unexpected", "linked", "nonbinary", "mean", "overall"])
def test_custom_evidence_requires_every_expected_case(live, tmp_path, damage):
    report = discover_rewards(live, tmp_path, cases=2)
    path = tmp_path / "opencode/with-skill/trials/trial-0/reward.json"
    reward = json.loads(path.read_text())
    if damage == "missing":
        path.unlink()
    elif damage == "linked":
        target = tmp_path / "linked-reward.json"
        path.rename(target)
        path.symlink_to(target)
    elif damage == "mean":
        report["agents"]["opencode"]["custom_with_skill"]["provider_evidence"] = 1
    else:
        if damage == "duplicate":
            reward["entry_id"] = "case-1"
        elif damage == "unexpected":
            reward["entry_id"] = "not-an-authored-case"
        elif damage == "nonbinary":
            reward["custom_metrics"]["report_created"] = 0.5
        elif damage == "overall":
            reward["custom_metrics"]["discover_overall"] = 1
        path.write_text(json.dumps(reward))
    with pytest.raises(ValueError):
        live.summarize_discover_evidence(report, tmp_path, ["case-0", "case-1"])


def test_discover_missing_sibling_is_incomplete_before_invocation(live, repo, tmp_path, monkeypatch):
    discover_dataset(repo)
    (repo / "skills/eval-author-audit/SKILL.md").unlink()
    monkeypatch.setattr(live, "execute", lambda *args: pytest.fail("invalid group launched a process"))
    report = live.collect(repo, tmp_path / "missing-sibling", tier="3", skill_name="eval-author-discover")
    row = next(row for row in report["observations"] if row["skill"] == "eval-author-discover" and row["tier"] == 3)
    assert row["status"] == "incomplete" and row["reason"] == "invalid_dataset"


@pytest.mark.parametrize("change", ["extra_include", "duplicate_block", "alternate_file", "missing_config"])
def test_discover_config_cannot_expand_reviewed_group(live, repo, tmp_path, monkeypatch, change):
    skill = discover_dataset(repo)
    path = skill / "evals/config.yml"
    config = path.read_text()
    if change == "extra_include":
        path.write_text(config.replace("    - eval-author-audit", "    - eval-author-audit\n    - another-skill"))
    elif change == "duplicate_block":
        path.write_text(config + "\nskill_workspace:\n  mode: group\n  include: [another-skill]\n")
    elif change == "alternate_file":
        (path.parent / "config.yaml").write_text(config)
    else:
        path.unlink()
    monkeypatch.setattr(live, "execute", lambda *args: pytest.fail("unreviewed config launched a process"))
    report = live.collect(repo, tmp_path / "bad-config", tier="3", skill_name="eval-author-discover")
    row = next(row for row in report["observations"] if row["skill"] == "eval-author-discover" and row["tier"] == 3)
    assert row["status"] == "incomplete" and row["reason"] == "invalid_dataset"


def test_discover_reviewed_config_matches_native_group(live):
    skill = ROOT / "skills/eval-author-discover"
    live.validate_discover_config(skill)
    config = yaml.safe_load((skill / "evals/config.yml").read_text())
    profile = live.evaluation_profile(skill)
    assert config["skill_workspace"] == {"mode": "group", "include": profile["included_skills"]}
    assert config["grading"]["mode"] == profile["grading_mode"]


def test_discover_sibling_mutation_invalidates_group_evidence(live, repo, tmp_path, monkeypatch):
    discover_dataset(repo)
    monkeypatch.setenv("INFERENCE_HUB_API_KEY", "test-credential")

    def execute(argv, cwd, env, log, timeout):
        if "validate" in argv:
            return 0, None
        run_dir = Path(argv[argv.index("--results-dir") + 1]) / "eval-author-discover/run"
        (run_dir.parent).mkdir(parents=True)
        data = discover_rewards(live, run_dir)
        (run_dir / "result.json").write_text(json.dumps(data))
        (repo / "skills/eval-author-audit/SKILL.md").write_text("Changed sibling\n")
        return 0, None

    monkeypatch.setattr(live, "execute", execute)
    report = live.collect(repo, tmp_path / "mutated-sibling", run=True, tier="3", skill_name="eval-author-discover")
    row = next(row for row in report["observations"] if row["skill"] == "eval-author-discover" and row["tier"] == 3)
    assert row["status"] == "incomplete" and row["reason"] == "skill_changed_during_run"
    assert "arms" not in row and "deterministic_evidence" not in row
