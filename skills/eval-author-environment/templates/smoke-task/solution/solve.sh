#!/bin/bash
# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

# Reference solution. For each dependency it makes one read and one write through the agent's own
# client code or CLI, inside main, so the check covers the configuration path the agent uses. Each
# write stores the dependency's smoke marker, which never occurs in the starting data. The collect
# hooks in task.toml export the end state after this script exits, as they do after NOP.
set -euo pipefail

# Repeat this block for each dependency.
# FILL: the dependency's name, as in task.toml and tests/test.sh.
dependency="<dependency>"
marker="eval-author-env-smoke-$dependency"
# FILL: read a record the starting data always contains, and fail unless it comes back.
echo "solve.sh: fill in the read for $dependency" >&2; exit 1
# FILL: write one new record that holds "$marker" in a single field. Insert or append rather than
# overwrite, so a write that survived an earlier trial shows up twice.
echo "solve.sh: fill in the write of $marker" >&2; exit 1
