# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Fetch an explicitly pinned private runtime/suite ZIP without disclosing its URL."""

import argparse
import base64
import hashlib
import io
import os
import re
import stat
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

LIMIT = 20_000_000
PART_SIZE = 40_000
PART_COUNT = 4


def fetch():
    """Prefer the private bundle configured by configure_semantic_ci.py."""
    parts = [os.environ.get(f"SEMANTIC_BUNDLE_PART_{i}", "") for i in range(1, PART_COUNT + 1)]
    if any(parts):
        if any(len(part) > PART_SIZE for part in parts) or any(
            parts[i] and not parts[i - 1] for i in range(1, len(parts))
        ):
            raise ValueError("invalid bundle parts")
        return base64.b64decode("".join(parts), validate=True)
    url = os.environ["SEMANTIC_BUNDLE_URL"]
    if not url.startswith("https://"):
        raise ValueError("HTTPS required")
    with urllib.request.urlopen(url, timeout=60) as response:
        if not response.url.startswith("https://"):
            raise ValueError("HTTPS required")
        return response.read(LIMIT + 1)


def unpack(data, expected, destination):
    if not re.fullmatch("[0-9a-f]{64}", expected) or hashlib.sha256(data).hexdigest() != expected:
        raise ValueError("bundle digest mismatch")
    if len(data) > LIMIT:
        raise ValueError("bundle too large")
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        members = archive.infolist()
        if len(members) > 1000 or sum(m.file_size for m in members) > LIMIT:
            raise ValueError("bundle expanded size exceeded")
        names = set()
        for member in members:
            name = PurePosixPath(member.filename)
            if (
                name.is_absolute()
                or ".." in name.parts
                or "\\" in member.filename
                or any(p.startswith(".") for p in name.parts)
                or stat.S_ISLNK(member.external_attr >> 16)
                or member.filename in names
                or (name.parts[0] not in ("ratchet", "baselines") and str(name) != "suite.json")
            ):
                raise ValueError("invalid bundle member")
            names.add(member.filename)
        if "suite.json" not in names or "ratchet/scripts/cli.py" not in names:
            raise ValueError("missing bundle inputs")
        destination.mkdir(parents=True, exist_ok=False)
        for member in members:
            path = destination / member.filename
            if member.is_dir():
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(archive.read(member))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        unpack(fetch(), os.environ["SEMANTIC_BUNDLE_SHA256"], args.output)
    except Exception:
        # Signed URLs, credentials, private paths and provider errors must not reach CI logs.
        raise SystemExit("Could not provision the pinned semantic regression bundle") from None


if __name__ == "__main__":
    main()
