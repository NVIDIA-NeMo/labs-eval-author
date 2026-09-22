<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Dependency scope and licenses

Eval Author distributes Markdown skills and NVIDIA-authored Python scripts.
Copying the skills does not install Python packages, Harbor, Docker, or the NeMo
CLI. Dependencies are used through their APIs or command-line interfaces; their
implementations are not bundled in the skill directories.

This reference lists direct workflow, development, and separately installed CI
software. License links identify each upstream project's terms; packages can
include additional third-party notices. It is not a complete license inventory
of every development environment, container, or downloaded tool.

## Why the dependency lists differ

| Record | What it covers |
| --- | --- |
| [Generated license inventory](../THIRD_PARTY_LICENSES.md) and [full notices](../third_party/NOTICES.txt) | Root `pyproject.toml` runtime dependencies (`jsonschema` and `referencing`), root optional extras if declared, and their transitive/platform dependencies. Generation uses `uv export --frozen --no-dev --all-extras`. |
| Workflow dependencies below | Software used by individual skills, including packages supplied by the user's environment or installed through documented setup commands. Some are only in the root development group or absent from the root declarations. |
| Development and CI tools below | Direct tools used to test and maintain this repository. These are excluded from the generated root runtime inventory. |
| [uv.lock](../uv.lock) | Resolved versions, dependency edges, source revisions, and download artifacts for the root project and development group. It is not a license report or a list of packages shipped with the skills. Multiple wheel URLs describe platform variants of the same package. Separately installed CI tools have their own dependency environments. |

The generated inventory currently has six packages: `attrs`, `jsonschema`,
`jsonschema-specifications`, `referencing`, `rpds-py`, and `typing-extensions`.
It therefore does not match a list of the direct dependencies of all workflows.
Do not use it to claim license coverage for the entire development lockfile.
The lockfile is retained to make development and tests reproducible; deleting
it would not remove dependencies or change what the scripts use.

## Workflow dependencies

Constraints below come from [pyproject.toml](../pyproject.toml), the
[audit requirements](../skills/eval-author-audit/requirements.txt), and the
linked skill instructions.

| Dependency | Usage and version constraint | Upstream license |
| --- | --- | --- |
| [Harbor](https://github.com/harbor-framework/harbor) | Task validation and execution; audit requires `>=0.16.1`, development pins `==0.20.0`; discovery probes the existing installation. | [Apache-2.0](https://github.com/harbor-framework/harbor/blob/main/LICENSE) |
| [jsonschema](https://github.com/python-jsonschema/jsonschema) | Audit and trace schema validation; root `>=4.23`, audit requirements `>=4.0`. | [MIT](https://github.com/python-jsonschema/jsonschema/blob/main/COPYING) |
| [referencing](https://github.com/python-jsonschema/referencing) | Trace schema reference handling; root `>=0.28.4`. | [MIT](https://github.com/python-jsonschema/referencing/blob/main/COPYING) |
| [PyYAML](https://github.com/yaml/pyyaml) | Audit YAML and Harbor inventory parsing; audit and development `>=6.0`. | [MIT](https://github.com/yaml/pyyaml/blob/main/LICENSE) |
| [Pydantic](https://github.com/pydantic/pydantic) | Harbor-backed validation; development `>=2`, also a dependency of Harbor and Trace Intel. | [MIT](https://github.com/pydantic/pydantic/blob/main/LICENSE) |
| [MLflow](https://github.com/mlflow/mlflow) | Optional live ATIF conversion uses an existing MLflow installation without an explicit converter version constraint. The separate Trace Intel loader requires the `mlflow` extra, which declares `mlflow-skinny>=3.6,<4`. | [Apache-2.0](https://github.com/mlflow/mlflow/blob/master/LICENSE.txt) |
| [Trace Intel trace-ingest](https://github.com/NVIDIA-NeMo/labs-trace-intel/tree/692d1bf57b6a9372f628b7c2004852aec7a9a83e/packages/trace-ingest) | Shared Gym and MLflow loaders; pinned revision `692d1bf57b6a9372f628b7c2004852aec7a9a83e`. Development includes `trace-ingest[mlflow]`; standalone loaders require the package in their selected environment. | [Apache-2.0](https://github.com/NVIDIA-NeMo/labs-trace-intel/blob/692d1bf57b6a9372f628b7c2004852aec7a9a83e/LICENSE) |

### What can install dependencies

The current workflows are not universally "use installed packages only."
Audit examples use `uv run --with` or `--with-requirements`, which can resolve and
install packages when invoked. [Harbor setup](../skills/eval-author-discover/references/harbor-setup.md)
first checks the existing installation and provides user-run installation
instructions; agent-driven installation requires explicit authorization.
The [Gym](../skills/gym-to-atif/references/trace-intel-ingest.md) and
[MLflow](../skills/mlflow-to-atif/references/trace-intel-ingest.md) loader references
provide pinned installation commands for environments authorized for setup.
The loader scripts themselves do not install dependencies.

### Docker and NeMo CLI

Docker is a prerequisite when the selected Harbor task uses a Docker backend,
including the documented container-based NOP and Oracle checks. It is not
required just to read skills, inventory files, or perform offline conversion.
The user must provide a working backend for those execution paths; copying the
skills does not install Docker. Other Harbor backends have their own requirements.
Docker Engine, Compose, and Docker Desktop are distinct products; the user's
chosen installation determines its terms. See [Docker Engine](https://github.com/moby/moby/blob/master/LICENSE),
[Compose](https://github.com/docker/compose/blob/main/LICENSE), and
[Docker Desktop terms](https://www.docker.com/legal/docker-subscription-service-agreement/).
Separately, the live evaluation CI installs Docker Compose on its runner.

The NeMo CLI is required for the Intake workflow that queries NeMo Platform.
It must already be configured with the required workspace and access. It is not
required for offline trace conversion or local audit processing. The skill uses
the existing CLI and does not install it; see [trace inspection](../skills/eval-author-inspect-trace/SKILL.md).
Its source is [nemo-platform](https://github.com/NVIDIA-NeMo/nemo-platform), under
[Apache-2.0](https://github.com/NVIDIA-NeMo/nemo-platform/blob/main/LICENSE).

## Development and CI tools

These tools support repository maintenance and validation; they are not required
simply to load the skills.

| Tool | Declaration or pin | Upstream license |
| --- | --- | --- |
| MCP Python SDK | Development `>=1.29,<2`; integration tests | [MIT](https://github.com/modelcontextprotocol/python-sdk/blob/main/LICENSE) |
| pytest | Development `>=9.0.3` | [MIT](https://github.com/pytest-dev/pytest/blob/main/LICENSE) |
| Ruff | Development `>=0.14` | [MIT, with additional upstream notices](https://github.com/astral-sh/ruff/blob/main/LICENSE) |
| uv | CI `0.12.3`; dependency management | [Apache-2.0 OR MIT](https://github.com/astral-sh/uv#license) |
| OSV-Scanner | `2.3.3`; license inventory generation | [Apache-2.0](https://github.com/google/osv-scanner/blob/v2.3.3/LICENSE) |
| pre-commit | Development `>=4,<5`; local DCO hook | [MIT](https://github.com/pre-commit/pre-commit/blob/main/LICENSE) |
| ty | Development `>=0.0.80`; type checking | [MIT](https://github.com/astral-sh/ty/blob/main/LICENSE) |
| SkillEvaluator | CI revision `7e189c6bdada8910dfa1684f25feedca87f2db85`, security or tier2/tier3 extras | [Apache-2.0](https://github.com/NVIDIA/SkillEvaluator/blob/7e189c6bdada8910dfa1684f25feedca87f2db85/LICENSE) |
| SkillSpector | CI revision `69dcdfb74487d361ba4c811d088cfdea2ff3a9dc` | [Apache-2.0](https://github.com/NVIDIA/SkillSpector/blob/69dcdfb74487d361ba4c811d088cfdea2ff3a9dc/LICENSE) |
| Semgrep | CI `1.177.0`; standalone scanner | [LGPL-2.1-or-later](https://github.com/semgrep/semgrep/blob/v1.177.0/cli/pyproject.toml), [license text](https://github.com/semgrep/semgrep/blob/v1.177.0/LICENSE) |
| Gitleaks | CI `8.30.1`; standalone scanner | [MIT](https://github.com/gitleaks/gitleaks/blob/v8.30.1/LICENSE) |
| Docker Compose | Live CI `5.5.1` | [Apache-2.0](https://github.com/docker/compose/blob/v5.5.1/LICENSE) |

The CI tools are installed separately on runners; they are not bundled into
Eval Author's skills. CI pins and commands are in [CI](../.github/workflows/ci.yml)
and [live evaluations](../.github/workflows/skill-evaluation-live.yml).
The table describes the named tools' licenses, not blanket approval of their
transitive dependencies or downloaded rule sets.

The optional `npx skills` installation route uses the
[Skills CLI (MIT)](https://github.com/vercel-labs/skills/blob/main/LICENSE),
[Node.js (MIT, with bundled dependency notices)](https://github.com/nodejs/node/blob/main/LICENSE), and
[npm/npx (Artistic-2.0, with bundled dependency notices)](https://github.com/npm/cli/blob/latest/LICENSE).
The [manual installation route](getting-started.md#manual-installation-without-nodejs)
does not need these tools.

## Source notices and contribution terms

- NVIDIA source header examples: [entry skill](../skills/eval-author/SKILL.md) and [discovery script](../skills/eval-author-discover/scripts/discover.py).
- Project license and notices: [LICENSE](../LICENSE) and [NOTICE](../NOTICE).
- Collected dependency texts: [third_party/NOTICES.txt](../third_party/NOTICES.txt), indexed by [THIRD_PARTY_LICENSES.md](../THIRD_PARTY_LICENSES.md).
- Contribution restrictions, sign-off, and the full DCO: [CONTRIBUTING.md](../CONTRIBUTING.md#sign-off-and-contribution-license).
