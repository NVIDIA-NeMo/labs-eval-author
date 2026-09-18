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
or broken installations. First-eval creation also requires
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
| [`eval-author-audit`](skills/eval-author-audit/SKILL.md) | Sub-flow. Defines, validates, and measures intended behavior coverage against available trace evidence. |
| [`eval-author-inspect-trace`](skills/eval-author-inspect-trace/SKILL.md) | Sub-flow. Not user-invocable. Explains one Intake trace after `eval-author` selects it. |
| [`eval-author-task-create`](skills/eval-author-task-create/SKILL.md) | Sub-flow. Proposes eval improvements from audit findings; when requested, creates and proves one eligible tool-gap task. |
| [`eval-author-trace-environment`](skills/eval-author-trace-environment/SKILL.md) | Sub-flow. Converts one canonicalized trace into a private candidate, inventories ground truth and software constraints, and builds a reproducible Harbor task environment when supported. |
| [`mlflow-to-atif`](skills/mlflow-to-atif/SKILL.md) | Utility. Normalizes bounded MLflow exports to canonical ATIF. |

Adaptation is temporarily disabled and is not an available route. Its instructions
are retained in `skills/eval-author-adapt/SKILL.md.disabled` for possible restoration;
the directory has no active `SKILL.md`. Discovery can still inventory existing
non-Harbor material, but does not convert it into Harbor tasks.

Discovery also reports availability of the optional
[Harbor assistant skills](https://github.com/harbor-framework/harbor/tree/main/skills).

## Getting started

Eval Author selects the entry route from the user's starting situation and request:

| Starting situation | Entry route |
| --- | --- |
| No evals; help me bootstrap some | First-eval authoring, with a plan and guided milestones |
| Existing evals; audit them | Audit's own intent and coverage workflow |
| Unsure whether or where evals exist | Report what exists and how to run it from the inspected docs and source, then ask whether the user wants an audit |
| An audit is available; propose new evals | Ranked proposals, stopping before task creation or execution unless requested |

Readiness-only and other scoped requests keep their own routes. Authoring uses
the core's [five-step checklist](skills/eval-author/SKILL.md#show-the-path-ahead),
which groups the ten internal stages while preserving their
[stage check-ins](skills/eval-author/references/milestone-checkins.md). A starting
point already settled by the user or inventory is reused without another scan.
Discovery's run instructions are labeled as documented or source-derived until
readiness is validated. General evaluation help does not automatically continue
from discovery into an audit.

For a local skill tree, invoke the entrypoint and load supporting instructions as
each stage needs them:

```text
Use Eval Author at <skill-tree>/eval-author/SKILL.md to help me get my evals working
in this repository. Show me the plan first. Load sub-flows and references from
that same local skill tree as needed for the current stage.
```

## Where findings go

First-eval saves its plan in `.eval-author/first-eval.md`, drafts under
`.eval-author/task-drafts/`, and a run config in `.eval-author/first-eval.yaml`.

`eval-author-discover` leaves a report at `.eval-author/discovery.md`. Inventory
reports explain what evals exist, their purposes, and documented run instructions.
Readiness reports also carry provider JSON in an evidence section so a later model
can read the verdict without Harbor. A teammate can reuse either report's findings
and their stated limits.

`eval-author-inspect-trace` leaves one report per trace under
`.eval-author/traces/`. The front matter carries Intake source metadata and the
exact read commands. Findings use `behavior`, `issue`, `recovery`, and
`uncertainty` categories.

`eval-author-trace-environment` creates one owner-private, gitignored workspace
per task under `.eval-author/trace-environments/`. Each finalized workspace has
a `candidate` or `no_candidate` summary and keeps restricted source evidence
separate from its text-only scrubbed ATIF copy. It also accepts
[Gym Responses traces](skills/eval-author-trace-environment/references/gym.md)
through a bounded offline adapter. For Harbor-backed Gym rollouts, retain and
prefer the original ATIF rather than round-tripping through Gym's projection.
No Gym runtime, model invocation, or image download is needed for normalization.

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
