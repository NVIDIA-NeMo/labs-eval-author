<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Ethos

`ETHOS.md` is the **intent layer** for a production agent: a Markdown contract
that records what the agent is for, what it must not do, what success looks like,
and what may change. Builders, reviewers, evaluators, and optimizers read it to
detect and resolve divergence between developer intent and agent execution.

Code shows implementation. Ethos records mission, constraints, success and
failure, and safe modification boundaries.

This directory holds two coding-assistant skills that create and maintain an
`ETHOS.md`:

| Skill | What it does |
| --- | --- |
| [`ethos-explore`](skills/ethos-explore/SKILL.md) | Reads the agent's code and docs, fills in what they establish, then asks one intent question at a time for what they cannot. Hands its answers to `ethos`. |
| [`ethos`](skills/ethos/SKILL.md) | Writes `ETHOS.md` from those answers using the [schema-v1 template](skills/ethos/references/templates/ethos.md), validates the front matter and required sections, and reviews the result with you. |

## Why it exists

Critical agent context lives outside the codebase: business objectives,
developer intent, success and failure criteria, and safe modification
boundaries. It is rarely written down. An optimizer or evaluator that sees only
code and traces cannot tell a real failure from a trade-off you already
accepted.

Without an Ethos, every new agent, review, or eval has to rediscover that
context, and automated changes align with whatever the traces happen to show.
With one, the same file can steer a new build, guide a review of logs and evals,
reveal divergence from intent, and keep an optimization loop inside human-set
bounds.

## Scattered context, one contract

Intent arrives in pieces:

- **Codebase:** files, docs, configs, and logic. What the agent does today.
- **Traces and logs:** telemetry, errors, and metrics. How a run looked, not
  whether that was acceptable.
- **Business goals:** objectives, value, and the result the agent is accountable for.
- **Developer intent:** tone, priorities, and judgment calls that never made it
  into a ticket.
- **Constraints:** limits, policies, and guardrails no change may cross.

`ETHOS.md` is the portable snapshot of that contract. Write the intended state,
not only the implemented one; where they differ, say so.

## What it unlocks

| It unlocks | Meaning |
| --- | --- |
| **Portable context** | Every builder, reviewer, and optimizer starts from the same file instead of reconstructing intent from the repo. |
| **Shared contract** | Humans and agents agree on purpose, bounds, and what counts as divergence. |
| **Spec-driven creation** | Purpose, goals, and expected behavior are explicit before code exists. |
| **Safe changes** | Optimization agents know what they may change, what needs approval, and what they must not touch. |
| **Recursive updates** | Intent clarified while reviewing a change, eval, or finding goes back into the file. A stale Ethos steers the next loop the wrong way. |

`Change Scope` is the machine-readable part of safe changes: each lever is
`yes`, `no`, or `with-approval`.

## Ethos is not `AGENTS.md`

| | `AGENTS.md` | `ETHOS.md` |
| --- | --- | --- |
| When it matters | Any repository a coding agent should navigate | When the repository, or a package in it, *is* an agent |
| Job | How to contribute: layout, conventions, commands | Intent, goals, and constraints |
| Location | Repository root | Next to the agent |

## What's in the file

YAML front matter (`schema_version`, `name`, `created_timestamp`, `author`, and
optional `owner` and `updated_timestamp`) followed by fifteen required sections.
Section bodies stay human-readable; the headings are the outline other agents
parse. A section with nothing to say contains `_(none)_`.

| Section | Captures |
| --- | --- |
| `Role` | What the agent does, in one concrete sentence. |
| `Purpose & Outcomes` | Why it exists, and the result it is judged by. |
| `Scope` | Who it serves, in-scope work, and boundaries. |
| `Tools` | APIs, tools, and knowledge sources it can use. |
| `Harness` | How the agent actually runs. |
| `Behavior` | Rules, tone, refusals, and policies. |
| `Principles` | How to decide when no rule in `Behavior` covers the case. |
| `Success Criteria` | What good production behavior looks like. |
| `Trade-offs` | Hard gates, priority order, and unacceptable regressions. |
| `Constraints` | Limits no optimization may cross. |
| `Evaluation Setup` | How it is tested and measured. |
| `Metric Semantics` | What metric names mean, and the claims they do not support. |
| `Change Scope` | What optimization agents may modify. |
| `Vision` | Where the agent is headed, beyond today's scope. |
| `Open Questions` | Unknowns to resolve. |

## Create an ETHOS.md

Install both skills together; `ethos-explore` hands off to `ethos`. From a
checkout of this repository:

```bash
npx skills add ./ethos --agent claude-code
```

Replace `claude-code` with your assistant's identifier. Then, in your agent's
repository, ask your coding assistant:

```text
Use ethos-explore to capture what my agent should do, then write its ETHOS.md.
```

`ethos-explore` scans the codebase first and asks at least three intent
questions, covering purpose and outcomes, principles, and vision. `ethos`
writes the file, validates it, and asks you to review it. You can also write
the file by hand from the [template](skills/ethos/references/templates/ethos.md).

To revise an existing Ethos, ask for the edit directly; `ethos` updates the
relevant sections in place and sets `updated_timestamp`.

## Current limitations

These skills come from NeMo Platform and still assume it:

- They expect the `nemo` CLI, a completed NeMo setup, and a workspace.
- `ethos` writes `agents/<agent-name>-ethos/ETHOS.md` and uploads it to a NeMo
  Filesets fileset, which it treats as the canonical copy.
- They refer to NeMo Platform skills that this repository does not ship:
  `nemo-build-agent`, `nemo-model-selection`, and `nemo-skill-selection`.

Eval Author's own installation uses the single-file
[`skills/ethos`](../skills/ethos/SKILL.md) skill, which writes a local
`ETHOS.md` without NeMo Platform. Both are named `ethos`; install one or the
other in a given assistant. `npx skills add NVIDIA-NeMo/labs-eval-author --skill '*'`
does not install the skills in this directory.

## Origin

The skills, template, and each skill's `tests.json` test cases come from
[NVIDIA-NeMo/nemo-helix](https://github.com/NVIDIA-NeMo/nemo-helix) at commit
`08128e6d0e1248928d4d4152a39bc06360ca74b1`, the last revision before upstream
removed them in `0fd8da64c`. They were renamed from `nemo-explore` and
`nemo-ethos`. This README adapts the NeMo Helix `ETHOS.md` documentation page
(`docs/agents/ethos.mdx`) from the same commit.
