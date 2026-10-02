# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

# FILL: the base image of the kit's build/Dockerfile: a public image, or a pushed one pinned by
# digest; never a locally built kit tag.
FROM <base image>

# FILL: the other steps of the kit's build/Dockerfile, without an ENTRYPOINT, since Harbor supplies
# the command. main needs bash, the agent's own code with the clients or CLI its tools use, and the
# tools the main collect hook runs.

# FILL: the kit's generated starting data, copied from its data/ into environment/data/, at the
# path the kit's build expects.
COPY data/ <data path>
