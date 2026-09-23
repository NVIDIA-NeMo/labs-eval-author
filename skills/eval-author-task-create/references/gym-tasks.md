<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Author and prove a Gym evaluation

Use this provider path to create a task from an existing actionable audit gap
when Gym is selected. It replaces Harbor-specific scaffolding, Oracle, and job
commands; the shared proposal-only boundary, evidence rules, and repeated
measured coverage requirements still apply. Preserve the user's provider choice
and existing suite.

## Scaffold the native draft

Require an installed Gym v0.6.0+ runtime in its separate Python 3.13.14+
environment. Obtain its Python and CLI paths from the existing installation;
use the installed CLI's `--help` before invoking it. If the runtime is missing,
report the prerequisite and retain the proposal without scaffolding.
Keep each draft in a fresh `.eval-author/task-drafts/<task-slug>/` directory.
For an actionable uncovered tool, the existing selector chooses the same gap:

```bash
python scripts/task_pipeline.py scaffold --provider gym \
  --gym-python /path/to/Gym/.venv/bin/python \
  --report <aggregate-coverage.json> --target <tool-name> \
  --out .eval-author/task-drafts/<task-slug> \
  --task-name <org>/<task-slug> --description '<scenario>' --author '<actual-author>' \
  --instruction-file .eval-author/proposals/<task-slug>-instruction.md
```

The wrapper uses Gym's native `scaffold_environment`, puts the proposed
instruction into its example dataset, and records `draft.json`. Hyphenated task
slugs map to underscored Gym module names. **This is a draft, not a verified task.**
The generated example grader, rewards, and verifier cases are placeholders for
the proposed scenario. Replace them; passing template tests does not prove the
proposal works or exercises its selected tool.

## Complete the task without changing its intended capability

- `environments/<name>/manifest.yaml` identifies the environment, reward contract,
  components, dataset, and provenance. Preserve unknown license or authorship
  until the source or user establishes it; a scaffold is not permission to publish.
- `environments/<name>/config.yaml` composes resources, agent, and model roles.
  Configuration is authoritative; keep manifest mirrors consistent.
- `resources_servers/<name>/app.py` implements the scenario tools, per-session
  state/reset, and verifier. Grade the requested outcome; do not award full reward
  merely for a tool call when the requirement includes arguments or side effects.
- Dataset JSONL rows supply `responses_create_params` and task-specific verifier
  fields. Keep expected answers out of the model input unless the task requires
  them. Distinguish training, validation, and benchmark splits. Document fixture
  origins and preserve native application and access requirements.
- `tests/verifier_cases.jsonl` exercises the actual scenario's positive, negative,
  malformed, and partial-credit cases. Include a no-action/empty-output case and
  a known-correct reference response or interaction. These are verifier controls,
  not measurements of a model's ability.

Inspect the installed Gym base request models and a comparable resources server
when authoring. Do not assume Harbor's task.toml, solve.sh, or reward.txt protocol
applies. Stateful tasks need controls against the same stateful tools and reset
behavior, not just fabricated final responses fed to a stateless verifier.

## Validate, run, and retain evidence

From the draft root, using the verified Gym CLI:

```bash
/path/to/Gym/.venv/bin/gym env validate --manifest environments/<name>/manifest.yaml --json
/path/to/Gym/.venv/bin/gym env test <name> --json
```

Gym's verifier fixtures provide the known-correct and no-action/negative controls;
Gym does not use Harbor's `-a oracle` or `-a nop` flags. Inspect observed rewards
and errors, including resets and repeatability. A manifest may validate while a
model is still unconfigured; neither validation nor verifier fixtures establish
service readiness or actual agent performance.

Select the repository's actual agent and its required model configuration. Start
and run it through Gym, retaining the complete composition and input identities.
For the native simple-agent composition and an explicit example JSONL file,
start services in one terminal, then collect in another from the same draft root:

```bash
/path/to/Gym/.venv/bin/gym env start \
  --environment <name> --config /path/to/verified-model-config.yaml \
  +observability_enabled=true

/path/to/Gym/.venv/bin/gym eval run --no-serve --agent <configured-agent-instance> \
  --input environments/<name>/data/example.jsonl \
  --output .eval-author/runs/<run-id>/rollouts.jsonl \
  --num-repeats 2 --concurrency 1
```

Use the head-server address from the running composition when it differs from
Gym's default. In v0.6.0, end-to-end `gym eval run` without `--no-serve` uses
prepared `train`, `validation`, or `benchmark` splits; it rejects `--input` and
`--split example`. For that mode, declare repeats in the dataset configuration.
The example above uses an explicit file and `--num-repeats` against running servers.

Adapt agent selection and dependencies to the inspected repository. Do not
replace the actual agent with a reference implementation to claim gap closure.
Do not disable Gym health checks, discard failed attempts, or mark a missing
model credential as successful execution. Use fresh output paths and retain run
IDs, input digests, Gym revision/version, configured agent/model, rewards,
exceptions, and control results. Only claim a working task after native execution
succeeds; only claim measured gap closure after every required real-agent repeat
closes the selected gap under the existing `verify` command.
