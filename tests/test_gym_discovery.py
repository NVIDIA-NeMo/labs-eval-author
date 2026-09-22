# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Exercise Gym inventory without requiring its runtime or probing services."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/eval-author-discover/scripts"
spec = importlib.util.spec_from_file_location("gym_inventory", SCRIPTS / "providers/gym/inventory.py")
assert spec and spec.loader
inventory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory)


def write_config(root: Path, relative: str = "resources_servers/lookup/configs/lookup.yaml") -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("""lookup:
  resources_servers:
    lookup:
      entrypoint: app.py
      datasets:
        - name: held-out
          type: validation
          jsonl_fpath: data/tasks.jsonl
          agent: lookup_agent
lookup_agent:
  responses_api_agents:
    simple_agent:
      resources_server: {type: resources_servers, name: lookup}
      model_server: {type: responses_api_models, name: policy_model}
""")
    return path


def test_finds_dataset_on_resources_server_without_claiming_readiness(tmp_path):
    write_config(tmp_path)
    report = inventory.scan(tmp_path)
    assert len(report["configs"]) == 1
    assert report["configs"][0]["datasets"] == [
        {"name": "held-out", "type": "validation", "jsonl_fpath": "data/tasks.jsonl", "agent": "lookup_agent"}
    ]
    assert {c["role"] for c in report["components"]} == {"resources_servers", "responses_api_agents"}
    assert report["runtime"] == {"checked": False}
    assert not report["runnable"] and not report["proven"]


def test_retains_invalid_candidates_and_orphan_manifests(tmp_path):
    path = write_config(tmp_path)
    path.write_text("resources_servers: [broken YAML\n")
    manifest = tmp_path / "benchmarks/missing/manifest.yaml"
    manifest.parent.mkdir(parents=True)
    manifest.write_text("name: missing\nkind: benchmark\n")
    report = inventory.scan(tmp_path)
    assert not report["configs"][0]["parsed"]
    assert report["manifests"][0]["config_path"] == "benchmarks/missing/config.yaml"
    assert not report["runnable"]


def test_does_not_follow_symlinks_or_read_excluded_trees(tmp_path):
    source = write_config(tmp_path / "outside")
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "linked.yaml").symlink_to(source)
    (repo / "external").symlink_to(source.parent, target_is_directory=True)
    write_config(repo, ".venv/candidate.yaml")
    report = inventory.scan(repo)
    assert report["configs"] == []
    assert report["search_limits"]["skipped"] == [{"path": "linked.yaml", "reason": "symlink_not_followed"}]


def test_recursive_yaml_does_not_recurse_forever(tmp_path):
    path = write_config(tmp_path)
    path.write_text("resources_servers: &a\n  cycle: *a\n")
    assert len(inventory.scan(tmp_path)["configs"]) == 1


def test_fingerprint_changes_when_dataset_declaration_changes(tmp_path):
    path = write_config(tmp_path)
    before = inventory.scan(tmp_path)["fingerprint"]
    path.write_text(path.read_text().replace("validation", "train"))
    assert inventory.scan(tmp_path)["fingerprint"] != before


def test_missing_runtime_keeps_inventory(tmp_path):
    write_config(tmp_path)
    report = inventory.validate(inventory.scan(tmp_path), str(tmp_path / "absent-python"))
    assert report["configs"][0]["validation"] == "unavailable"
    assert not report["runnable"]


def test_composition_only_workload_and_json_components(tmp_path):
    wrapper = tmp_path / "environments/lookup/config.yaml"
    wrapper.parent.mkdir(parents=True)
    wrapper.write_text("config_paths:\n  - resources_servers/lookup/configs/lookup.json\n")
    component = tmp_path / "resources_servers/lookup/configs/lookup.json"
    component.parent.mkdir(parents=True)
    component.write_text(json.dumps({"lookup": {"resources_servers": {"lookup": {"entrypoint": "app.py"}}}}))
    (component.parent.parent / "app.py").write_text("# a resources server\n")
    (wrapper.parent / "dataset.jsonl").write_text('{"private": "do not include dataset contents"}\n')
    report = inventory.scan(tmp_path)
    configs = {entry["path"]: entry for entry in report["configs"]}
    assert configs["environments/lookup/config.yaml"]["kind"] == "workload"
    assert configs["environments/lookup/config.yaml"]["config_paths"] == [
        "resources_servers/lookup/configs/lookup.json"
    ]
    assert configs["resources_servers/lookup/configs/lookup.json"]["kind"] == "component"
    assert report["component_directories"] == ["resources_servers/lookup"]
    assert report["dataset_files"] == ["environments/lookup/dataset.jsonl"]
    assert "do not include dataset contents" not in json.dumps(report)


def test_unrelated_config_paths_are_not_gym_workloads(tmp_path):
    (tmp_path / "application.yaml").write_text("config_paths: [application/settings.yaml]\n")
    assert not inventory.scan(tmp_path)["configs"]


def test_auto_cli_reports_gym_first_and_retains_harbor(tmp_path):
    write_config(tmp_path)
    (tmp_path / "harbor.yaml").write_text("tasks:\n  - path: tasks/example\n")
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "discover.py"), "--repo", str(tmp_path), "--inventory-only"],
        capture_output=True,
        text=True,
        check=True,
    )
    report = json.loads(result.stdout)
    assert [p["provider"] for p in report["providers"]] == ["gym", "harbor"]
    assert not report["runnable"]
    rendered = subprocess.run(
        [sys.executable, str(SCRIPTS / "render_report.py")],
        input=result.stdout,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Gym artifacts" in rendered.stdout
    assert "execution have not been checked" in rendered.stdout
    assert "Evidence JSON" in rendered.stdout
