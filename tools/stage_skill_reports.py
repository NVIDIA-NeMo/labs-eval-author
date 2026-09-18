#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Retain complete native JSON reports, excluding runtime homes and linked aliases."""

import argparse
import hashlib
import json
from pathlib import Path


def stage(source: Path, output: Path):
    if source.is_symlink() or output.exists():
        raise ValueError("source must not be linked and output must be new")
    source = source.resolve()
    if output.resolve().is_relative_to(source):
        raise ValueError("output must be outside the source tree")
    manifest = []
    # Tier 1/2 reports and Tier 3 native run results. No logs, HOME, or
    # arbitrary execution artifacts; never follow the native latest alias.
    for pattern in ("*/reports/*.json", "check-*/results/*/*/result.json"):
        for path in sorted(source.glob(pattern)):
            relative = path.relative_to(source)
            if any(parent.is_symlink() for parent in [path, *path.parents] if parent != source):
                continue
            if not path.is_file():
                continue
            raw = path.read_bytes()
            target = output / relative
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            target.write_bytes(raw)
            target.chmod(0o600)
            manifest.append({"path": relative.as_posix(), "sha256": hashlib.sha256(raw).hexdigest()})
    if manifest:
        (output / "manifest.json").write_text(json.dumps({"reports": manifest}, indent=2) + "\n")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    stage(args.source, args.output)
