<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SkillEvaluator CI reports

The `skill-evaluator` CI job scans every `skills/*/SKILL.md`, including the main
`eval-author` router and all sub-skills. Newly added skill directories are picked
up automatically. The router is measured as its own skill; the suite verdict is
derived from all skill verdicts, without averaging unlike quality scores.

CI uses SkillEvaluator 0.2.1 at commit
`7e189c6bdada8910dfa1684f25feedca87f2db85`, SkillSpector 2.11.2, Semgrep 1.177.0,
and Gitleaks 8.30.1. These are isolated CI tools, not runtime dependencies shipped
with the skills. Their transitive Python dependencies are resolved at installation;
top-level pins do not imply a fully locked scanner environment.

The external Tier 1 profile runs schema, version, security, PII, license,
code-integrity, Unicode, quality and lint checks, with quality threshold 70.
LLM checks and deduplication are disabled. No agent jobs, model calls or private
traces are used. Each skill has a 90-second timeout and a separate report directory.
One failed scan does not prevent scanning the remaining skills.

The job uploads `skillevaluator-summary.json` in the artifact named
`skill-evaluations-<run-id>-<attempt>`, retained for 30 days, including on collection
failure when a summary could be produced. Tool installation failures are
non-blocking and do not manufacture a summary. Raw scanner reports, console logs and
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
continue. If installation or infrastructure fails before a summary exists, no
artifact is available. Existing tests and lint retain their normal blocking behavior.
The collector's optional local `--enforce` flag does not change this CI policy.

Local invocation with the pinned tools installed on `PATH`:

```bash
python tools/collect_skill_evaluations.py --output /tmp/new-skill-evaluation
```

Use a new output directory each time. Skills must be clean in Git. The collector
does not rewrite skill sources. Raw output stays local; only the summary has the
allowlisted fields intended for fixtures ingestion.
