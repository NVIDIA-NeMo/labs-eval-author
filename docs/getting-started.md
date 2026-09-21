<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Get started with Eval Author

Load Eval Author's skills into your coding agent, then choose the work you need.
A skill is a set of instructions and supporting scripts that your agent reads
to carry out a task.

## Load the skills

Use a coding agent that can read local instructions, read and write project
files, and run shell commands. The following workflow loads the skills by file
path and does not depend on an assistant-specific skill installer.

1. Clone this repository and print the absolute path to the entry skill:

   ```bash
   git clone https://github.com/NVIDIA-NeMo/labs-eval-author.git
   cd labs-eval-author
   printf '%s/skills/eval-author/SKILL.md\n' "$PWD"
   ```

2. Open the repository you want to evaluate in your coding agent. Give the agent
   access to both that repository and this skill checkout. Keep this checkout
   intact: the entry skill loads sibling skills, scripts, schemas, templates,
   and references, and some workflows also link to the `docs/` directory.

3. Start your request with this text, replacing `<entry-skill-path>` with the
   path printed above. Add your goal from one of the [workflow guides](../README.md#start-here):

   ```text
   Use Eval Author at <entry-skill-path> in this repository.
   Load supporting skills and references from the same skill tree as needed.
   ```

Loading the skills requires no Python package installation. You need your coding
agent's usual setup; later steps have [workflow-specific requirements](#requirements).

## Find existing evaluations

If you are unsure what evaluations exist, add this request to the text above:

```text
Find the existing evaluations, explain what they test, and show their
documented run commands. Save the findings to .eval-author/discovery.md.
```

This request inventories the repository's documentation and source. It does not
require Harbor, Docker, or model credentials for evaluation runs. If you already
know your starting point, go directly to the relevant workflow guide.

### What to expect

The agent produces `.eval-author/discovery.md` in the repository being evaluated.
It describes the evaluations it found, their purpose, and available run
instructions. For example, an inventory might identify a smoke-test suite,
point to its configuration, and quote its documented command. Those instructions
remain unverified until a readiness check. If no evaluations are found, the
report records that result and the scope inspected.

To continue, [check an existing suite](existing-evals.md#check-readiness),
[audit its coverage](existing-evals.md#audit-coverage), or
[build your first evaluations](first-evals.md).

## Requirements

Requirements depend on the operation. Use the
[Harbor setup guide](../skills/eval-author-discover/references/harbor-setup.md) when
you need to create, validate, or run Harbor tasks.

| Operation | Requirements |
| --- | --- |
| Read repository docs, establish Ethos, and plan cases | Your coding agent and repository access. Harbor is not required for this work. |
| Run the discovery helper | Python 3.11+. Verified readiness requires Harbor importable by that interpreter; Docker is needed for the Docker backend check. |
| Create, validate, and run Harbor tasks | Harbor and its supported Python environment. Execution also needs the selected backend and any application access, agent integration, and provider credentials required by the task. |
| Generate or validate an audit specification; aggregate measured coverage | Python 3.11+, PyYAML, and jsonschema. These operations read local evidence and do not call NeMo services. |
| Measure coverage from ATIF traces | Python 3.12+ and the [audit dependencies](../skills/eval-author-audit/requirements.txt), including Harbor. Measurement does not start evaluation jobs. |
| Convert exported MLflow traces | Python 3.11+ and the standard library. Live MLflow queries additionally need an existing MLflow environment and access to the store. |
| Convert Gym traces with the trace-environment adapter (**experimental**) | Python 3.11+ and the standard library for conversion. |
| Prepare and validate a trace-derived environment (**experimental**) | Python 3.11+, jsonschema 4.23+, and referencing 0.28.4+ for preparation; Harbor and Docker for execution checks. |
| Inspect NeMo Intake traces | A working `nemo` CLI, an explicit workspace, and read access to a configured local or remote NeMo Platform instance. |

Use the Python environment supported by your installed Harbor version for
Harbor-backed operations. This repository's development checks use Python 3.12
and 3.13 with Harbor 0.20.0; see [development setup](../DEVELOPMENT.md).

The experimental trace-to-environment workflow uses Harbor's `nop` agent (a no-op
baseline) and `oracle` agent (the task's reference solution). These checks do not require a model
provider. Running your actual agent uses its configured provider and dependencies.

If you need help, [open an issue](https://github.com/NVIDIA-NeMo/labs-eval-author/issues)
with the workflow, relevant versions, and a minimal reproduction using synthetic
data. Keep credentials and private traces out of public reports.
