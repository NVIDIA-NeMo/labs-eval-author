<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Contributing

Contributions are currently limited to the NVIDIA ASE team
(`@NVIDIA-NeMo/ase_team`). Keep this repository private, with routine access
limited to that team. Organization and enterprise administrators may retain
access under NVIDIA policy. Ask an ASE maintainer to coordinate any access
change with a repository administrator before inviting other contributors.

## Development and review

Create a branch in this repository and open a pull request against `main`.
Use a Git worktree when practical. Do not commit or push directly to `main`.
Fork contributions are not supported during this restricted phase.

Use Python 3.12 or 3.13 and uv (CI uses uv 0.12.3). Before handing off or
committing changes, run the same checks as CI, plus Git's whitespace check:

```bash
uv sync --locked
make hooks
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked pytest -q -rs
make check-copyright-headers
make check-licenses
git diff --check
make commit-check COMMIT_MSG=/path/to/prepared-commit-message
```

License validation requires OSV-Scanner 2.3.3 on `PATH` and network access;
see [DEVELOPMENT.md](DEVELOPMENT.md) for setup and dependency updates.
`make hooks` installs the sign-off check for `git commit`. `make commit-check`
checks Git's last commit-message file by default; pass `COMMIT_MSG` to check a
prepared message before committing. Report any failed or skipped checks and
explain their impact in the pull request. Describe the problem, resulting
behavior, and validation.
Obtain approval from another ASE team member before merging; `.github/CODEOWNERS`
assigns that team to every file, including workflows and CODEOWNERS itself.

The default tests use synthetic evidence and mocked providers. Some checks skip
when a backend or optional plugin is unavailable. Live model execution requires
separate explicit authorization; do not enable it in ordinary CI. See
[trace fixture checks](docs/trace-derived-fixtures.md#regression-checks).
Keep credentials, customer traces, and private evaluation artifacts out of
commits, CI logs, and artifacts. Review runtime dependency additions carefully:
users copy the standalone skill trees and rely on their documented dependencies.

## Sign-off and contribution license

Contributions are licensed under this project's [Apache License 2.0](LICENSE).
Sign off every new commit to certify the [Developer Certificate of Origin 1.1](DCO),
using your own name and email configured in Git:

```bash
git commit -s -m "docs: clarify contribution requirements"
```

This adds a `Signed-off-by: Your Name <your@email.com>` trailer. Use `-s` for
amends and fixups as well. A DCO sign-off is a contributor certification, not a
cryptographic signature. Only sign off work you have the right to submit.

The local hook requires a sign-off on every commit. As in nemo-platform,
`.github/dco.yaml` configures the DCO app with `require.members: false`: the app
exempts commits authored and cryptographically verified by organization members.
That exception does not change the contributor instruction to sign off. The
configuration only takes effect after an administrator enables the
[DCO app](https://github.com/apps/dco) for this repository.

## PR titles and commit subjects

Follow nemo-platform's Conventional Commit-style PR titles:
`type(optional-scope): description`, with a maximum of 100 characters.
Examples: `fix(audit): reject missing evidence` and `docs: explain ASE access`.
Use `!` before the colon for a breaking change. Supported types are `feat`,
`fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, and
`revert`. Use the same style for commit subjects where practical; the CI format
check applies to PR titles, while the commit hook checks sign-off.

The PR-title workflow reads metadata with a read-only token and does not check
out PR code. If squash-merging, retain the semantic PR title and the appropriate
sign-off trailers in the resulting commit.

## CI trust boundary

The checked-in CI workflow tests same-repository pull requests targeting `main`
and pushes to `main` on GitHub-hosted Ubuntu runners. It uses a read-only
`GITHUB_TOKEN`, disables persisted checkout credentials and shared dependency
caching, pins actions to commit SHAs and uv to a version, and limits each job
to 20 minutes. New runs cancel older runs for the same PR or branch.

Dependency installation and tests execute code from the proposed change.
Repository writers must therefore be trusted to run code in CI. Review workflow,
dependency, build, and test changes with that in mind. Keep PR jobs free of
repository or organization secrets, privileged environments, cloud credentials,
self-hosted runners, and internal network access. Do not use
`pull_request_target` or a privileged `workflow_run` to execute PR code.

The same-repository job condition is defense in depth, not an access control:
a PR can modify workflow YAML. CODEOWNERS controls review routing, not who can
read the repository or execute workflows, and required review controls merging,
not execution before review. The settings below are required to enforce this
restricted contribution policy.

## Required administrator settings

An administrator must apply and verify these controls in GitHub; adding this
document or CODEOWNERS does not configure them:

- **Access:** keep visibility private; grant `ase_team` write or maintain access.
  Remove non-ASE routine access through other teams, direct collaborators,
  invitations, and outside collaborators. Check inherited organization base
  permissions, parent teams, installed apps, and deploy keys as well. Preserve
  required organization and enterprise administration access. Disable private
  repository forking for this restricted phase.
- **Actions → General:** disable **Run workflows from fork pull requests**.
  Keep **Send write tokens to workflows from pull requests** and **Send secrets
  to workflows from pull requests** off. Set default workflow permissions to
  read-only and disable **Allow GitHub Actions to create and approve pull
  requests**. These defaults do not stop a repository writer from changing a
  workflow's permissions; restricting write access remains essential.
- **Actions and credentials:** allow only the actions used by CI
  (`actions/checkout`, `astral-sh/setup-uv`, and
  `amannn/action-semantic-pull-request`) and require full commit SHA pins
  where supported. Deny this repository access to self-hosted runner groups.
  Remove secrets and cloud trust grants available to ordinary PR jobs; any
  future privileged workflow needs a separate review and protected environment.
- **Rules for `main`:** require a pull request, at least one approving review,
  code-owner approval, dismissal of stale approvals on new commits, approval of
  the latest push by someone other than its author, and both matrix checks
  (`test (3.12)` and `test (3.13)`) plus `semantic-pull-request` from GitHub
  Actions. Enable the DCO app for this repository and require its `DCO` check,
  bound to that app. Require branches to be up to date. Block force pushes and
  deletion, and limit bypass permissions to
  required administrators.

Verify effective access and rules after applying them. Confirm a same-repository
PR runs the test and title checks and a fork PR cannot start a workflow even if its YAML
removes the job condition. Do not treat skipped jobs as proof of access control.

GitHub documents these controls in
[Actions settings](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository),
[secure workflow use](https://docs.github.com/en/actions/reference/security/secure-use),
and [code owners](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners).
