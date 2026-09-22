#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Discover Gym and Harbor evaluations without conflating inventory with execution.

Auto-detection reports Gym first in mixed repositories. --inventory-only reads
files without importing either runtime. Gym native validation uses --gym-python
in a separate process; it never starts services or establishes live readiness.
Harbor retains its native validation ladder and v1 report for Harbor-only repos.
Mixed reports contain both provider reports under a v2 envelope.

Exit 0 means inventory completed when --inventory-only is used. Otherwise it
means the provider established readiness; Gym static checks alone cannot do so.
Run native validation only against trusted repositories. Helpers never install
dependencies, synchronize manifests, fetch datasets, or launch evaluation jobs.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Every bundled module resolves against this directory, so put it on the path
# before importing one. Note that it holds no directory named after a provider
# package: a `harbor/` directory here would satisfy `find_spec("harbor")` on a
# machine without Harbor and make the probe claim an install that is not there.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _checks import CheckResult, required_failures  # noqa: E402
from providers.harbor import _probe  # noqa: E402
from providers.harbor._inventory import RepositoryScan, scan_repository  # noqa: E402

_SCHEMA_VERSION = 1
_MIN_PYTHON = (3, 11)


def _unproven(checks: list[CheckResult]) -> list[CheckResult]:
    """Mark observed findings so they cannot read as evidence."""
    for result in checks:
        result.proven = False
    return checks


async def _judge(scan: RepositoryScan, repo_root: Path) -> list[dict]:
    """Run the validation ladder against each config Harbor can read.

    Imported here rather than at module scope because the ladder imports Harbor,
    which a repository without Harbor does not have.
    """
    from providers.harbor import _ladder

    configs: list[dict] = []
    for candidate in scan.configs:
        outcome = await _ladder.run_ladder(candidate, repo_root)
        configs.append(
            {
                "name": candidate.name,
                "path": _display(candidate.path, repo_root),
                "runnable": not required_failures(outcome.checks),
                "required_env_vars": [
                    {
                        "name": item.name,
                        "default": item.default,
                        "declared_in": _display(item.declared_in, repo_root),
                    }
                    for item in outcome.required_env_vars
                ],
                "checks": [result.as_dict() for result in outcome.checks],
                "_checks": outcome.checks,
            }
        )
    return configs


def _unjudged(scan: RepositoryScan, repo_root: Path) -> list[dict]:
    """Describe each config without claiming anything about it."""
    return [
        {
            "name": candidate.name,
            "path": _display(candidate.path, repo_root),
            "runnable": False,
            "required_env_vars": [],
            "checks": [],
            "_checks": [],
        }
        for candidate in scan.configs
    ]


def _display(path: Path, repo_root: Path) -> str:
    if not path.is_absolute():
        return path.as_posix()
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _run_command(repo_root: Path, configs: list[dict]) -> str | None:
    """Return the Harbor command, only when exactly one config is runnable."""
    runnable = [config for config in configs if config["runnable"]]
    if len(configs) != 1 or len(runnable) != 1:
        return None
    return "cd {} && harbor job start -c {}".format(repo_root, runnable[0]["path"])


def _fail(message: str, hint: str) -> int:
    json.dump({"error": message, "hint": hint}, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 1


async def _harbor_report(repo_root: Path, *, inventory_only: bool = False) -> dict:
    runtime = {} if inventory_only else _probe.probe()
    runtime_checks = [] if inventory_only else _probe.probe_checks(runtime)
    scan = scan_repository(repo_root)
    proven = not inventory_only and _probe.is_available(runtime)
    configs = await _judge(scan, repo_root) if proven else _unjudged(scan, repo_root)

    repository_checks = scan.checks if proven else _unproven(scan.checks)
    grouped = [*runtime_checks, *repository_checks, *(item for config in configs for item in config["_checks"])]
    for config in configs:
        config.pop("_checks")

    runnable = proven and bool(configs) and all(config["runnable"] for config in configs)
    report = {
        "schema_version": _SCHEMA_VERSION,
        "repo_root": repo_root.as_posix(),
        "provider": _probe.PROVIDER,
        "proven": proven,
        "runnable": runnable,
        "runtime": runtime,
        "configs": configs,
        "dataset_paths": [_display(path, repo_root) for path in scan.dataset_paths],
        "task_count": len(scan.task_paths),
        "ethos_path": scan.ethos_path,
        "fingerprint": "sha256:{}".format(scan.fingerprint),
        "input_file_count": scan.input_file_count,
        "discovered_at": datetime.now(timezone.utc).isoformat(),
        "checks": [result.as_dict() for result in grouped],
    }
    report["run_command"] = _run_command(repo_root, configs)

    return report


async def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Discover Gym and Harbor evaluations and validate provider configuration."
    )
    parser.add_argument("--repo", type=Path, default=Path(), help="Repository to inspect.")
    parser.add_argument("--compact", action="store_true", help="Emit single-line JSON.")
    parser.add_argument(
        "--provider",
        choices=("auto", "gym", "harbor", "all"),
        default="auto",
        help="Detect providers; Gym appears first in mixed reports.",
    )
    parser.add_argument("--inventory-only", action="store_true", help="Read files without runtime validation.")
    parser.add_argument("--gym-python", help="Python interpreter with Gym installed; never installs Gym.")
    args = parser.parse_args(argv)

    if sys.version_info < _MIN_PYTHON:
        return _fail(
            "Discovery needs Python {}.{} or later; this is {}.".format(
                _MIN_PYTHON[0], _MIN_PYTHON[1], ".".join(str(part) for part in sys.version_info[:3])
            ),
            "Re-run with a newer interpreter, for example `python3.12 discover.py --repo .`.",
        )

    repo_root = args.repo.expanduser()
    if not repo_root.is_dir():
        return _fail(
            "Not a directory: {}".format(repo_root),
            "Pass the repository that holds your Harbor configs and task directories.",
        )
    repo_root = repo_root.resolve()

    from providers.gym.inventory import scan as scan_gym
    from providers.gym.inventory import validate as validate_gym

    gym = scan_gym(repo_root) if args.provider != "harbor" else None
    gym_found = gym is not None and bool(gym["configs"] or gym["manifests"] or gym["component_directories"])
    if args.provider == "harbor" or (args.provider == "auto" and not gym_found):
        report = await _harbor_report(repo_root, inventory_only=args.inventory_only)
    else:
        assert gym is not None
        if not args.inventory_only:
            gym = validate_gym(gym, args.gym_python or sys.executable)
        if args.provider == "gym":
            report = gym
        else:
            harbor_scan = scan_repository(repo_root)
            providers = [gym]
            if harbor_scan.configs or harbor_scan.task_paths or args.provider == "all":
                providers.append(await _harbor_report(repo_root, inventory_only=args.inventory_only))
            report = {
                "schema_version": 2,
                "provider": "multiple",
                "repo_root": str(repo_root),
                "providers": providers,
                "runnable": False,
                "proven": False,
            }
    runnable = report["runnable"]

    json.dump(report, sys.stdout, indent=None if args.compact else 2)
    sys.stdout.write("\n")
    return 0 if runnable or args.inventory_only else 1


def main(argv: list[str] | None = None) -> int:
    """Run discovery and print the JSON report."""
    return asyncio.run(_main(argv))


if __name__ == "__main__":
    sys.exit(main())
