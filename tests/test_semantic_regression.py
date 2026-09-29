# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import io
import json
import os
import stat
import sys
import zipfile
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import fetch_semantic_bundle as bundles
import semantic_regression as semantic


def suite():
    return {
        "schema": "nemo.semantic_suite.v1",
        "runs": 5,
        "models": {"author": "author-v1", "extractor": "extractor-v1", "judge": "judge-v1"},
        "cases": [
            {"id": "audit", "query": "Explain the evidence.", "skill_files": ["skills/eval-author-audit/SKILL.md"]}
        ],
    }


def test_plan_and_missing_baseline_never_call_models(tmp_path):
    path = tmp_path / "suite.json"
    semantic.dump(path, suite())

    def forbidden(*args):
        pytest.fail("model was called")

    for mode in ("plan", "check"):
        result = semantic.run(path, None, tmp_path / mode, mode, forbidden)
        assert result["observations"][0]["status"] == "incomplete"
        assert result["observations"][0]["metrics"] is None
        assert "claims" not in (tmp_path / mode / "semantic-regression-summary.json").read_text()


def test_failure_keeps_all_cases_and_publishes_checkpoint(tmp_path, monkeypatch):
    spec = suite()
    spec["cases"][0]["baseline"] = "missing/lock.json"
    spec["cases"].append({**spec["cases"][0], "id": "second"})
    path = tmp_path / "suite.json"
    semantic.dump(path, spec)

    def broken(*args):
        raise ValueError("secret provider body")

    monkeypatch.setattr(semantic, "check_case", broken)
    result = semantic.run(path, None, tmp_path / "out", "check", object())
    assert len(result["observations"]) == 2
    assert all(r["reason"] == "execution_or_input_error" for r in result["observations"])
    assert "secret" not in (tmp_path / "out/semantic-regression-summary.json").read_text()


def test_retention_match_requires_exact_claim_accounting():
    source = {"run_ids": ["r1"], "claims": [{"run_id": "r1", "claim_idx": 0}]}
    baseline = {"core_cluster_ids": ["c1"]}
    match = {"run_ids": ["r1"], "clusters": [{"cluster_id": "c1", "members": source["claims"]}], "unmatched": []}
    semantic.validate_match(match, source, baseline)
    for invalid in (
        {**match, "run_ids": ["r2"]},
        {**match, "unmatched": source["claims"]},
        {**match, "clusters": []},
        {**match, "clusters": [{"cluster_id": "invented", "members": source["claims"]}]},
    ):
        with pytest.raises(ValueError):
            semantic.validate_match(invalid, source, baseline)


def test_template_does_not_expand_placeholders_inside_evidence(tmp_path):
    (tmp_path / "prompts").mkdir()
    (tmp_path / "prompts/p.md").write_text("{{RESULT}} {{RUN_ID}}")
    result = semantic.prompt(tmp_path, "p.md", {"RESULT": "{{RUN_ID}}", "RUN_ID": "r1"})
    assert result.endswith("{{RUN_ID}} r1")


@pytest.mark.parametrize(
    "name,symlink", [("../escape", False), ("/escape", False), ("ratchet/x.py", True), ("ratchet/.hidden", False)]
)
def test_bundle_rejects_unsafe_members(tmp_path, name, symlink):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        member = zipfile.ZipInfo(name)
        if symlink:
            member.external_attr = (stat.S_IFLNK | 0o777) << 16
        archive.writestr(member, "outside")
    raw = buffer.getvalue()
    with pytest.raises(ValueError):
        bundles.unpack(raw, semantic.sha(raw), tmp_path / "bundle")
    assert not (tmp_path / "bundle").exists()


def test_bundle_pin_and_layout(tmp_path):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("suite.json", "{}")
        archive.writestr("ratchet/scripts/cli.py", "# external runtime")
    raw = buffer.getvalue()
    with pytest.raises(ValueError):
        bundles.unpack(raw, "0" * 64, tmp_path / "bad")
    bundles.unpack(raw, semantic.sha(raw), tmp_path / "ok")
    assert (tmp_path / "ok/suite.json").read_text() == "{}"


def test_workflow_main_only_credentials_and_no_calibration():
    path = semantic.ROOT / ".github/workflows/semantic-regression.yml"
    workflow = yaml.safe_load(path.read_text())
    live = workflow["jobs"]["live"]
    assert "github.ref == 'refs/heads/main'" in live["if"]
    assert live["environment"] == "skill-evaluator"
    assert live["continue-on-error"] is True
    assert workflow["permissions"] == {"contents": "read"}
    assert "--mode calibrate" not in path.read_text() and "--mode lock" not in path.read_text()
    assert "secrets." not in json.dumps(workflow["jobs"]["plan"])
    upload = live["steps"][-1]
    assert upload["if"] == "always()" and "semantic-publish" in upload["with"]["path"]


class ScriptedModel:
    """Fixed synthetic responses exercise the real external scoring pipeline, not inference."""

    def __init__(self, empty=False):
        self.ids = []
        self.empty = empty

    def __call__(self, model, prompt, structured=False):
        if model == "author-v1":
            return "" if self.empty else "Excel coverage is unmeasured. Native CAD fidelity remains unproven."
        if model == "extractor-v1":
            # The upstream template includes a run_id placeholder in its JSON example.
            import re

            matched = re.search(r'"run_id": "([a-f0-9]+-r\d+)"', prompt)
            assert matched is not None
            run_id = matched[1]
            self.ids.append(run_id)
            return {
                "run_id": run_id,
                "claims": []
                if self.empty
                else [
                    {"text": "Excel coverage is unmeasured.", "evidence": "Excel coverage is unmeasured."},
                    {
                        "text": "Native CAD fidelity remains unproven.",
                        "evidence": "Native CAD fidelity remains unproven.",
                    },
                ],
            }
        if "# Prompt: cluster" in prompt:
            return {
                "run_ids": self.ids,
                "clusters": [
                    {"cluster_id": f"c{i}", "canonical": t, "example": t, "texts": [t]}
                    for i, t in enumerate(("Excel coverage is unmeasured.", "Native CAD fidelity remains unproven."))
                ],
            }
        return {
            "run_ids": [self.ids[0]],
            "clusters": [
                {"cluster_id": f"c{i}", "members": [{"run_id": self.ids[0], "claim_idx": i}]} for i in range(2)
            ],
            "unmatched": [],
        }


def test_real_ratchet_calibrate_review_compare_and_damage(tmp_path):
    external = os.environ.get("RATCHET_TEST_RUNTIME")
    if not external:
        pytest.skip("external Ratchet runtime not redistributed; set RATCHET_TEST_RUNTIME for integration")
    runtime = Path(external)
    spec = suite()
    path = tmp_path / "suite.json"
    semantic.dump(path, spec)
    result = semantic.run(path, runtime, tmp_path / "calibration", "calibrate", ScriptedModel())
    assert result["observations"][0]["reason"] == "awaiting_baseline_review"
    packet = tmp_path / "calibration/audit"
    mapping_hash = semantic.sha((packet / "mapping.md").read_bytes())
    with pytest.raises(ValueError):
        semantic.lock_packet(packet, "0" * 64, tmp_path / "bad-lock", runtime)
    semantic.lock_packet(packet, mapping_hash, tmp_path / "locked", runtime)
    with pytest.raises(FileExistsError):
        semantic.lock_packet(packet, mapping_hash, tmp_path / "locked", runtime)
    spec["cases"][0]["baseline"] = "locked/lock.json"
    semantic.dump(path, spec)
    passed = semantic.run(path, runtime, tmp_path / "healthy", "check", ScriptedModel())
    assert passed["observations"][0]["status"] == "passed"
    assert passed["observations"][0]["metrics"]["retention"] == 1
    failed = semantic.run(path, runtime, tmp_path / "damaged", "check", ScriptedModel(empty=True))
    assert failed["observations"][0]["status"] == "regression"
    assert failed["observations"][0]["metrics"]["retention"] == 0
    assert failed["observations"][0]["metrics"]["presence_passed"] is False

    def unavailable(*args):
        raise OSError("provider unavailable")

    interrupted = semantic.run(path, runtime, tmp_path / "interrupted", "check", unavailable)
    row = interrupted["observations"][0]
    assert row["status"] == "incomplete" and row["metrics"] is None
    assert row["comparison_digest"] == passed["observations"][0]["comparison_digest"]
    spec["models"]["judge"] = "changed-v2"
    semantic.dump(path, spec)
    aborted = semantic.run(path, runtime, tmp_path / "changed", "check", ScriptedModel())
    assert aborted["observations"][0]["status"] == "incomplete"
