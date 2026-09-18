<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Development

## Validation

CI runs copyright headers, OSV-backed third-party license disclosure checks,
Ruff lint, and formatting once in the **Quality** job, following the
[`labs-trace-intel` CI](https://github.com/NVIDIA-NeMo/labs-trace-intel/blob/main/.github/workflows/ci.yaml)
layout. Tests run separately on Python 3.12 and 3.13. Quality and test failures
fail CI; skill evaluation remains advisory.

OSV-Scanner is pinned to version 2.3.3 and verified by SHA-256 before execution.
The license check compares the runtime dependency inventory and collected
upstream notices against the committed files. It is not a vulnerability gate:
scanner vulnerability findings do not currently fail the license generator.
Eval Author distributes standalone skills (`tool.uv.package = false`), so the
reference repository's wheel/sdist builds and distribution-license checks do
not apply here.

Run `uv sync --locked` and `make hooks` to install the DCO commit-message hook.
See [CONTRIBUTING.md](CONTRIBUTING.md) for sign-off and PR-title conventions.
Before committing, check a prepared message with
`make commit-check COMMIT_MSG=/path/to/prepared-commit-message`; the hook also
runs on `git commit`. Plain `make commit-check` validates the current `HEAD`
commit, so it also works after cloning or pulling a merged change.

When adding NVIDIA-authored files or changing dependencies, update the tracked
licensing artifacts first:

```bash
make update-copyright-headers
make update-licenses
```

For dependency changes, run `uv add <package>` and `make update-licenses`, review
the generated diff, and commit it. Generation requires `osv-scanner` 2.3.3 on `PATH`
and automatically collects license and attribution texts for locked runtime
dependencies and all extras into `third_party/NOTICES.txt`, with indexes in
`THIRD_PARTY_LICENSES.md` and `third_party/licenses.jsonl`.

Only exceptions require manual work: if a distribution omits its license, add a
version-specific, checksum-pinned upstream document in `third_party/license_exceptions.yaml`.
Unknown license terms require a shared text under `third_party/license_texts/` and,
where necessary, a reviewed compatibility entry in `third_party/license_overrides.yaml`.
The standard texts were sourced from SPDX license-list-data commit
`16f3aa6c3bdd62e50f8b1cf618f32d2a510250ee`; original package notices are retained separately.

`make check-licenses` verifies the generated disclosures. Scanner intermediates and
download caches live in ignored `tmp/`; a cold cache requires network access.
These notices cover this source distribution;
shipping containers or bundled native environments requires collecting notices from
those actual artifacts too, since platform wheels can bundle additional libraries.

Run the same read-only checks used by CI:

```bash
make check-copyright-headers
make check-licenses
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked pytest
```
