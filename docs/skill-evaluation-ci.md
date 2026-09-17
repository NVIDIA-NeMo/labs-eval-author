<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SkillEvaluator CI reports

The `skill-evaluator` CI job scans every `skills/*/SKILL.md`, including the main
`eval-author` router and all sub-skills. Newly added skill directories are picked
up automatically. The router is measured as its own skill; the suite verdict is
derived from all skill verdicts, without averaging unlike quality scores.

CI uses SkillEvaluator 0.2.1 at commit
`7e189c6bdada8910dfa1684f25feedca87f2db85`, SkillSpector 2.11.2, Semgrep 1.177.0,
and Gitleaks 8.30.1. SkillSpector is installed from its upstream Git repository at
`69dcdfb74487d361ba4c811d088cfdea2ff3a9dc`, not from the Python package registry.
These are isolated CI tools, not runtime dependencies shipped
with the skills. Their transitive Python dependencies are resolved at installation;
top-level pins do not imply a fully locked scanner environment.

The external Tier 1 profile runs schema, version, security, PII, license,
code-integrity, Unicode, quality and lint checks, with quality threshold 70.
LLM checks and deduplication are disabled. No agent jobs, model calls or private
traces are used. Each skill has a 90-second timeout and a separate report directory.
One failed scan does not prevent scanning the remaining skills.

The job uploads `skillevaluator-summary.json` in the artifact named
`skill-evaluations-<run-id>-<attempt>`, retained for 30 days, including on collection
failure when a summary could be produced. After an installation failure, the
collector still runs unless the job was cancelled, recording missing tools or
reports as incomplete evidence. Raw scanner reports, console logs and
scanner home directories are not uploaded because they may include source text
or findings. They remain available in a local invocation's output directory.

The versioned `nemo.eval_author.skill_evaluations.v1` summary contains:

- Repository and actual checked-out Git revision, timestamps, CI run and attempt.
- Configured evaluator source pin, observed tool versions and requested policy.
- Each discovered skill's path and content digest, scan exit code, collection error,
  raw report SHA-256, verdict, validator statuses, quality score and grade.
- Counts of passed, failed and incomplete skills and an overall verdict.

Quality scores are retained independently of the gate: a score of 99 does not
make an incomplete security scan pass. Missing reports, missing validators and
timeouts remain incomplete. The configured evaluator pin is installation intent;
the local command does not attest an arbitrary supplied executable's Git origin.
For pull requests, checkout normally uses GitHub's merge commit; `source_revision`
records that exact revision rather than claiming it is the PR head.

For future `nemo-eval-author-fixtures` ingestion, download the summary from this
job, verify the repository/workflow identity, and retain `(source_revision,
run-id, attempt, skill path, tree_digest, report_digest)`. Treat observations as
skill-package checks, not dataset success rates. Keep missing scores null and
distinguish incomplete from failed. CI artifact availability is limited by the
retention period; a long-term consumer should archive summaries.

The entire job is **non-blocking**, using job-level `continue-on-error: true`.
Findings, installation errors, timeouts, collection errors and upload failures
must not fail the CI workflow. Collection errors remain visible in step logs and
the summary when available; artifact upload always runs when the runner can
continue. If checkout, Python setup or infrastructure prevents collection, no
artifact is available and upload emits a warning. Existing tests and lint retain
their normal blocking behavior.
The collector's optional local `--enforce` flag does not change this CI policy.

Local invocation with the pinned tools installed on `PATH`:

```bash
python tools/collect_skill_evaluations.py --output /tmp/new-skill-evaluation
```

Use a new output directory each time. Skills must be clean in Git. The collector
does not rewrite skill sources. Raw output stays local; only the summary has the
allowlisted fields intended for fixtures ingestion.

## Tier 2 and Tier 3: automatic advisory workflow

`skill-evaluation-live.yml` runs automatically on same-repository pull requests
targeting `main` or the stacked base `ci/skillevaluator-reports`, and on pushes
to `main`, matching Tier 1's triggers. Automatic runs select both tiers and all
skills. Fork PRs are excluded. All live model roles use NVIDIA Inference Hub
with the explicitly authorized CI-only credential in the `skill-evaluator`
GitHub environment. The repository variable
`SKILL_EVALUATION_LIVE_ENABLED=true` enables live work; setting it to false is
the opt-out for automatic and manual execution.

Both the keyless plan and live job use `continue-on-error: true`. Findings,
missing credentials, evaluator failures, timeouts, and upload errors are
advisory. Unit tests and Tier 1 run independently, without waiting for this
workflow. Do not configure the live jobs as required merge checks if pending
live runs should not delay merging. New commits cancel superseded runs on the
same PR or branch.

Manual dispatch remains available from `main` for a selected tier and skill.
It defaults to a keyless plan; `run_live: true` opts into execution for that
dispatch. The plan has no environment secrets or environment-scoped model
overrides, so it describes coverage rather than validating live configuration.

Tier 2 runs `context-optimization-check` for selected skills (embeddings plus
chat), then `similarity-check` over the complete collection (embeddings only).
Intentional overlap between the router and sub-skills needs human interpretation;
similarity is not proof that a skill should be deleted. Each command has a
five-minute timeout. Provider errors and incomplete analysis remain incomplete,
distinct from completed scans with duplicate-content findings.

Tier 3 runs `tier3 evaluate` with OpenCode in Docker, one attempt per case,
one concurrent case, both arms, and the native agent runtime preflight enabled.
CI installs Docker Compose 5.5.1 with a pinned SHA-256. The Ubuntu runner's
Compose 2.38.2 rejects Harbor's `up --wait` for these generated containers with
`has no healthcheck configured`, even after successfully building and starting
the container. Keep the native preflight enabled when updating this runtime.
It validates the authored dataset first and never uses autopilot or generates
cases during CI. Each skill is limited to four cases and thirty minutes.
Execution is capped by these counts and timeouts, **not by a dollar budget**;
configure provider spending/rate limits before enabling live work. Docker
containers may outlive a killed evaluator process until the ephemeral runner
is destroyed. For local runs, inspect Docker and clean up the run's containers
after interruption.

The live tool environment installs the same SkillEvaluator source pin with
`[tier2,tier3]`. Its Harbor dependency is **0.13.2**, isolated from this repository's
development Harbor **0.20.0**; do not combine the environments or upgrade one to
match the other. The Docker Compose plugin and outbound access to the provider, package
registries, and container registries are needed. The upstream Docker runtime
installs the agent CLI; a separate host OpenCode installation is not required.
The evaluator source is pinned, but transitive packages, downloaded agent tools,
and base images are not fully locked by this workflow.

### Setup needed

Repository settings verified on 2026-09-17 include the `skill-evaluator`
environment, its `INFERENCE_HUB_API_KEY` secret, repository enable variable
`SKILL_EVALUATION_LIVE_ENABLED=true`, and environment model override
`SKILL_EVAL_LLM_MODEL=azure/openai/gpt-5.6-luna`. No environment protection rules
or deployment-branch restrictions were configured.

1. Same-repository PRs run automatically, including this PR before merge.
   Once merged, pushes to `main` also run automatically and manual dispatch is
   available from `main`. The ordinary CI and title workflows also accept
   `ci/skillevaluator-reports` as a PR base so this stack receives normal checks.
2. Use the existing `skill-evaluator` environment. Optional deployment branch
   restrictions and required reviewers can be configured in GitHub settings;
   declaring an environment in YAML does not configure them. The workflow
   requires the repository enable flag. Required reviewers or branch restrictions
   can pause or prevent automatic live runs; configure them accordingly.
3. The environment secret **`INFERENCE_HUB_API_KEY`** must contain your NVIDIA
   Inference Hub **inference** key from
   [Hub key management](https://inference.nvidia.com/key-management). The Hub
   metadata key and NVIDIA Build key are not used by this workflow. Do not put
   credentials in `evals/config.yml`.
4. The default chat/grader/agent model is **`azure/openai/gpt-5.6-luna`** and
   the default embedding model is **`azure/openai/text-embedding-3-small`**.
   Both IDs were listed by the Hub's authenticated `/v1/models` catalog on
   2026-09-17. This is a small-model starting point for CI smoke evaluation;
   a small chat request to Luna through the Hub also succeeded. Catalog presence
   and a connectivity check do not establish evaluation quality.
   These OpenAI models are accessed through NVIDIA Inference Hub, not a direct
   public OpenAI connection.

   Optional environment variables override the defaults:

   | Variable | Purpose | Default |
   | --- | --- | --- |
   | `SKILL_EVAL_LLM_MODEL` | Chat analysis and Tier 3 grading | `azure/openai/gpt-5.6-luna` |
   | `SKILL_EVAL_EMBEDDING_MODEL` | Embeddings for context and similarity checks | `azure/openai/text-embedding-3-small` |
   | `SKILL_EVAL_AGENT_MODEL` | Tool-capable OpenCode agent model | The selected chat model |

   All three accept **raw Hub model IDs**, including any namespace shown in the
   Hub catalog. The collector adds the `openai/` adapter prefix for OpenCode;
   do not add an extra adapter prefix yourself. A raw Hub ID that already starts
   with `openai/` retains that namespace after the adapter prefix is added.
   Unset or blank variables use the defaults above. Tier 3 does not use embeddings.

   Chat, embedding, and agent requests use the fixed endpoint
   **`https://inference-api.nvidia.com/v1`**. The collector maps the one inference
   key to SkillEvaluator's `SKILL_EVAL_LLM_API_KEY` and
   `SKILL_EVAL_EMBEDDING_API_KEY`, selecting `openai-compatible` for both.
   SkillEvaluator passes the same key and endpoint to OpenCode using
   `OPENAI_API_KEY` / `OPENAI_BASE_URL`; these are SDK variable names, not a route
   to public OpenAI. The pinned Harbor adapter registers the selected model and
   writes the Hub URL into OpenCode's provider configuration.

   Verify the key has chat/tool-calling and embedding access, and that the
   GitHub runner and its Docker containers can reach the Hub. Tier 2 requires
   an actual embedding model; a chat-only model is insufficient. If Hub
   embeddings or runner access are unavailable, the affected tier stays
   unrun/incomplete. This workflow has no public OpenAI or NVIDIA Build fallback.
   Keyless checks do not validate live inference. The earlier four-case
   `mlflow-to-atif` A/B smoke completed on `gpt-5.4-mini`; its scores should not
   be attributed to Luna. Each report records its configured model IDs.
5. Set the **repository** variable `SKILL_EVALUATION_LIVE_ENABLED=true` after
   setup; the job condition cannot read an environment-only variable.
6. Inspect **SkillEvaluator Tier 2 and 3** on the next same-repository PR update
   or `main` push. To investigate one skill, manually dispatch from `main` with
   a selected tier/skill and `run_live=true`; omit live opt-in for a keyless plan.

### Embedding alternatives

The default remains `azure/openai/text-embedding-3-small`. Three other Hub models
returned valid vectors for two synthetic inputs using the evaluator's existing
OpenAI-compatible embedding request shape on 2026-09-17:

| Hub model ID | Observed dimensions | Why compare it |
| --- | --- | --- |
| `azure/openai/text-embedding-3-large` | 3072 | A direct larger-model comparison against the current small embedding model |
| `nvidia/nvidia/nemotron-3-embed-1b` | 2048 | NVIDIA's multilingual retrieval embedding model |
| `nvidia/qwen/qwen3-embedding-8b` | 4096 | Multilingual and code-retrieval coverage |

Model references: [OpenAI embedding model](https://developers.openai.com/api/docs/models/text-embedding-3-large),
[NVIDIA embedding model](https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-3-embed-1b),
and [Qwen model card](https://huggingface.co/Qwen/Qwen3-Embedding-8B).
These are compatibility checks, not quality benchmarks. Compare Tier 2 findings
on the same skill collection before changing the default; similarity thresholds
may behave differently across embedding models. Embeddings do not affect Tier 3.

### Initial Tier 3 scope

Two authored synthetic datasets ship in the skill-owned `evals/` directories:

- `eval-author`: four routing cases covering explicit discovery, implicit first
  evals, a corrected request for trace-environment creation, and an unrelated
  negative case. This measures routing and evidence boundaries, not successful
  execution of downstream sub-skills.
- `mlflow-to-atif`: explicit and implicit offline conversion, refusal to invent
  a missing human instruction, and a negative case. Fixture JSON is synthetic;
  no customer or Intake access is required. This measures bounded offline
  conversion, not live MLflow authentication or every normalization edge case.

The standard SkillEvaluator grader uses model judgments and trace-derived
signals. These scores do not replace our deterministic converter tests or the
trace-environment NOP/Oracle proof contract. One attempt on four cases is a
smoke evaluation, not a reliable population estimate.

All other discovered skills receive `missing_dataset` for selected Tier 3
work. Author a bounded, reviewed `evals/evals.json` and validate it before
enabling each additional skill. Harbor/Docker authoring inside a Tier 3 agent
container requires a deliberate nested-runtime design; this PR does not mount
the host Docker socket, add production credentials, or claim end-to-end
trace-environment proof. Relative sibling-skill dependencies also need an
explicit group evaluation design before measuring those sub-flows.

### Reports and local checks

The separate `nemo.eval_author.live_skill_evaluations.v1` JSON preserves the
Tier 1 artifact contract. It records the exact source revision, skill-tree
digests (including eval inputs), configured evaluator pin, provider/models,
selection, bounded run policy, timestamps, report digests, and every skill's
selected or skipped status, and the fixed Hub endpoint. Tier 2 exports severity counts. Completed Tier 3
exports both arms' five dimension scores, pass counts/denominators, and signed
lift. Negative lift is a completed experiment, not an execution error. Missing
or incomplete baseline evidence cannot produce lift. No blended tier score is
computed. Configured pins/models describe intent, not independent runtime
attestation.

GitHub receives only `live-skillevaluator-summary.json` and its Markdown view,
retained for 30 days. Raw reports, prompts, trajectories, provider errors, and
logs remain outside artifacts. A checkpoint is written before execution and
after every check so later failures retain earlier results. Hard runner failure
or cancellation can still prevent upload; consumers must distinguish absent
artifacts from successful runs. These artifacts are ready for ingestion, but
this PR does not change the fixtures dashboard consumer.

Keyless plan (no SkillEvaluator installation or provider calls required):

```bash
python3 tools/collect_live_skill_evaluations.py --output /tmp/new-live-plan
```

Keyless native dataset validation using the pinned tool:

```bash
skillevaluator tier3 validate skills/eval-author --json
skillevaluator tier3 validate skills/mlflow-to-atif --json
```

After reviewing the checkout and setting `INFERENCE_HUB_API_KEY` in the host
environment (plus any optional model overrides), this command explicitly
authorizes live calls:

```bash
python3 tools/collect_live_skill_evaluations.py --run --tier 3 \
  --skill mlflow-to-atif --provider inference_hub --output /tmp/new-live-run
```

Outputs must be outside the checkout in a fresh directory. The evaluator receives
a private `HOME` under that output directory so Docker can store client state
without using the checkout or inheriting the operator's Docker credentials and
agent configuration. Live skill inputs
must be clean in Git. A keyless plan may inspect uncommitted inputs and records
`inputs_clean=false`. Missing credentials yield `not_run`, missing datasets yield
`skipped`, and malformed reports/timeouts yield `incomplete`; none is a pass.
Live collection returns nonzero for incomplete or unrun selected work, while
completed findings remain advisory. No live execution is needed for the repo's
normal unit tests, lint, or commit checks.
