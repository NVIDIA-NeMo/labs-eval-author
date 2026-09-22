# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Bounded, file-only Gym inventory; no Gym imports or service startup."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

GROUPS = ("resources_servers", "responses_api_agents", "responses_api_models")
EXCLUDED = {".git", ".venv", "venv", "node_modules", "__pycache__", "cache", "jobs", "build", "dist"}
MAX_DEPTH = 6
MAX_BYTES = 2_000_000


def _datasets(value: object, seen: set[int] | None = None) -> list[dict]:
    seen = set() if seen is None else seen
    if not isinstance(value, (dict, list)) or id(value) in seen:
        return []
    seen.add(id(value))
    result = []
    if isinstance(value, dict):
        datasets = value.get("datasets")
        if isinstance(datasets, list):
            for dataset in datasets:
                if isinstance(dataset, dict):
                    result.append(
                        {
                            k: dataset[k]
                            for k in (
                                "name",
                                "type",
                                "jsonl_fpath",
                                "prepare_script",
                                "prompt_config",
                                "agent",
                                "num_repeats",
                            )
                            if k in dataset and isinstance(dataset[k], (str, int, float, bool, type(None)))
                        }
                    )
        children = value.values()
    else:
        children = value
    for child in children:
        result.extend(_datasets(child, seen))
    return result


def scan(repo: Path) -> dict:
    """Retain candidates even when YAML is invalid or its parser is unavailable."""
    try:
        import yaml
    except ImportError:
        yaml = None
    repo = repo.resolve()
    configs, components, manifests, limits = [], [], [], []
    component_directories, dataset_files = [], []
    digest = hashlib.sha256()
    for current, dirs, files in os.walk(repo, followlinks=False):
        directory = Path(current)
        depth = len(directory.relative_to(repo).parts)
        dirs[:] = sorted(
            d
            for d in dirs
            if d not in EXCLUDED and not d.startswith(".") and not (directory / d).is_symlink() and depth < MAX_DEPTH
        )
        parts = directory.relative_to(repo).parts
        if len(parts) >= 2 and parts[-2] in GROUPS and "app.py" in files:
            component_directories.append(directory.relative_to(repo).as_posix())
        for name in sorted(files):
            path = directory / name
            if path.suffix == ".jsonl" and not path.is_symlink():
                dataset_files.append(path.relative_to(repo).as_posix())
            if path.suffix not in {".yaml", ".yml", ".json"}:
                continue
            relative = path.relative_to(repo).as_posix()
            if path.is_symlink():
                limits.append({"path": relative, "reason": "symlink_not_followed"})
                continue
            try:
                if path.stat().st_size > MAX_BYTES:
                    limits.append({"path": relative, "reason": "size_limit"})
                    continue
                raw = path.read_bytes()
                text = raw.decode("utf-8")
            except (OSError, UnicodeError):
                limits.append({"path": relative, "reason": "unreadable"})
                continue
            is_manifest = name in {"manifest.yaml", "manifest.yml"} and any(
                p in {"environments", "benchmarks"} for p in path.relative_to(repo).parts
            )
            # Native workload wrappers can contain only config_paths. Keep these
            # candidates even when their referenced config is missing or invalid.
            composition = bool(re.search(r"\bconfig_paths[\"']?\s*:", text)) and (
                any(p in {"environments", "benchmarks"} for p in path.relative_to(repo).parts)
                or any(f"{group}/" in text for group in GROUPS)
            )
            looks_gym = is_manifest or composition or any(re.search(rf"\b{group}[\"']?\s*:", text) for group in GROUPS)
            if not looks_gym:
                continue
            digest.update(relative.encode() + b"\0" + raw + b"\0")
            parse_error = None
            data = None
            try:
                if path.suffix == ".json":
                    data = json.loads(text)
                elif yaml is not None:
                    data = yaml.safe_load(text)
                else:
                    parse_error = "PyYAML unavailable; candidate not parsed"
            except Exception as exc:
                parse_error = f"{type(exc).__name__}: invalid configuration"
            if not isinstance(data, dict):
                parse_error = parse_error or "expected a mapping"
                data = {}
            entry = {
                "path": relative,
                "parsed": parse_error is None,
                "parse_error": parse_error,
                "datasets": _datasets(data),
                "config_paths": [p for p in data.get("config_paths", []) if isinstance(p, str)]
                if isinstance(data.get("config_paths"), list)
                else [],
                "validation": "not_run",
                "runnable": False,
                "required_env_vars": sorted(set(re.findall(r"\$\{oc\.env:([A-Za-z_][A-Za-z_0-9]*)", text))),
            }
            if is_manifest:
                entry["name"] = data.get("name") if isinstance(data.get("name"), str) else directory.name
                entry["config_path"] = (directory / "config.yaml").relative_to(repo).as_posix()
                manifests.append(entry)
                continue
            servers = []
            for instance, block in data.items():
                if not isinstance(block, dict):
                    continue
                for group in GROUPS:
                    implementations = block.get(group)
                    if isinstance(implementations, dict):
                        for implementation in implementations:
                            if isinstance(implementation, str):
                                servers.append(
                                    {"instance": str(instance), "role": group, "implementation": implementation}
                                )
            entry["components"] = servers
            entry["kind"] = (
                "workload"
                if composition
                or entry["datasets"]
                or any(server["role"] == "responses_api_agents" for server in servers)
                else "component"
            )
            # A component-only config is still useful inventory, not an assembled eval.
            configs.append(entry)
            components.extend(dict(server, config_path=relative) for server in servers)
    return {
        "provider": "gym",
        "repo_root": str(repo),
        "configs": configs,
        "manifests": manifests,
        "components": components,
        "component_directories": component_directories,
        "dataset_files": dataset_files,
        "fingerprint_scope": "candidate_configuration_bytes",
        "fingerprint": "sha256:" + digest.hexdigest(),
        "search_limits": {
            "max_depth": MAX_DEPTH,
            "max_file_bytes": MAX_BYTES,
            "excluded_directories": sorted(EXCLUDED),
            "skipped": limits,
        },
        "proven": False,
        "runnable": False,
        "execution": "not_run",
        "runtime": {"checked": False},
    }


def validate(report: dict, python: str) -> dict:
    """Delegate validation to the selected Gym interpreter; never install dependencies."""
    helper = Path(__file__).with_name("validate.py")
    commands = [(entry, entry["path"], entry["config_path"]) for entry in report["manifests"]]
    manifest_configs = {entry["config_path"] for entry in report["manifests"]}
    commands.extend(
        (entry, None, entry["path"])
        for entry in report["configs"]
        if entry["path"] not in manifest_configs and entry.get("kind") == "workload"
    )
    for entry, manifest, config in commands:
        command = [python, str(helper), "--repo", report["repo_root"], "--config", config]
        if manifest:
            command += ["--manifest", manifest]
        try:
            result = subprocess.run(
                command, cwd=report["repo_root"], capture_output=True, text=True, timeout=90, check=False
            )
            payload = json.loads(result.stdout)
            if not isinstance(payload, dict) or "status" not in payload:
                raise ValueError("invalid validation response")
            entry["validation"] = payload["status"]
            entry["validation_evidence"] = payload
            report["runtime"] = payload.get("runtime", {"checked": True})
        except (OSError, subprocess.TimeoutExpired, ValueError):
            entry["validation"] = "unavailable"
            entry["validation_evidence"] = {"error": "Gym interpreter unavailable, timed out, or returned no report"}
    # Static validation never establishes live runtime readiness or agent performance.
    return report
