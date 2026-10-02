<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# NeMo Eval Author

![Status: Research Preview](https://img.shields.io/badge/Status-Research%20Preview-orange)

Turning your agent's intended behavior into representative evaluation cases is
hard. Each case needs checks that distinguish success from failure, and passing
cases can still leave important behavior untested.

NeMo Eval Author explores how a coding assistant can help you create evaluations
and investigate gaps in behavior coverage. It provides skills that work with
your agent's repository, its intended behavior, and available execution traces
(records of the steps your agent took). You can start without traces: build a
first evaluation suite, inspect existing evaluations, or plan cases with your
coding assistant.

> [!WARNING]
> **Research preview**
>
> This is early research for experimentation and collaboration with developers.
> Workflows and interfaces may change. Review generated cases, graders (the
> checks that score an agent's work), and coverage findings before relying on
> their results.

For example, an audit might report:

> **Recovery from rejected tool arguments lacks trace evidence.** The agent is
> expected to correct an invalid argument, but the measured traces do not cover
> that behavior. This does not establish that a recovery test is missing. Review
> the existing cases to decide whether to add a test or collect more evidence.

## Questions we are exploring

- How can intended behavior become representative cases with meaningful success
  checks?
- How can generated tasks challenge an agent in realistic ways and distinguish
  stronger behavior from weaker behavior?
- How can evaluations and traces reveal gaps without overstating coverage?
- How can developers decide which evaluations to add or improve next?

## Help shape the research

Try Eval Author with your agent and tell us where the approach needs work:

- Where do proposed cases miss behavior that matters to you?
- Where do graders judge outcomes incorrectly?
- Which coverage findings leave you unsure what to test or investigate next?

Generated tasks can be too easy. Where do your agents pass without exercising
the behavior you wanted to test? An anonymized example of the task, how the agent
passed, and what would make it meaningfully challenging would help us improve
task generation.

If an NVIDIA contact shared this preview with you, send your feedback through
that contact and ask them to route it to the Eval Author research team.
Otherwise, use the [NVIDIA Developer contact form](https://developer.nvidia.com/contact)
with **Eval Author research preview feedback** in the subject. Include your
workflow, what you expected, what happened, and a small anonymized example.
Please avoid sending raw traces, prompts, credentials, or user data in an initial
message. For code contributions, see the [current contribution policy](CONTRIBUTING.md).

## Start here

You need a coding assistant that can read and write project files and run shell
commands, [Node.js 22.20+](https://nodejs.org/en/download) (including npm and
`npx`), and [Git](https://git-scm.com/downloads). In a terminal, change to the
root of the repository containing **your agent**, then install the skills:

```bash
cd /path/to/your-agent-repository
npx skills add NVIDIA-NeMo/labs-eval-author --skill '*' --agent claude-code --yes
```

Replace `claude-code` with [your assistant's identifier](docs/getting-started.md#install-eval-author-with-npx).
See the setup guide for [manual installation without Node.js](docs/getting-started.md#manual-installation-without-nodejs)
and [verification](docs/getting-started.md#verify-your-assistant-can-use-eval-author).

Creating, validating, and running evaluation tasks requires an evaluation
runtime: [NeMo Gym](https://docs.nvidia.com/nemo/gym/latest/) or
[Harbor](https://docs.harborframework.com/). Eval Author follows your choice,
otherwise keeps the runtime your existing suite uses, and defaults to Harbor.
Installing the skills does not install Gym, Harbor, or Python dependencies; see
the [workflow requirements](docs/getting-started.md#requirements). Repository
inventory and case planning can start without either runtime.

Open your agent's repository in a new session of the selected coding assistant
and ask:

```text
Use eval-author to help me with the evals for my agent.
```

With no starting point supplied, Eval Author inventories existing evaluations
and saves `.eval-author/discovery.md` with what it found and documented run
commands. For a specific starting point, choose a guide and include the relevant
file paths, trace IDs, or workspace names in your request:

| Your starting point | Guide |
| --- | --- |
| Find evaluations in an unfamiliar repository | [Discover existing evaluations](docs/getting-started.md#find-existing-evaluations) |
| Build a suite when you have no evaluations | [Build your first evaluations](docs/first-evals.md) |
| Check whether Gym or Harbor evaluations are ready to run | [Check readiness](docs/existing-evals.md#check-readiness) |
| Compare intended behavior with evaluation and trace evidence | [Audit coverage](docs/existing-evals.md#audit-coverage) |
| Create a Gym task from an audit gap | [Author and prove a Gym task](skills/eval-author-task-create/references/gym-tasks.md) |
| Decide what to add after an audit | [Plan new or improved evaluations](docs/existing-evals.md#propose-new-evaluations) |
| Understand a NeMo Helix Intake trace | [Inspect a trace](docs/traces.md#inspect-an-intake-trace) |
| Turn a local trace into an evaluation task | **Experimental** · [Build a task from a trace](docs/traces.md#build-an-evaluation-task) |
| Understand an evaluation report | [Read your results](docs/results.md) |
| Review a task derived from a trace before sharing it | **Experimental** · [Review the task for publication](docs/traces.md#sharing-generated-tasks) |

### Experimental trace-environment loop

The [trace-environment workflow](docs/traces.md#build-an-evaluation-task) turns
trace evidence into a private candidate task, validates it with Harbor's `nop`
and `oracle` or Gym's native validation and repeated controls, and uses the findings
to refine the task. Gym output uses a private native report; automated publication
and readiness reporting remain Harbor-specific. It can start directly
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
