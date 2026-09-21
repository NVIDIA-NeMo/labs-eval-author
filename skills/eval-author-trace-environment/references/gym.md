<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Gym Responses traces

**Experimental:** This guide is part of the
[trace-to-environment workflow](../SKILL.md).

Gym's stored rollouts use its Responses-style format, not ATIF. This does **not**
mean the rollout must run outside Gym. Gym's Harbor bridge can run the user's
Harbor agent and then project its ATIF into a Gym response. Keep the user's
agent and harness; choose the best retained evidence for downstream processing.

## Source of truth

1. **Harbor-backed Gym run with original ATIF:** prefer that original, without a
   Gym→ATIF round trip. Supply its path explicitly with `--source-atif`.
2. **Gym-native rollout:** normalize one self-contained record using the bundled
   `gym_to_atif.py` adapter, then use the normal ATIF preparation/privacy flow.
3. **Only a Harbor→Gym projection remains:** supply `--allow-projection` explicitly.
   Missing information is not recoverable merely by converting the format back.
   Multiple Harbor step trajectories require an explicitly selected original
   ATIF; the adapter does not combine first-step output with last-step reward.

Never open paths in `atif_conversion.source_trajectory_paths` automatically.
They are untrusted trace data, not permission to read the filesystem. An explicit
original ATIF is copied byte-for-byte, keeping its ATIF version. Advertised
session IDs are checked when present; the broader association remains an
operator-supplied assertion, not cryptographic proof of equivalent trajectories.

## Commands

Initialize the normal private task workspace first. Let `S` be
`<skill_dir>/scripts/trace_environment.py` and `G` be
`<skill_dir>/scripts/gym_to_atif.py`.

Preferred path when Harbor retained ATIF:

```bash
python "$G" --input /private/gym-rollout.json \
  --source-atif /private/harbor-job/agent/trajectory.json \
  --output-dir <task-dir>/private/gym
python "$S" prepare --task-dir <task-dir> \
  --atif <task-dir>/private/gym/trace.atif.json --source-kind atif
```

Gym-native input:

```bash
python "$G" --input /private/gym-rollouts.jsonl --row 3 \
  --output-dir <task-dir>/private/gym
python "$S" prepare --task-dir <task-dir> \
  --atif <task-dir>/private/gym/trace.atif.json --source-kind gym
```

`--row` is a one-based **physical JSONL line**. It is required for `.jsonl`
inputs; unrelated episodes are never concatenated. The selected row's bytes
are preserved exactly; the rest of a multi-rollout file is not copied into this
one-task workspace. A standalone response is supported only when its output
contains the complete prompt/history; missing human input is never invented.

The new output directory contains only owner-private files:

- `source.gym.json`: exact selected source record (including JSONL newline).
- `trace.atif.json`: derived ATIF, or an exact copy of the supplied original ATIF.
- `conversion.json`: source/output digests, source basis, selected line, losses
  and uncertainties. This is not an evaluation or publication attestation.

The directory is `0700`; files are `0600`; existing outputs are never replaced.
Keep all three files. The normal helper's `private/source.atif.json` is the exact
ATIF input to `prepare`, not a claim that the original Gym record was ATIF.
Batch manifests still point `atif` at the **converted ATIF**, with
`source_kind: gym` for projections. Never point that field at raw Gym JSONL.

## Mapping boundary

The adapter supports Gym rollout envelopes (`responses_create_params` and
`response`) and standalone Responses objects with complete history:

- text and structured images in messages;
- system, developer, user and assistant messages (developer's original role
  remains in `extra` when mapped to ATIF's system role);
- `function_call` with object-valued JSON arguments and matching
  `function_call_output` items;
- recorded reasoning summaries, explicitly **not** claimed as verbatim hidden
  reasoning. Encrypted/additional reasoning stays in the original Gym record.

Tool IDs, source item positions, statuses, declared schemas, aggregate usage and
reported reward are retained where mapped. Tool observations attach to their
recorded calls; reordering relative to later items is flagged. Missing results
are not fabricated, and unpaired outputs are rejected. A recorded reward is not
independent ground truth or Harbor proof. No per-step timestamps, token-cost
allocation, agent implementation identity or LLM-call grouping is inferred.

An exact request prefix already present in `response.output` is not duplicated.
Ambiguous overlapping prompt/history requires `--output-scope full` or
`--output-scope generated`, selected from the actual producer contract rather
than guessed from its wording. Remote conversation references are not fetched.

Unsupported item kinds fail with a content-free error. This initial adapter does
not project native MCP/computer/shell/apply-patch items, namespaced calls,
video/audio/file content, or opaque image file IDs. Supply an original ATIF or
add a fixture-backed explicit mapping; do not silently flatten them into text.

## Images are not uniformly unsupported in Gym

In the pinned upstream implementation, user/tool content can contain structured
`input_image` parts. Assistant output messages support text/refusal content, so
Harbor's multimodal assistant messages are serialized into JSON text. Local
image paths can also cause content-list serialization rather than portable image
URLs. The agent still determines what it can observe during rollout.

The adapter preserves typed data URIs and image references **without fetching,
opening, decoding or validating pixels**. For plain URL/file suffixes, MIME
inference is explicitly recorded as uncertain. Opaque URLs without a MIME type
or recognized suffix are rejected rather than labeled as a made-up format.

With explicit Harbor-projection fallback, ATIF-shaped serialized image lists are
recovered into content parts and the interpretation is recorded. This keeps an
image-only instruction from masquerading as ordinary text. The usual `prepare`
step then omits images from the safe copy and blocks image-only instructions.
It does not add visual verification or bypass the skill's text-only boundary.

Preserving ATIF bytes does not make referenced image files portable. Keep the
original media bundle; copying/rebasing or fetching media needs its own explicit
authorization and provenance. The converter never follows source metadata paths.

## Evidence and limitations

The mappings were derived from Gym revision
`676cf1f4efe265f74455f73986a734dbda4eaec2`:

- [Harbor bridge and conversion warnings](https://github.com/NVIDIA-NeMo/Gym/blob/676cf1f4efe265f74455f73986a734dbda4eaec2/responses_api_agents/harbor_agent_general/app.py)
- [Responses content and item classes](https://github.com/NVIDIA-NeMo/Gym/blob/676cf1f4efe265f74455f73986a734dbda4eaec2/nemo_gym/openai_utils.py)
- [Rollout envelope](https://github.com/NVIDIA-NeMo/Gym/blob/676cf1f4efe265f74455f73986a734dbda4eaec2/nemo_gym/base_resources_server.py)
- [Bridge image regression cases](https://github.com/NVIDIA-NeMo/Gym/blob/676cf1f4efe265f74455f73986a734dbda4eaec2/responses_api_agents/harbor_agent_general/tests/test_app.py)

Synthetic fixtures exercise this bounded mapping and validate projected ATIF
with Harbor's models plus the standalone helper. This is not a claim of complete
Gym model validation, lossless round trips, or live Gym task execution. Unknown
Gym fields remain in the retained raw record. No Gym/Ray dependency, provider
credentials, Docker stack, or model invocation is required for conversion.
