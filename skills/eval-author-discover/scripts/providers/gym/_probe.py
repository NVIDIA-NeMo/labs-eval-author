# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Detect whether NeMo Gym is installed.

Standard library only. The Probe passes when Harbor or Gym is installed. Gym alone
is enough to explore, and to judge and solve Gym manifests. Harbor still judges
every task directory, including the Gym extension tasks that discovery converts.
"""

from __future__ import annotations

import importlib.metadata
import importlib.util
import shutil
import sys
from pathlib import Path

from _checks import ADVISORY, PASS, WARN, CheckResult, check


def probe() -> dict:
    """Report the Gym runtime without importing it."""
    try:
        importable = importlib.util.find_spec("nemo_gym") is not None
    except (ImportError, ValueError):
        importable = False
    version = None
    if importable:
        try:
            version = importlib.metadata.version("nemo-gym")
        except importlib.metadata.PackageNotFoundError:
            version = None
    executable = Path(sys.executable).parent / "gym"
    return {
        "gym_importable": importable,
        "gym_version": version,
        "gym_cli": str(executable) if executable.is_file() else shutil.which("gym"),
    }


def is_available(runtime: dict) -> bool:
    """Return whether NeMo Gym is importable."""
    return bool(runtime["gym_importable"])


def probe_checks(runtime: dict, *, report_missing: bool) -> list[CheckResult]:
    """Report Gym availability; report its absence only when it matters."""
    if runtime["gym_importable"]:
        return [
            check(
                "gym",
                "runtime",
                PASS,
                "NeMo Gym {} is importable.".format(runtime["gym_version"] or "?"),
                severity=ADVISORY,
            )
        ]
    if not report_missing:
        return []
    return [
        check(
            "gym",
            "runtime",
            WARN,
            "NeMo Gym is not importable.",
            severity=ADVISORY,
            hint="Install NeMo Gym (`nemo-gym` from PyPI, or the Gym repository) to run Gym environments.",
        )
    ]
