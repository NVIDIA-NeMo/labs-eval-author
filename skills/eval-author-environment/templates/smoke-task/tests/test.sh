#!/bin/bash
# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

# Grades only the export that task.toml's collect hooks wrote, never a live service. Writes one
# "<check-id><tab>PASS|FAIL" row per check to /logs/verifier/results, and reward 1 only when every
# check passes.
set -euo pipefail

# FILL: one entry per dependency: its name, as in task.toml and solution/solve.sh, then a value from
# a record the starting data always contains.
dependencies=(
  "<dependency>|<seeded value>"
)

results=/logs/verifier/results
mkdir -p /logs/verifier
: >"$results"

# An export that is missing or lacks the starting data is an infrastructure error. No reward is
# written, so Harbor records an error rather than a score, and NOP's 0 never comes from a broken
# export.
for entry in "${dependencies[@]}"; do
  export_file="/tmp/export/${entry%%|*}.txt"
  if ! grep -qF -- "${entry#*|}" "$export_file"; then
    printf 'export-readable\tFAIL\n' >>"$results"
    echo "Infrastructure error: $export_file is missing, unreadable, or lacks the starting data."
    exit 1
  fi
done
printf 'export-readable\tPASS\n' >>"$results"

# Each dependency must show its smoke write exactly once. NOP shows none; two mean state survived
# from an earlier trial.
reward=1
for entry in "${dependencies[@]}"; do
  name=${entry%%|*}
  count=$({ grep -oF -- "eval-author-env-smoke-$name" "/tmp/export/$name.txt" || true; } | wc -l)
  status=PASS
  if ((count != 1)); then
    status=FAIL
    reward=0
  fi
  echo "$name: smoke write found $((count)) time(s); expected exactly once."
  printf '%s-smoke-write\t%s\n' "$name" "$status" >>"$results"
done
echo "$reward" >/logs/verifier/reward.txt
