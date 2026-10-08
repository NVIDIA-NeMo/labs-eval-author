<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Ethos skills

The original two-skill Ethos workflow, restored as a baseline for evaluation:

| Skill | Role |
| --- | --- |
| [`nemo-explore`](skills/nemo-explore/SKILL.md) | Explore the agent's code and docs, then interview the user for intended behavior. Hands off to `nemo-ethos`. |
| [`nemo-ethos`](skills/nemo-ethos/SKILL.md) | Write, validate, and review `ETHOS.md` from the explore answers, using the bundled [schema-v1 template](skills/nemo-ethos/references/templates/ethos.md). |

Each skill's `tests.json` holds its original test cases.

## Provenance

Copied byte-for-byte from
[NVIDIA-NeMo/nemo-helix](https://github.com/NVIDIA-NeMo/nemo-helix) at commit
`08128e6d0e1248928d4d4152a39bc06360ca74b1` (2026-09-18), path
`packages/nemo_platform_ext/src/nemo_platform_ext/skills/`. That is the last
revision before upstream removed both skills in `0fd8da64c` (#2281). Files keep
their upstream SPDX headers; `tools/check_copyright_headers.py` accepts that form
under `ethos/skills/` only.

Keep that baseline reviewable: make each later change in its own commit and
evaluate its behavioral impact against the restored originals.

## Status

The consolidated [`skills/ethos`](../skills/ethos/SKILL.md) remains the skill that
Eval Author installs and hands off to. These skills are not wired into Eval Author,
and `npx skills add NVIDIA-NeMo/labs-eval-author --skill '*'` does not discover
`ethos/skills/`.

To try both skills together from a checkout, run
`npx skills add ./ethos --agent <assistant>` at the repository root.

As restored, the skills still target NeMo Platform:

- Preconditions `nemo_cli_available`, `nemo_setup_complete`, and `workspace_exists`.
- `nemo-ethos` treats a NeMo Filesets fileset as the canonical copy and
  `agents/<name>-ethos/ETHOS.md` as a local cache.
- Handoffs and `not-for` entries name `nemo-build-agent`, `nemo-model-selection`,
  and `nemo-skill-selection`, which this repository does not ship.
- NeMo Platform's earlier `nemo-explore`, which hands off to `nemo-spec`, uses the
  same skill name.
