<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# NeMo Eval Author

NeMo Eval Author helps your coding agent create useful evaluations and find
gaps in behavior coverage, grounded in your agent's intended behavior and
execution traces.

Bring your agent's repository and use the skills with your own coding agent.
Build a first evaluation suite, check an existing suite, or audit its coverage.

First evaluations and readiness checks use [Harbor](https://docs.harborframework.com/).
Task creation from an existing audit gap also supports [NeMo Gym](https://docs.nvidia.com/nemo/gym/latest/)
through the [Gym task-authoring guide](skills/eval-author-task-create/references/gym-tasks.md).
Gym proposals include a version-locking and rerun plan for comparable evaluations.

For example, an audit might report:

> **Recovery from rejected tool arguments lacks trace evidence.** The agent is
> expected to correct an invalid argument, but the measured traces do not cover
> that behavior. Review the existing cases to decide whether to add a recovery
> test or collect more evidence.

This project is in alpha. Workflows and interfaces may change.

## Prerequisites

Harbor is required for first-evaluation authoring and Harbor task execution. Use a Python
environment supported by your Harbor installation; see the
[setup guide](skills/eval-author-discover/references/harbor-setup.md) for installation
and verification. Repository inventory and case planning can start without Harbor.

First-evaluation design and coverage audits require a local **Ethos** describing
your agent's purpose, boundaries, and success criteria.

The discovery helper requires Python 3.11+. Audit generation, validation, and
aggregation require Python 3.11+, PyYAML, and jsonschema. Measuring coverage from
ATIF traces requires Python 3.12+ and the
[audit dependencies](skills/eval-author-audit/requirements.txt), including Harbor.

Task execution may need Docker, application access, and model credentials,
depending on the task and agent. See the
[full requirements](docs/getting-started.md#requirements)
for each workflow, including local trace conversion and experimental
environment preparation.

## Start here

### Install with npx

You need a coding assistant that can read and write project files and run shell
commands, [Node.js 22.20+](https://nodejs.org/en/download) (including npm and
`npx`), and [Git](https://git-scm.com/downloads). In a terminal, change to the
root of the repository containing **your agent**, then install for your assistant:

```bash
cd /path/to/your-agent-repository
npx skills add NVIDIA-NeMo/labs-eval-author --skill '*' --agent claude-code --yes
```

Replace `claude-code` with your assistant's identifier:

| Coding assistant | `--agent` value |
| --- | --- |
| Claude Code | `claude-code` |
| Codex | `codex` |
| Cursor | `cursor` |
| Pi | `pi` |

See the [Skills CLI documentation](https://github.com/vercel-labs/skills#supported-agents)
for other assistants.

Installation adds ten skill directories with their instructions, scripts,
schemas, templates, and references. Harbor and Python dependencies are separate
[workflow requirements](docs/getting-started.md#requirements).

Verify the installation from the same directory, using the same assistant value:

```bash
npx skills list --agent claude-code
```

For a global installation, add `--global` to this check too. Look for `eval-author`
and its supporting skills. The CLI may show other assistants that share a skills
directory; it has not installed those assistants. See the
[installation guide](docs/getting-started.md#install-eval-author-with-npx)
for scope, file locations, and troubleshooting.

### Install without npx

With Git and a POSIX shell (macOS, Linux, or WSL), you can clone this repository
and copy its complete active skill directories into your assistant's project
skills folder. This path requires no Node.js or npm. Follow the
[manual installation steps](docs/getting-started.md#manual-installation-without-nodejs)
for the destination, copy commands, and verification. You can also
[load the checkout by file path](docs/getting-started.md#manual-checkout).

### Start your first interaction

Open your agent's repository in a new session of the selected coding assistant
and ask:

```text
Use eval-author to help me with the evals for my agent.
```

With no starting point supplied, Eval Author inventories existing evaluations
and saves `.eval-author/discovery.md` with what it found and documented run
commands. Inventory can start without Harbor. If the assistant cannot find
`eval-author`, follow the [availability check](docs/getting-started.md#verify-your-assistant-can-use-eval-author).
If you know more about your scenario, try one of these:

| Say to your coding assistant | Guide |
| --- | --- |
| "Find the evals in this repository and explain how to run them." | [Discover existing evaluations](docs/getting-started.md#find-existing-evaluations) |
| "I don't have evals yet. Help me build my first ones." | [Build your first evaluations](docs/first-evals.md) |
| "Check whether my Harbor evals are ready to run." | [Check readiness](docs/existing-evals.md#check-readiness) |
| "Audit my evals against my agent's intended behavior using these traces." | [Audit coverage](docs/existing-evals.md#audit-coverage) |
| "Create a Gym evaluation from this audit gap." | [Author and prove a Gym task](skills/eval-author-task-create/references/gym-tasks.md) |
| "Use this audit report to propose the next evals to add." | [Plan new or improved evaluations](docs/existing-evals.md#propose-new-evaluations) |
| "Explain Intake trace TRACE_ID in workspace WORKSPACE." | [Inspect a trace](docs/traces.md#inspect-an-intake-trace) |
| "Turn this local trace into a Harbor eval task." | **Experimental** · [Build a task from a trace](docs/traces.md#build-an-evaluation-task) |
| "Explain this eval report and what I should check next." | [Read your results](docs/results.md) |
| "Review this task derived from a trace before I share it." | **Experimental** · [Review the task for publication](docs/traces.md#sharing-generated-tasks) |

Include the relevant file paths, trace IDs, or workspace names in your request.

### Experimental trace-environment loop

The [trace-environment workflow](docs/traces.md#build-an-evaluation-task) turns
trace evidence into a private candidate task, validates it with Harbor's `nop`
and `oracle`, and uses the findings to refine the task. It can start directly
from a trace or be paired with [dataset proposals](docs/existing-evals.md#propose-new-evaluations):
propose a useful scenario, construct it from supporting trace evidence, then
validate and refine it.

```text
Use this audit report to propose an eval, then use eval-author-trace-environment
to build a private candidate from the supporting trace. Validate it when the
required runtime is available, and report any remaining blockers.
```

A proposal does not establish that a task can be built or that its environment
works. The loop may produce no candidate or an unproven candidate; successful
validation still does not measure your agent's performance. Proposal-only
requests stop at recommendations. See the [trace guide](docs/traces.md#build-an-evaluation-task)
for evidence requirements and validation, and the
[publication review](docs/traces.md#sharing-generated-tasks) before sharing a task.

[Development](DEVELOPMENT.md) · [Skill reference](DEVELOPMENT.md#skill-reference) · [Support](https://github.com/NVIDIA-NeMo/labs-eval-author/issues)

## License

Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.

Eval Author is licensed under the [Apache License, Version 2.0](LICENSE).
See [NOTICE](NOTICE) for attributions and the external-materials disclaimer,
[THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) for dependency license
disclosures, and [third_party/licenses.jsonl](third_party/licenses.jsonl) for
the machine-readable inventory.

The bundled JSON examples and synthetic test fixtures are NVIDIA-authored and
covered by the project license.

This project is currently not accepting contributions. Internal maintenance is
limited to the NVIDIA ASE team. See [CONTRIBUTING.md](CONTRIBUTING.md) for the
current policy, sign-off, and review requirements.
