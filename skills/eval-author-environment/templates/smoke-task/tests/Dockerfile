# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

# The separate verifier's image. Install grading dependencies here, at build time, so grading
# installs nothing and needs no network; tests/test.sh as written needs only bash, grep, and coreutils.
FROM debian:bookworm-slim
COPY . /tests/
