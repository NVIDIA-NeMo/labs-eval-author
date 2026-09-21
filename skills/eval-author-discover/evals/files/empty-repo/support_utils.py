# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Small text utility, not a support-agent implementation."""


def normalize_subject(subject):
    return " ".join(subject.strip().split()).lower()
