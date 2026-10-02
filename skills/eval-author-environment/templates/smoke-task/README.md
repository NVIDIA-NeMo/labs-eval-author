<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Environment smoke task

A Harbor task skeleton for the smoke task that proves an environment kit. Its
reference solution reads and writes each dependency once through the agent's
own client code or CLI. Collect hooks export the end state after every trial,
NOP included, and a separate, offline verifier checks that the export shows each
smoke write exactly once. These runs are environment proof, not task evidence:
never declare them as a task's controls or count them among its evidence
receipts.

1. Copy this directory under the kit, from the repository root:

   ```bash
   mkdir -p .eval-author/environments/<agent-slug>/smoke
   cp -R <skill_dir>/templates/smoke-task \
     .eval-author/environments/<agent-slug>/smoke/<agent-slug>-environment-smoke
   ```

2. Build its `environment/` from copies of the kit's build files and generated
   data: the `build/` Dockerfile, any `docker-compose.yaml` and sidecar build
   contexts, and the seeded data, so the smoke task builds on its own. Never
   start it `FROM` a locally built kit tag.
3. Fill in each line marked `FILL:`, giving every dependency the same name in
   `task.toml`, `solution/solve.sh`, and `tests/test.sh`, and delete the marker.
   From the task directory, this prints nothing when you are done:

   ```bash
   grep -n 'FILL:' task.toml environment/Dockerfile solution/solve.sh tests/test.sh
   ```

4. Run NOP once and the reference solution twice from the repository root:

   ```bash
   harbor trial start -p .eval-author/environments/<agent-slug>/smoke/<agent-slug>-environment-smoke -a nop \
     --trials-dir "$PWD/.eval-author/environments/<agent-slug>/smoke/trials" --trial-name env-smoke-nop-1
   harbor trial start -p .eval-author/environments/<agent-slug>/smoke/<agent-slug>-environment-smoke -a oracle \
     --trials-dir "$PWD/.eval-author/environments/<agent-slug>/smoke/trials" --trial-name env-smoke-oracle-1
   harbor trial start -p .eval-author/environments/<agent-slug>/smoke/<agent-slug>-environment-smoke -a oracle \
     --trials-dir "$PWD/.eval-author/environments/<agent-slug>/smoke/trials" --trial-name env-smoke-oracle-2
   ```

   Expect NOP to score 0, with `export-readable` passing and every write check
   failing in its `verifier/results`, and both reference runs to score 1. A
   reference run that scores 0 means the environment or a filled-in script is
   broken. A trial without a reward is an infrastructure error, never a pass:
   `result.json` records the exception, and when an export is missing,
   `verifier/test-stdout.txt` names it and `trial.log` shows the collect hook's
   output. Fix the environment rather than the checks, and rerun with a fresh
   trial name. If Harbor rejects `no-network` on this Docker host, set both
   verifier network modes in `task.toml` to `public` for this local proof and
   record isolation as unproven.
5. Record each command, trial directory, and result in the Proof table of the
   kit's `environment-plan.md`.
