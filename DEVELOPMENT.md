<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Development

## Environment and skill layout

Development uses Python 3.12 or 3.13 and uv. Run `uv sync --locked` to prepare
the environment, including the test runner, validators, MCP, and Harbor 0.20.0.
No NeMo Platform checkout is required. See [CONTRIBUTING.md](CONTRIBUTING.md)
for the CI tool versions and contribution requirements.

This repository is not installed as a Python package. Users
[install the skills with `npx`, copy them manually, or load a checkout by file path](docs/getting-started.md#load-the-skills).
Keep runtime instructions and resources inside the skill directories, and
preserve relative paths between sibling skills. A skill installation does not
include repository-level documentation or tests. The bundled scripts do not
expose a published Python package API.

Adding a runtime dependency to a bundled script changes the requirements for
users who copied the skill. Contract tests inspect script imports and reject
dependencies outside the standard library, sibling modules, and explicitly
allowed third-party dependencies. Update the relevant skill's compatibility
instructions and the [workflow requirements](docs/getting-started.md#requirements)
when those requirements change.

The audit validator is
[`skills/eval-author-audit/scripts/audit_spec/validate.py`](skills/eval-author-audit/scripts/audit_spec/validate.py).
See the [audit script guide](skills/eval-author-audit/scripts/audit_spec/README.md)
for measurement assumptions, evidence sidecars, and aggregation. Command examples
are in the [audit skill](skills/eval-author-audit/SKILL.md).
The experimental trace-environment skill documents its
[artifact contract](skills/eval-author-trace-environment/SKILL.md#artifact-contract).
For standalone Gym trace conversion, see
[`gym-to-atif`](skills/gym-to-atif/SKILL.md).

## Skill reference

Start with `eval-author`; it selects the appropriate workflow and loads supporting
instructions. The individual skill files document each workflow in detail.

| Skill | Purpose |
| --- | --- |
| [`eval-author`](skills/eval-author/SKILL.md) | Entry point and shared workflow guidance. |
| [`eval-author-first-eval`](skills/eval-author-first-eval/SKILL.md) | Plan, build, and validate a small starter evaluation suite. |
| [`eval-author-discover`](skills/eval-author-discover/SKILL.md) | Inventory evaluations and check Harbor readiness. |
| [`eval-author-audit`](skills/eval-author-audit/SKILL.md) | Define intended behavior and measure coverage against trace evidence. |
| [`eval-author-task-create`](skills/eval-author-task-create/SKILL.md) | Propose improvements from an audit and create a supported task when requested. |
| [`eval-author-inspect-trace`](skills/eval-author-inspect-trace/SKILL.md) | Explain an Intake trace selected through the entry skill. |
| [`eval-author-trace-environment`](skills/eval-author-trace-environment/SKILL.md) | **Experimental.** Derive and validate a private Harbor environment from trace evidence. |
| [`mlflow-to-atif`](skills/mlflow-to-atif/SKILL.md) | Convert MLflow traces to ATIF. |
| [`gym-to-atif`](skills/gym-to-atif/SKILL.md) | Convert one Gym Responses record or retain original Harbor ATIF from a Gym run. |

## Validation

Run `uv sync --locked` and `make hooks` to install the DCO commit-message hook.
See [CONTRIBUTING.md](CONTRIBUTING.md) for sign-off and PR-title conventions.
Before committing, check a prepared message with
`make commit-check COMMIT_MSG=/path/to/prepared-commit-message`; the hook also
runs on `git commit`. Plain `make commit-check` validates the current `HEAD`
commit, so it also works after cloning or pulling a merged change.

When adding NVIDIA-authored files or changing dependencies, update the tracked
licensing artifacts first:

```bash
make update-copyright-headers
make update-licenses
```

For dependency changes, run `uv add <package>` and `make update-licenses`, review
the generated diff, and commit it. Generation requires `osv-scanner` 2.3.3 on `PATH`
and automatically collects license and attribution texts for locked runtime
dependencies and all extras into `third_party/NOTICES.txt`, with indexes in
`THIRD_PARTY_LICENSES.md` and `third_party/licenses.jsonl`.

Only exceptions require manual work: if a distribution omits its license, add a
version-specific, checksum-pinned upstream document in `third_party/license_exceptions.yaml`.
Unknown license terms require a shared text under `third_party/license_texts/` and,
where necessary, a reviewed compatibility entry in `third_party/license_overrides.yaml`.
The standard texts were sourced from SPDX license-list-data commit
`16f3aa6c3bdd62e50f8b1cf618f32d2a510250ee`; original package notices are retained separately.

`make check-licenses` verifies the generated disclosures. Scanner intermediates and
download caches live in ignored `tmp/`; a cold cache requires network access.
These notices cover this source distribution;
shipping containers or bundled native environments requires collecting notices from
those actual artifacts too, since platform wheels can bundle additional libraries.

Run the same read-only checks used by CI:

```bash
make check-copyright-headers
make check-licenses
uv run --locked ruff check .
uv run --locked ty check --python-platform linux --python-version 3.12
uv run --locked ty check --python-platform linux --python-version 3.13
uv run --locked ruff format --check .
uv run --locked pytest
```

The default tests use synthetic local evidence and mocked providers. Tests that
need a running environment backend skip when one is unavailable. The optional
Ethos parser compatibility test skips without the NeMo Agents plugin. Live
model execution is opt-in outside configured CI workflows; see
[trace fixture checks](docs/trace-derived-fixtures.md#regression-checks) and
[skill evaluation CI](docs/skill-evaluation-ci.md).
