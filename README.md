<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# NeMo Eval Author

NeMo Eval Author helps your coding agent create useful evaluations and find
gaps in behavior coverage, grounded in your agent's intended behavior and
execution traces.

Bring your agent's repository and use the skills with your own coding agent.
Build a first evaluation suite, check an existing suite, or audit its coverage.

Evaluations run with [Harbor](https://docs.harborframework.com/), the framework
Eval Author uses to validate tasks, execute agents, and grade results.

For example, an audit might report:

> **Recovery from rejected tool arguments lacks trace evidence.** The agent is
> expected to correct an invalid argument, but the measured traces do not cover
> that behavior. Review the existing cases to decide whether to add a recovery
> test or collect more evidence.

This project is in alpha. Workflows and interfaces may change.

## Prerequisites

Harbor is required to create, validate, and run evaluation tasks. Use a Python
environment supported by your Harbor installation; see the
[setup guide](skills/eval-author-discover/references/harbor-setup.md) for installation
and verification. Repository inventory and case planning can start without Harbor.

First-evaluation design and coverage audits require a local **Ethos** describing
your agent's purpose, boundaries, and success criteria. Eval Author can help you
reuse or create one with the [Local Ethos procedure](skills/eval-author/references/local-ethos.md),
without a NeMo service, account, or upload.

The discovery helper requires Python 3.11+. Audit generation, validation, and
aggregation require Python 3.11+, PyYAML, and jsonschema. Measuring coverage from
ATIF traces requires Python 3.12+ and the
[audit dependencies](skills/eval-author-audit/requirements.txt), including Harbor.

Task execution may need Docker, application access, and model credentials,
depending on the task and agent. Intake trace inspection requires a working
`nemo` CLI, an explicit workspace, and read access to a configured local or remote
NeMo Platform instance. See the [full requirements](docs/getting-started.md#requirements)
for each workflow, including local trace conversion and experimental
environment preparation.

## Start here

With the [Eval Author skills loaded](docs/getting-started.md#load-the-skills)
and your agent's repository open, ask your coding assistant:

```text
Help me with the evals for my agent.
```

Eval Author helps you find the right starting point. If you know more about your
scenario, try one of these:

| Say to your coding assistant | Guide |
| --- | --- |
| "Find the evals in this repository and explain how to run them." | [Discover existing evaluations](docs/getting-started.md#find-existing-evaluations) |
| "I don't have evals yet. Help me build my first ones." | [Build your first evaluations](docs/first-evals.md) |
| "Check whether my Harbor evals are ready to run." | [Check readiness](docs/existing-evals.md#check-readiness) |
| "Audit my evals against my agent's intended behavior using these traces." | [Audit coverage](docs/existing-evals.md#audit-coverage) |
| "Use this audit report to propose the next evals to add." | [Plan new or improved evaluations](docs/existing-evals.md#propose-new-evaluations) |
| "Explain Intake trace TRACE_ID in workspace WORKSPACE." | [Inspect a trace](docs/traces.md#inspect-an-intake-trace) |
| "Turn this local trace into a Harbor eval task." | **Experimental** · [Build a task from a trace](docs/traces.md#build-an-evaluation-task) |
| "Explain this eval report and what I should check next." | [Read your results](docs/results.md) |
| "Review this task derived from a trace before I share it." | **Experimental** · [Review the task for publication](docs/traces.md#sharing-generated-tasks) |

Include the relevant file paths, trace IDs, or workspace names in your request.

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

Contributions are currently limited to the NVIDIA ASE team. See
[CONTRIBUTING.md](CONTRIBUTING.md) for the current policy and review requirements.
