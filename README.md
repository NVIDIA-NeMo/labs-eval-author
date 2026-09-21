<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# NeMo Eval Author

NeMo Eval Author helps your coding agent create useful evaluations and find
gaps in behavior coverage, grounded in your agent's intended behavior and
execution traces.

Bring your agent's repository and use the skills with your own coding agent.
Build a first Harbor evaluation suite, check an existing suite, or audit its
coverage. Core workflows do not require a NeMo Platform service or account.

For example, an audit might report:

> **Recovery from rejected tool arguments lacks trace evidence.** The agent is
> expected to correct an invalid argument, but the measured traces do not cover
> that behavior. Review the existing cases to decide whether to add a recovery
> test or collect more evidence.

This project is in alpha. Workflows and interfaces may change.

## Start here

Use a coding agent with local file and shell access, and install
[Git](https://git-scm.com/downloads/) to obtain the skills. Then choose a guide:

| Your starting point | Guide |
| --- | --- |
| Unsure what evaluations exist in your repository | [Load the skills and find your evaluations](docs/getting-started.md) |
| No evaluations yet | [Build your first evaluations](docs/first-evals.md) |
| An existing Harbor suite | [Check readiness](docs/existing-evals.md#check-readiness) |
| Existing evaluations and traces | [Audit coverage](docs/existing-evals.md#audit-coverage) |
| Coverage gaps identified by an audit | [Plan new or improved evaluations](docs/existing-evals.md#propose-new-evaluations) |
| A NeMo Platform Intake trace | [Inspect a trace](docs/traces.md#inspect-an-intake-trace) |
| Local MLflow, Gym, or ATIF traces | [Work from recorded traces](docs/traces.md) |
| Reports or evaluation results to interpret | [Read your results](docs/results.md) |
| A task derived from traces that you want to share | [Review the task for publication](docs/traces.md#sharing-generated-tasks) |

Harbor, Docker, and trace-platform access are needed only for the workflows that
use them. Each guide links to the relevant [requirements](docs/getting-started.md#requirements).

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
