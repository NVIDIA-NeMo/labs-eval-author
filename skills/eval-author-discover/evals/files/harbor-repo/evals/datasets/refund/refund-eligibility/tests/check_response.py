# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Grade the task outcome without inspecting which tools the agent used."""

import argparse
import json
from pathlib import Path


def is_correct(response):
    if not isinstance(response, dict):
        return False
    return response == {"decision": "eligible", "days_since_purchase": 18, "reason": "within_30_days"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--response", type=Path, default=Path("/app/response.json"))
    parser.add_argument("--reward", type=Path, default=Path("/logs/verifier/reward.txt"))
    args = parser.parse_args()
    try:
        correct = is_correct(json.loads(args.response.read_text()))
    except (OSError, ValueError, TypeError, KeyError):
        correct = False
    args.reward.parent.mkdir(parents=True, exist_ok=True)
    args.reward.write_text("1\n" if correct else "0\n")


if __name__ == "__main__":
    main()
