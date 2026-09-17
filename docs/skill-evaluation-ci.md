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

## Tier 2 and Tier 3: explicit live workflow

`skill-evaluation-live.yml` adds a separate manual workflow. PR checks remain
credential-free Tier 1 checks. The new workflow always produces a keyless plan;
live work requires `run_live: true`, the repository variable
`SKILL_EVALUATION_LIVE_ENABLED=true`, and dispatch from `main`. The live job uses
the `skill-evaluation-live` GitHub environment and is advisory. No schedule or
automatic PR model calls are added.

Tier 2 runs `context-optimization-check` for selected skills (embeddings plus
chat), then `similarity-check` over the complete collection (embeddings only).
Intentional overlap between the router and sub-skills needs human interpretation;
similarity is not proof that a skill should be deleted. Each command has a
five-minute timeout. Provider errors and incomplete analysis remain incomplete,
distinct from completed scans with duplicate-content findings.

Tier 3 runs `tier3 evaluate` with OpenCode in Docker, one attempt per case,
one concurrent case, both arms, and the native agent runtime preflight enabled.
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
match the other. Docker Compose v2 and outbound access to the provider, package
registries, and container registries are needed. The upstream Docker runtime
installs the agent CLI; a separate host OpenCode installation is not required.
The evaluator source is pinned, but transitive packages, downloaded agent tools,
and base images are not fully locked by this workflow.

### Setup needed

Repository settings inspected on 2026-09-17 had no Actions secrets, variables,
or environments. This PR does not create credentials or change those settings.

1. Merge the parent PR #9 and this stacked PR before dispatching live CI; the
   live workflow deliberately refuses non-`main` refs. The ordinary CI and title
   workflows also accept `ci/skillevaluator-reports` as a PR base so this stack
   receives normal checks.
2. Create the `skill-evaluation-live` environment. Restrict deployments to
   `main`, add the team's required reviewer, and review the cases and current
   workflow before releasing model credentials. Environment protections are
   configured in GitHub settings; declaring an environment in YAML does not
   configure them. If this repository's plan cannot enforce these protections,
   leave live CI disabled and use the local command on a reviewed checkout.
3. Add one environment secret: `NVIDIA_API_KEY` for `nv_build` (default), or
   `OPENAI_API_KEY` for `openai`. That provider must supply chat, embeddings,
   and the selected OpenCode model. No credentials belong in `evals/config.yml`.
4. Optionally configure environment variables `SKILL_EVAL_LLM_MODEL`,
   `SKILL_EVAL_EMBEDDING_MODEL`, and `SKILL_EVAL_AGENT_MODEL`. Set all three when
   changing providers if overrides were previously configured. The defaults are:

   | Provider | Chat / grader | Embeddings | OpenCode model |
   | --- | --- | --- | --- |
   | `nv_build` | `nvidia/nemotron-3-nano-30b-a3b` | `nvidia/nv-embed-v1` | `nvidia/nvidia/nemotron-3-nano-30b-a3b` |
   | `openai` | `gpt-5.4-mini` | `text-embedding-3-small` | `openai/gpt-5.4-mini` |

   Model availability and inference permissions must be verified with the
   chosen account. An internal OpenAI-compatible service is not wired in this
   initial workflow: it additionally needs reachable endpoints, embedding
   support, TLS trust, and verified OpenCode routing. Do not treat a chat-only
   endpoint as sufficient for Tier 2.
5. Set the **repository** variable `SKILL_EVALUATION_LIVE_ENABLED=true` after
   setup; the job condition cannot read an environment-only variable.
6. Dispatch **SkillEvaluator Tier 2 and 3**, initially with `run_live=false`.
   Then dispatch one selected skill with live execution enabled. Expand to
   `all` only after inspecting a successful small run and its cost.

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
selected or skipped status. Tier 2 exports severity counts. Completed Tier 3
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

After reviewing the checkout and configuring the selected provider in the host
environment, this command explicitly authorizes live calls:

```bash
python3 tools/collect_live_skill_evaluations.py --run --tier 3 \
  --skill mlflow-to-atif --provider nv_build --output /tmp/new-live-run
```

Outputs must be outside the checkout in a fresh directory. Live skill inputs
must be clean in Git. A keyless plan may inspect uncommitted inputs and records
`inputs_clean=false`. Missing credentials yield `not_run`, missing datasets yield
`skipped`, and malformed reports/timeouts yield `incomplete`; none is a pass.
Live collection returns nonzero for incomplete or unrun selected work, while
completed findings remain advisory. No live execution is needed for the repo's
normal unit tests, lint, or commit checks.
