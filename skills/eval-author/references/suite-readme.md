<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Save instructions for rerunning a generated suite

Save the rerun guide at the top level of each generated evaluation suite while
authoring it, using `readme.md` for a new suite guide and preserving task README
filenames as described below. Finish it before handing the suite back. Update it
when cases, configuration, setup, or commands change. A conversation reply or run report
does not replace this entry point. Multi-task suites need a suite guide in
addition to individual task READMEs.

Use the suite's existing root under `.eval-author/`: for first-eval this is
`.eval-author/readme.md`, beside `first-eval.yaml`; for a standalone task draft,
extend `.eval-author/task-drafts/<task-slug>/README.md`. For trace-derived work,
use `<task-dir>/readme.md`, beside `task/`; a generated batch also needs a README
at its collection root. Keep the trace task's required `task/README.md` intact.
When an existing generated suite has an uppercase `README.md` at the same
location, keep its filename and content and add the rerun sections there. Do not
rename existing task READMEs or create files differing only in case. Keep
unrelated suite guides separate.
Proposal-only work does not create a suite or require this file.

## What a returning user needs

Write the guide using the generated files and verified runtime information.
It must be usable without the authoring conversation or an agent reconstructing
the commands. Include:

- **Setup and working directory:** where to run every command; the provider and
  runtime version used; installation or environment activation commands;
  dependency manifests/locks; required backend, services, agent adapter, model
  configuration, and access. Name credential variables and how to supply them
  to the configured runtime, without saving secret values. Link local setup
  files and explain fixture/state reset before each run.
- **Run the full suite:** a copyable command using the saved configuration and
  exact intended case set, including attempts and any required service startup.
  Use fresh job names/output paths on each invocation so prior results survive.
  Label whether this evaluates the actual agent or only checks task wiring.
- **Run one coverage item:** a table mapping the suite's existing requirement or
  coverage IDs and descriptions to task names/paths or dataset rows. Include
  commands for the mapped selections and a concrete example from this suite.
  A coverage item may need multiple cases; preserve all of them. If it shares a
  task with other checks, explain that selection runs the whole task. An audit
  tool/requirement ID is not automatically a provider CLI selector.
- **Read results and troubleshoot:** where each new run saves rewards, errors,
  logs, and available traces; how to inspect one case's result; the meaning of
  the actual reward fields; and remedies for known setup failures. Link the
  saved run summary for observed results and limitations.

Keep task design and verifier details in their existing documents and link them
from the guide. For an incomplete suite, save the instructions that are known,
identify blocked cases and missing setup explicitly, and label unverified or
pending commands. Do not invent an adapter, model, credential, or successful run
to complete the README. Replace authoring placeholders before describing a
command as ready to copy; explicit blockers are preferable to fake runnable
examples. Refresh the guide and link it in the final handoff even if execution
is blocked.

## Select cases without changing the experiment

Use the installed provider's help/schema to verify commands. Preserve the full
suite's agent, model, environment, verifier, attempts, and other run settings
when selecting a subset. Check the resolved selection includes exactly the
intended cases, excluding unrelated drafts and blocked cases unless explicitly
selected. Document any deliberate setting changes.

For Harbor, reuse the full-suite config. A CLI task/path override is suitable
only after checking that it replaces the selection as intended and preserves
task-specific settings. Dataset name filters do not filter an explicit `tasks`
list. When overrides cannot preserve the configuration, save a subset config
under the suite root: retain the selected task entries, remove other task and
dataset sources, and keep the non-selection settings. Do not replace the real
agent with Oracle or NOP to demonstrate an individual agent evaluation.

For example, after saving and validating a one-case config for a starter suite
whose case is `refund-policy`, its guide could show these commands from the
repository root (use the actual runtime and paths in the generated guide):

```bash
# Full suite: actual agent evaluation, with a new output directory each time.
harbor job start -c .eval-author/first-eval.yaml \
  --jobs-dir .eval-author/jobs --job-name "suite-$(date -u +%Y%m%dT%H%M%S)-$$"

# Only the refund-policy case, preserving the same agent and run settings.
harbor job start -c .eval-author/rerun/refund-policy.yaml \
  --jobs-dir .eval-author/jobs --job-name "refund-policy-$(date -u +%Y%m%dT%H%M%S)-$$"
```

For Gym, retain the selected composition, model configuration, dataset identity,
and reset procedure from `reproducibility.md`. Use a verified native selector or
save a subset JSONL with the complete original rows, including verifier fields,
in their original order. Show the exact selection and run commands, including
service startup when using `--no-serve`; do not invent a coverage-ID flag. Keep
full-suite and subset output paths distinct and fresh.

## Verify the handoff

Check the README's paths and saved configurations from its stated working
directory. Use provider validation or configuration inspection to confirm both
full-suite and individual selections and their preserved settings. Record what
was validated versus actually executed; printing a config is not run evidence.
Reuse authorized run evidence where applicable. Do not spend model credentials
just to check documentation. A returning user should be able to follow the
saved setup, run the suite or a named item, and locate the result using this
README and the files it links.
