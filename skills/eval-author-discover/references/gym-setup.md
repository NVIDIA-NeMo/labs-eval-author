<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Get NeMo Gym ready

Use this for Gym bootstrap or a missing Gym runtime. Prefer the repository's
existing provider and documented environment; for a new suite, offer Gym first,
Harbor second. Do not require both runtimes. Explain that Gym composes a dataset,
agent, resources server (tools, state, and verifier), and optional model server.
Installation of Eval Author's skills does not install either evaluation framework.

The compatibility baseline is [Gym v0.6.0](https://github.com/NVIDIA-NeMo/Gym/releases/tag/v0.6.0),
commit `3045a793346a31291d7ea4ae6af3f94a35036ce5`. It requires Python **3.13.14+**.
Use its own environment: Gym and Harbor pin different dependencies. A newer
colocated checkout is usable when its documented APIs and commands are verified;
record its Git revision and package version rather than calling it the release.

First inspect the selected repository's setup instructions and existing Gym
checkout. Probe only an existing interpreter; do not use an installing command as
an availability check:

```bash
/path/to/Gym/.venv/bin/python -c 'import sys, importlib.metadata; import nemo_gym; print(sys.executable, importlib.metadata.version("nemo-gym"))'
/path/to/Gym/.venv/bin/gym --help
```

When dependency setup is authorized and no existing installation works, install
from the release in a new directory (replace the destination as appropriate):

```bash
git clone --branch v0.6.0 --depth 1 https://github.com/NVIDIA-NeMo/Gym.git .eval-author/runtime/Gym
cd .eval-author/runtime/Gym
uv sync --locked --no-dev
.venv/bin/gym --help
.venv/bin/python -c 'import importlib.metadata; print(importlib.metadata.version("nemo-gym"))'
```

Keep that interpreter and CLI path in the workflow findings. Do not change a
customer's Python environment or install Gym into Harbor's environment. If `uv`
is missing, follow [uv's installation guide](https://docs.astral.sh/uv/getting-started/installation/)
within the existing setup authorization.

Installation proves only that the tools load. Native manifest validation, verifier
controls, service readiness, model access, and actual agent runs are separate
checks. Read `.agents/skills/` in the selected Gym checkout for relevant optional
Gym authoring or debugging skills; report what is available without making their
installation a prerequisite. Gym setup does not require Docker universally:
individual components may require Docker, browsers, GPUs, external applications,
accounts, or model credentials. Preserve those requirements and record blockers.
