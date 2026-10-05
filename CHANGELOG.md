<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Changelog

Notable changes to NeMo Eval Author are recorded here. Eval Author is a research
preview: workflows, skills, and saved artifacts may change between releases.

## 0.1.0 (unreleased)

The first research-preview release of NeMo Eval Author: skills that help your
coding assistant build evaluations for your agent, check existing evaluation
suites, and investigate gaps in behavior coverage. They work from your agent's
repository, its intended behavior, and, when available, its execution traces.
Generated tasks run on [NeMo Gym](https://docs.nvidia.com/nemo/gym/latest/) or
[Harbor](https://docs.harborframework.com/).

Review generated cases, graders, and coverage findings before relying on their
results.

### Highlights

- **Build your first evaluations.** Starting from your agent's intended behavior
  (its Ethos) and, optionally, a trace source you select, Eval Author proposes a
  plan covering examples per behavior, difficulty, expected outcomes, grading,
  and rerun cost, and waits for your review before generating cases. It then
  builds the environment the tasks run in, reusing your repository's own
  services where it can and seeding realistic starting data, and proves that
  environment with a smoke task before any case relies on it.
- **Validate tasks before trusting them.** Each task is checked with controls
  before your agent is evaluated: Harbor's no-op baseline and reference
  solution, or Gym's known-correct and negative verifier fixtures. A realistic
  incorrect result must also be rejected. Evidence is bound to the task
  revision, so an edited task needs fresh validation, and setup errors are
  reported separately from agent behavior failures.
- **Find and check existing evaluations.** Discovery works in four phases
  (Probe, Explore, Judge, and Solve): it inventories the evaluations in a
  repository, explains what they test and how to run them, validates Gym and
  Harbor suites with their native tools, and runs a small sample of tasks end to
  end.
- **Audit coverage against intended behavior.** A guided audit with five
  milestones agrees on the tools, capabilities, and failure cases your
  evaluations should cover, measures coverage from ATIF traces, and explains
  findings, evidence limits, and next steps in a readable Audit coverage report.
  Without usable traces, coverage is reported as unmeasured, not 0%.
- **Decide what to build next.** Eval Author turns audit findings into ranked
  recommendations with expected behavior, verifier design, and supporting
  evidence, and can create a Gym or Harbor task for an eligible, measured
  tool-coverage gap.
- **Review and rerun generated suites.** Each generated suite gets a `README.md`
  with a readable case inventory, setup, full-suite and per-coverage-item rerun
  commands, and result locations. Harbor tasks and jobs open in Harbor's native
  viewer; Gym records and standalone ATIF traces render as a private, offline
  HTML report.
- **Work with traces.** Explain a NeMo Intake trace with cited evidence, convert
  MLflow and Gym traces to ATIF (the Agent Trajectory Interchange Format), and,
  experimentally, derive a private Harbor or native Gym task from trace
  evidence.

### Skills

All eleven skills install together. Start with `eval-author`; it selects the
workflow for your request and saves its output under `.eval-author/` in your
repository.

| Skill | Purpose |
| --- | --- |
| `eval-author` | Entry point; selects the workflow and applies the shared evidence standard. |
| `ethos` | Explore your agent and author or update a local `ETHOS.md`. |
| `eval-author-first-eval` | Plan, build, and validate a starter evaluation suite. |
| `eval-author-discover` | Inventory evaluations and check whether Gym and Harbor suites are ready to run. |
| `eval-author-audit` | Define intended coverage and measure it against trace evidence. |
| `eval-author-task-create` | Propose improvements from an audit and create a supported task on request. |
| `eval-author-environment` | Build and prove the environment a task runs in; used by first-eval and task creation. |
| `eval-author-inspect-trace` | Explain a NeMo Intake trace; selected through `eval-author`. |
| `eval-author-trace-environment` | **Experimental.** Derive and validate a private Harbor or native Gym task from trace evidence. |
| `mlflow-to-atif` | Convert MLflow traces to ATIF. |
| `gym-to-atif` | Convert a Gym Responses record to ATIF, or keep the original Harbor ATIF from a Gym run. |

### Install

From the root of your agent's repository, install for your coding assistant
(`claude-code`, `codex`, `cursor`, `pi`, or another
[Skills CLI agent](https://github.com/vercel-labs/skills#supported-agents)):

```bash
npx skills add NVIDIA-NeMo/labs-eval-author --skill '*' --agent claude-code --yes
```

This installs from the default branch. To install exactly this release, run
`git clone --branch v0.1.0 https://github.com/NVIDIA-NeMo/labs-eval-author.git`
and follow the [manual installation steps](docs/getting-started.md#manual-installation-without-nodejs),
which need only Git and a POSIX shell. Then ask your assistant:

```text
Use eval-author to help me with the evals for my agent.
```

### Requirements

- A coding assistant that can read and write project files and run shell
  commands. Installing with `npx` also needs Node.js 22.20+ and Git.
- Repository inventory, Ethos authoring, and case planning need no evaluation
  runtime.
- Harbor workflows need the Harbor CLI and a supported Python environment. This
  release is tested with Harbor 0.20.0. Docker-backed tasks need Docker, plus
  Compose for sidecar services.
- Gym workflows need NeMo Gym v0.6.0 or later in its own Python 3.13.14+
  environment.
- Bundled helper scripts need Python 3.11+, plus PyYAML and jsonschema for audit
  specifications. Measuring coverage from ATIF traces needs Python 3.12+ and the
  [audit dependencies](skills/eval-author-audit/requirements.txt), including
  Harbor.
- Inspecting Intake traces needs a working `nemo` CLI, an explicit NeMo Helix
  workspace, and read access to Intake.
- Running your actual agent needs its own model credentials and dependencies.

See the [full requirements](docs/getting-started.md#requirements) for each
workflow.

### Known limitations

- Generated tasks can be too easy. Passing controls show that a task and its
  grader work; they do not show that the task is challenging or measure your
  agent's performance.
- Coverage findings are limited by the traces you supply. An uncovered item can
  reflect a missing test, an agent failure, or insufficient evidence.
- Task creation from an audit handles one eligible, measured tool-coverage gap
  at a time. Other recommendations may need further design or measurement.
- The trace-to-environment workflow is experimental, including task creation,
  validation, and publication review. Publication review, export, automated
  readiness, and batch reporting cover Harbor tasks only; native Gym tasks from
  traces stay private.
- Discovery can describe evaluations in other formats, such as OpenTelemetry,
  MLflow, or ATIF data, but cannot convert them into Gym or Harbor suites.
- Gym compatibility is tested against v0.6.0; newer releases have not been
  verified. On Python versions older than 3.13.14, installers can silently pick
  an older Gym that lacks commands Eval Author needs.
- On Docker Desktop, Harbor 0.20.0 and 0.23.0 can reject tasks that use the
  `no-network` or `allowlist` network modes, because Docker Desktop's kernel can
  lack the nftables support Harbor's egress control needs. Use a Linux Docker
  host or a provider that supports these modes; otherwise Eval Author records
  isolation as unproven rather than relaxing the policy. See
  [network policy](skills/eval-author-environment/references/harbor.md#network-policy).
  Trace-derived Harbor tasks require `no-network`, so validating them locally
  can be blocked the same way.
- The offline HTML reader renders evidence as recorded. It does not validate
  ATIF schemas or confirm which run belongs to which case.

### Feedback

Tell us where proposed cases miss important behavior, graders judge outcomes
incorrectly, coverage findings are unclear, or generated tasks are too easy. If
an NVIDIA contact shared this preview with you, send feedback through that
contact. Otherwise, use the
[NVIDIA Developer contact form](https://developer.nvidia.com/contact) with
**Eval Author research preview feedback** in the subject. Avoid sending raw
traces, prompts, credentials, or user data in an initial message.

This project is not currently accepting code contributions; see
[CONTRIBUTING.md](CONTRIBUTING.md).
