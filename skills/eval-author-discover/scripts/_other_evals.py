# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Point at evaluation code that is neither a Harbor nor a Gym task.

Standard library only. These are leads for the agent to raise with the user, who
decides whether to convert them. They never count as discovered evals, and a
heuristic hit proves nothing about what the code does.

A directory is a lead when it holds an eval-named file, or a file carrying one of
the trace formats the rest of Eval Author reads: OpenTelemetry, MLflow tracing,
ATIF trajectories, or NeMo Intake.
"""

from __future__ import annotations

import re
from pathlib import Path

from providers.harbor._explore import walk_dirs

_CODE_SUFFIXES = frozenset({".py", ".ipynb", ".js", ".ts", ".sh"})
# Data files count only for ATIF, so a package.json that merely lists a tracing SDK is not a lead.
_DATA_SUFFIXES = frozenset({".json", ".jsonl"})
_MAX_READ_BYTES = 256 * 1024
_MAX_CANDIDATES = 50
_EVAL_NAME = re.compile(r"(?:^|[_.-])(?:evals?|evaluat(?:e|ion|or)|bench(?:mark)?s?)(?:[_.-]|$)", re.IGNORECASE)
_NAME_SIGNAL = "eval-named file"
_ATIF_SIGNAL = "holds ATIF trajectories"
# Each trace format and the bytes that mark it.
_TRACE_SIGNALS = {
    "imports OpenTelemetry": re.compile(rb"opentelemetry"),
    "uses MLflow tracing": re.compile(rb"mlflow\.(?:trace|start_span|get_trace|search_traces|genai)\b"),
    _ATIF_SIGNAL: re.compile(rb"ATIF-v\d"),
    "sends to NeMo Intake": re.compile(rb"apis/intake/|nemo intake "),
}


def find(repo_root: Path, owned: list[Path]) -> list[dict]:
    """Return directories holding eval-like code outside ``owned`` Harbor and Gym paths."""
    owned_roots = [path.resolve() for path in owned]
    candidates: list[dict] = []
    for directory in walk_dirs(repo_root):
        resolved = directory.resolve()
        if any(resolved == root or resolved.is_relative_to(root) for root in owned_roots):
            continue
        signals: set[str] = set()
        files: list[str] = []
        try:
            entries = sorted(directory.iterdir())
        except OSError:
            continue
        for path in entries:
            if path.is_symlink() or not path.is_file():
                continue
            found = _signals(path)
            if found:
                signals |= found
                files.append(path.name)
        if signals:
            candidates.append(
                {
                    "path": directory.relative_to(repo_root).as_posix() or ".",
                    "signals": sorted(signals),
                    "files": files,
                }
            )
            if len(candidates) == _MAX_CANDIDATES:
                break
    return candidates


def _signals(path: Path) -> set[str]:
    suffix = path.suffix.lower()
    if suffix in _CODE_SUFFIXES:
        names = set(_TRACE_SIGNALS)
        signals = {_NAME_SIGNAL} if _EVAL_NAME.search(path.stem) else set()
    elif suffix in _DATA_SUFFIXES:
        names, signals = {_ATIF_SIGNAL}, set()
    else:
        return set()
    try:
        with path.open("rb") as source:
            head = source.read(_MAX_READ_BYTES)
    except OSError:
        return signals
    return signals | {name for name in names if _TRACE_SIGNALS[name].search(head)}
