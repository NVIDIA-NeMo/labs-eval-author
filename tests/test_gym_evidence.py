# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""A successful process or skipped suite must never become measured compatibility."""

import importlib.util
import json
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "gym_evidence", Path(__file__).resolve().parents[1] / "tools/collect_gym_evidence.py"
)
assert spec and spec.loader
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)


def evidence(root, marks=("", "")):
    nodes = "".join(f'<testcase name="{name}">{mark}</testcase>' for name, mark in zip(collector.TESTS, marks))
    (root / "junit.xml").write_text(f"<testsuites><testsuite>{nodes}</testsuite></testsuites>")
    native = root / "native"
    native.mkdir()
    (native / "summary.json").write_text(json.dumps({**collector.EXPECTED, "model_performance_measured": False}))
    (native / "quality_summary.json").write_text(
        json.dumps(
            {
                "run": {
                    "verdicts": {"healthy": 0, "unhealthy": 0, "unobserved": 4},
                    "ignored_checks": [],
                    "artifacts": {"records": 4},
                }
            }
        )
    )


def test_valid_controls_preserve_unobserved_health(tmp_path):
    evidence(tmp_path)
    result = collector.summarize(tmp_path, 0)
    assert result["status"] == "passed"
    assert result["rollout_health"]["unobserved"] == 4


@pytest.mark.parametrize(
    "marks,status",
    [(("<skipped/>", ""), "incomplete"), (("", "<failure/>"), "failed"), (("<error/>", ""), "incomplete")],
)
def test_missing_execution_is_not_a_pass(tmp_path, marks, status):
    evidence(tmp_path, marks)
    assert collector.summarize(tmp_path, 0)["status"] == status


def test_successful_exit_needs_native_evidence(tmp_path):
    evidence(tmp_path)
    (tmp_path / "native/summary.json").unlink()
    assert collector.summarize(tmp_path, 0)["status"] == "incomplete"


@pytest.mark.parametrize(
    "xml",
    [
        "broken",
        "<testsuites/>",
        '<testsuite><testcase name="other"/></testsuite>',
        '<testsuite><testcase name="test_native_http_execution_controls"/>'
        '<testcase name="test_native_http_execution_controls"/></testsuite>',
    ],
)
def test_incomplete_or_changed_panel_does_not_pass(tmp_path, xml):
    evidence(tmp_path)
    (tmp_path / "junit.xml").write_text(xml)
    assert collector.summarize(tmp_path, 0)["status"] == "incomplete"


def test_exit_failure_cannot_be_hidden_by_old_success(tmp_path):
    evidence(tmp_path)
    assert collector.summarize(tmp_path, 1)["status"] == "incomplete"


def test_runtime_failure_still_writes_summary(tmp_path):
    output = tmp_path / "run"
    code = collector.run(output, "/nonexistent/python", tmp_path, "a" * 40, 1)
    report = json.loads((output / "gym-summary.json").read_text())
    assert code == 1
    assert report["status"] == "incomplete" and report["metrics"] is None
    assert report["finished_at"] is not None
    with pytest.raises(FileExistsError):
        collector.run(output, "/nonexistent/python", tmp_path, "a" * 40, 1)


def test_socket_restriction_is_infrastructure_not_a_control_failure(tmp_path, monkeypatch):
    def blocked():
        raise PermissionError("socket unavailable")

    monkeypatch.setattr(collector, "check_local_http", blocked)
    output = tmp_path / "restricted"
    assert collector.run(output, "/unused/python", tmp_path, "a" * 40, 1) == 1
    report = json.loads((output / "gym-summary.json").read_text())
    assert report["status"] == "incomplete"
    assert report["reason"] == "runtime_or_test_execution_error"
    assert set(report["checks"].values()) == {"missing"}
