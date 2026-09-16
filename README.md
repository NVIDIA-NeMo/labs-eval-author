<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# NeMo Eval Author

Skills that an agent reads to work on the evaluation suites in a user's own
repository, derive private environments from trace evidence, and understand
traces from NeMo Intake. This directory provides no
installed public package or service, so a customer points their agent at
`skills/` and nothing gets installed.

The audit sub-flow also ships a bundled validator CLI at
[`skills/eval-author-audit/scripts/audit_spec/validate.py`](skills/eval-author-audit/scripts/audit_spec/validate.py)
and private helper modules under `scripts/audit_spec/`. They are invoked from the
copied skill tree, not published as a package API.

## Prerequisites

Harbor is required to create, validate, and run eval tasks; see the
[setup guide](skills/eval-author-discover/references/harbor-setup.md) for missing
or broken installations. First-eval creation and non-Harbor adaptation also require
an applicable local Ethos before evaluation design. The bundled
[Local Ethos procedure](skills/eval-author/references/local-ethos.md) supports
reuse and creation without a NeMo service, account, or upload.

Discovery imports nothing beyond the standard library and Harbor itself, so it
runs on whatever Python the customer already has. Audit generation and
validation need PyYAML to read YAML and jsonschema to enforce
`schemas/audit.schema.json`; audit measurement and reporting use
`skills/eval-author-audit/requirements.txt`. Trace inspection requires the
supported `nemo` CLI, an explicit workspace, and read access to a configured
local or remote NeMo Platform instance.

Development uses Python 3.12 or 3.13 and uv. The development dependency group
includes the test runner, validators, MCP, and the Harbor version used by the
source monorepo. No NeMo Platform checkout is required.

| Skill | Role |
| --- | --- |
| [`eval-author`](skills/eval-author/SKILL.md) | Core. Owns the standard every sub-flow follows and routes to one. |
| [`eval-author-first-eval`](skills/eval-author-first-eval/SKILL.md) | Sub-flow. Plans and builds a small working starter suite while explaining how to run and extend it. |
| [`eval-author-discover`](skills/eval-author-discover/SKILL.md) | Sub-flow. Records whether a repository's Harbor evals are ready to run. |
| [`eval-author-adapt`](skills/eval-author-adapt/SKILL.md) | Sub-flow. Converts non-Harbor evals while preserving their cases and scoring rules. |
| [`eval-author-audit`](skills/eval-author-audit/SKILL.md) | Sub-flow. Validates an existing finite `audit.md` coverage denominator. |
| [`eval-author-inspect-trace`](skills/eval-author-inspect-trace/SKILL.md) | Sub-flow. Not user-invocable. Explains one Intake trace after `eval-author` selects it. |
| [`eval-author-task-create`](skills/eval-author-task-create/SKILL.md) | Sub-flow. Creates and proves one Harbor task from an actionable audit gap. |
| [`eval-author-trace-environment`](skills/eval-author-trace-environment/SKILL.md) | Sub-flow. Converts one canonicalized trace into a private candidate, inventories ground truth and software constraints, and builds a reproducible Harbor task environment when supported. |
| [`mlflow-to-atif`](skills/mlflow-to-atif/SKILL.md) | Utility. Normalizes bounded MLflow exports to canonical ATIF. |

Discovery also reports availability of the optional
[Harbor assistant skills](https://github.com/harbor-framework/harbor/tree/main/skills).

## Where findings go

Repository onboarding opens with the plan, then establishes Ethos, introduces and
checks Harbor, and discovers the evaluation starting point. It then routes to
first-eval creation or adaptation according to the selected material. The core owns the
[shared checklist](skills/eval-author/SKILL.md#show-the-path-ahead), with
[stage check-ins](skills/eval-author/references/milestone-checkins.md) for discussing
progress before advancing.

For a local skill tree, invoke the entrypoint and load supporting instructions as
each stage needs them:

```text
Use Eval Author at <skill-tree>/eval-author/SKILL.md to help me get my evals working
in this repository. Show me the plan first. Load sub-flows and references from
that same local skill tree as needed for the current stage.
```

First-eval saves its plan in `.eval-author/first-eval.md`, drafts under
`.eval-author/task-drafts/`, and a run config in `.eval-author/first-eval.yaml`.
Adaptation saves its source mapping in `.eval-author/adaptation.md` and drafts
under `.eval-author/adapted-tasks/`, preserving the source cases and scoring rules.
After a completed agent evaluation, offer help creating more evals through an
optional repository and coverage audit; see the shared
[post-evaluation handoff](skills/eval-author/references/milestone-checkins.md#after-a-successful-evaluation).

`eval-author-discover` leaves a report at `.eval-author/discovery.md`, carrying the
JSON in an evidence section so a later model reads the verdict without Harbor. It is
visible and worth committing: a teammate who reads it skips the discovery pass.

`eval-author-inspect-trace` leaves one report per trace under
`.eval-author/traces/`. The front matter carries Intake source metadata and the
exact read commands. Findings use `behavior`, `issue`, `recovery`, and
`uncertainty` categories.

`eval-author-trace-environment` creates one owner-private, gitignored workspace
per task under `.eval-author/trace-environments/`. Each finalized workspace has
a `candidate` or `no_candidate` summary and keeps restricted source evidence
separate from its text-only scrubbed ATIF copy.

Discovery scripts write no files. Audit scripts write only the requested
`.eval-author/` artifacts and report JSON summaries to stdout. Trace inspection
contains instructions only.
The trace-environment helper reports to stdout and writes only its documented
artifacts under `.eval-author/`.
Capability and failure-case measurement can also consume local skill-authored
judgment sidecars for non-tool evidence; deterministic tool requirements and
prohibited-tool checks still come from ATIF traces.

## Why skills instead of an agent

Harbor tasks live in the customer's repository, so an agent that proposes changes
has to write to that repository. Customers were unwilling to grant that, sandboxed
or not. A skill inverts the arrangement: the customer's own agent does the work,
and this directory only supplies the instructions and the deterministic scripts.

The Eval Author agent that Experimentalist insight mode still uses lives in
[the Experimentalist plugin](https://github.com/NVIDIA-NeMo/nemo-platform/tree/main/plugins/nemo-experimentalist/src/nemo_experimentalist_plugin/eval_author).

## Dependencies

Adding a runtime dependency to a bundled script is a breaking change for anyone who
copied the skill, so the contract test walks each script's imports and fails on
anything outside the standard library, a sibling module, or the explicitly allowed
third-party validators.

Trace inspection uses read-only `nemo intake` commands. The CLI handles its
contexts, authentication, transport, filters, pagination, and errors.

The standalone trace-environment helper requires Python 3.11 or newer. Proving
a candidate requires Harbor and Docker for the `harbor run -a nop` and
`harbor run -a oracle` checks; without them, the environment remains unproven.
The flow does not require model or provider configuration.

## License

Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.

Eval Author is licensed under the [Apache License, Version 2.0](LICENSE).
See [NOTICE](NOTICE) for attributions and the external-materials disclaimer,
and [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) for dependency licenses
and links to their full upstream notices.

The bundled JSON examples and synthetic test fixtures are NVIDIA-authored and
covered by the project license.

## Development

Contributions are currently limited to the ASE team. See
[CONTRIBUTING.md](CONTRIBUTING.md) for development checks, review requirements,
and the CI policy.

```bash
uv sync --locked
uv run --locked pytest -q
uv run --locked ruff check .
uv run --locked ruff format --check .
make check-copyright-headers
make check-licenses
```

After dependency changes, run `make update-licenses` and commit the generated
disclosures. License generation and checking require OSV-Scanner 2.3.3 and network
access. See [DEVELOPMENT.md](DEVELOPMENT.md) for the licensing workflow.

The default tests use synthetic local evidence and mocked providers. Tests that
need a running environment backend skip when one is unavailable. The optional
Ethos parser compatibility test skips without the NeMo Agents plugin. Live
model execution is opt-in; see [trace fixture checks](docs/trace-derived-fixtures.md#regression-checks).
