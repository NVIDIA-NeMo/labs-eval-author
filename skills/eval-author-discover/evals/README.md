<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Discover behavior evaluations

Eight authored SkillEvaluator Tier 3 cases exercise Discover using four synthetic
repositories. These are executable acceptance candidates, not evidence that a
live agent has passed. Fixtures need no customer data, production services,
credentials, or nested Docker. The outer evaluator needs Docker and agent/grader
credentials for live execution.

## Case coverage

| Case ID | P0 case | Fixture | Expected behavior |
| --- | --- | --- | --- |
| `discover-D01-existing-harbor` | D01 | `harbor-repo` | Explain both suites and documented commands, distinguish inventory from readiness, then offer audit. |
| `discover-D02-no-agent-evals` | D02 | `empty-repo` | Distinguish helper tests from agent evals; reuse confirmed absence and recommend bootstrap. |
| `discover-D03-non-harbor` | D03 | `script-repo` | Identify the Python/JSONL suite and its existing run command without conversion. |
| `discover-D04-external-location` | D04 | `external-repo` | Report the absent referenced checkout and ask for access without inferring no evals. |
| `discover-D05-missing-provider` | D05, provider variant | `harbor-repo` | Run discovery in `python3 -I -S`, retain inventory, and report unproven readiness from native JSON. |
| `discover-D06-inventory-only` | D06, stop variant | `harbor-repo` | Finish inventory without beginning or asking to start an audit. |
| `discover-D06-audit-handoff` | D06, continue variant | `harbor-repo` | Summarize inventory, then enter the requested audit's local Ethos checkpoint without duplicate authorization. |
| `discover-negative` | Trigger boundary | None | Answer unrelated arithmetic without starting an eval workflow. |

D05 variants covering invalid configs, unavailable backends, dropped tasks, and
missing variables remain future live cases. Existing deterministic provider tests do not prove those
conversational behaviors. D06 exercises one handoff turn, not a complete
multi-turn audit or content-review conversation.

The Harbor fixture selects `oracle` for reference-solution checks, not a
production agent. Both tasks were natively scaffolded and are checked by Harbor
0.20.0 in repository tests. They have outcome verifiers, but this dataset does
not start their Harbor jobs. The non-Harbor runner grades stored responses and
writes `.suite-was-run` if invoked.

The missing-provider runtime uses `-I -S` to exclude environment/user paths and
installed site packages. Standard-library discovery can still inventory JSON
configs. This establishes unavailability only in that selected runtime.

## Grading and comparison

Native assertions grade explanations, command accuracy, evidence claims, tool
behavior, and handoffs. The standalone `grader.py` adds artifact checks:

| Metric | Deterministic check |
| --- | --- |
| `report_created` | Nonempty discovery report; negative case instead expects no input-workspace artifacts. |
| `source_preserved` | All supplied source bytes, including historical provider evidence, remain unchanged. |
| `write_scope_respected` | New repository paths stay under `.eval-author/`; audit handoff may also create root `ETHOS.md`. |
| `no_suite_run` | Fixture execution marker absent; negative case has no shell calls. Other execution boundaries use native trace assertions. |
| `provider_evidence` | D05 has native missing-provider fields, both configs/tasks, correct repository identity, and an observed discovery invocation. Other cases pass as not applicable. |
| `discover_overall` | All five artifact checks pass. |

Artifact checks do not prove report semantics, detect reverted writes, inspect
writes outside the input repository, validate drafted Ethos, or establish that
no arbitrary program ran. The provider check establishes consistency, not
cryptographic attestation of subprocess output. Native assertions and existing
provider tests cover complementary behavior.

`default_plus_custom` keeps native overall/pass@1 unchanged. The collector
therefore reports artifact pass counts, per-case metrics/verdicts, and failed IDs
separately. Missing custom evidence makes collection incomplete. Assess both
native behavior results and artifact checks; CI remains advisory.

Group mode includes `eval-author` and `eval-author-audit` in both arms. The
baseline removes only Discover, so lift measures its incremental contribution
given those dependencies. Runtime skill copies exclude evaluator datasets and
graders. Explicit case `files` lists stage only the selected fixture.

## Validate and run

Use pinned SkillEvaluator `7e189c6bdada8910dfa1684f25feedca87f2db85` with `[tier3]`
in a separate environment. Keep its Harbor 0.13.2 separate from the repository's
Harbor 0.20.0 development environment.

Keyless checks, from the repository root:

```bash
skillevaluator tier3 validate skills/eval-author-discover --json
uv run --locked pytest -q tests/test_discover_skill_evaluations.py tests/test_live_skill_evaluations.py
python3 tools/collect_live_skill_evaluations.py --tier 3 \
  --skill eval-author-discover --output /tmp/new-discover-plan
```

After live execution is authorized, skill inputs are clean in Git, and the
documented inference credential is configured:

```bash
python3 tools/collect_live_skill_evaluations.py --run --tier 3 \
  --skill eval-author-discover --provider inference_hub \
  --output /tmp/new-discover-run
```

Use fresh output directories outside the checkout. Discover allows eight cases,
one attempt per arm, one concurrent case, and the existing thirty-minute timeout.
Its collector profile locks the reviewed config shape and sibling list; update
collector tests with policy changes. Other skills retain their four-case profile.

## Refresh fixture hashes

Review fixture changes before updating the embedded manifest. BYOG copies only
`grader.py`, so preservation checks cannot load a companion source manifest.
Repository tests reject stale hashes. From the repository root:

```bash
python3 - <<'PY'
import hashlib
import json
from pathlib import Path

root = Path('skills/eval-author-discover/evals')
manifest = {
    repo.name: {
        path.relative_to(repo).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(repo.rglob('*')) if path.is_file()
    }
    for repo in sorted((root / 'files').iterdir())
}
path = root / 'grader.py'
text = path.read_text()
start = text.index('# BEGIN FIXTURE HASHES')
end = text.index('# END FIXTURE HASHES')
block = '# BEGIN FIXTURE HASHES (regenerate using the recipe in README.md)\n'
block += 'FIXTURE_HASHES = ' + json.dumps(manifest, indent=4) + '\n'
path.write_text(text[:start] + block + text[end:])
PY
uv run --locked ruff format skills/eval-author-discover/evals/grader.py
```

Keep outputs, caches, and execution markers out of fixture sources. Run native
validation and focused tests after editing fixtures, cases, or grading logic.
