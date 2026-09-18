<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Temporary: Trace Intel ingestion package

**Status: temporary document.** Delete it once the migration it describes either
happens or is explicitly abandoned. It exists so the next person to touch Gym
conversion evaluates the shared ingestion package before extending this skill's
local adapter.

## What it is

[Trace Intel's `packages/trace-ingest`](https://github.com/NVIDIA-NeMo/labs-trace-intel/tree/main/packages/trace-ingest)
is the shared, provider-neutral trace ingestion library: canonical Pydantic
trace models (`trace_ingest.models`: `Trace`, `Span`, `SpanKind`, `ToolCall`,
`TokenCounts`, ...) plus one loader per provider. It exists so trace evidence
streams and the Trace Analyst share one normalization contract instead of every
consumer growing its own converter — which is what this skill's `gym_to_atif.py`
currently is.

Loaders present at revision `c7c4c1e3e6f5af5adb77bd779fc0ab2f4615f1b2`:

- `atif` — ATIF JSONL corpora;
- `mlflow` — file export and live store;
- `langsmith`, `langfuse`, `braintrust` — file and/or live;
- `intake` — NeMo Intake;
- `fs` — local filesystem layout.

There is **no Gym loader**. Gym Responses rollouts are not yet represented.

Install a pinned revision (never a floating branch):

```bash
uv add "git+https://github.com/NVIDIA-NeMo/labs-trace-intel#subdirectory=packages/trace-ingest" \
  --rev <commit-sha>
```

## Relationship to this skill

- `gym-to-atif` remains the authoritative Gym→ATIF path for Eval Author until
  trace-ingest grows a Gym loader **and** an ATIF emission path. The loader
  alone only yields the canonical model; `eval-author-trace-environment`
  consumes ATIF files.
- The same applies to the sibling `mlflow-to-atif` skill: trace-ingest has an
  MLflow loader, but until it emits canonical ATIF with the documented loss
  recording, the local converter stands.
- When a Gym loader lands upstream, port this adapter's contract first: the
  source-of-truth ordering (retained Harbor ATIF > native record > explicit
  projection fallback), the never-fetch-paths/URLs rule, the JSONL `--row`
  selection semantics, the content-free error boundary, and the loss/uncertainty
  recording. The fixtures in `tests/test_gym_to_atif.py` encode that contract.

## Boundaries that survive any migration

Regardless of where conversion code lives, these are evidence-handling rules,
not implementation details: sources stay owner-private; unknown fields remain in
the retained raw record; missing human input is never invented; recorded reward
is not ground truth; and nothing follows paths embedded in trace metadata.
