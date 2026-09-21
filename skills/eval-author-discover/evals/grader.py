#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Check Discover's saved artifacts; native trace assertions judge their meaning.

This standalone SkillEvaluator BYOG file is copied to /tests without siblings.
Fixture hashes are embedded below and checked against source by repository tests.
It never imports the skill or executes repository code during grading.
"""

from __future__ import annotations

import hashlib
import json
import os
import shlex
from pathlib import Path

CASE_REPOS = {
    "discover-D01-existing-harbor": "harbor-repo",
    "discover-D02-no-agent-evals": "empty-repo",
    "discover-D03-non-harbor": "script-repo",
    "discover-D04-external-location": "external-repo",
    "discover-D05-missing-provider": "harbor-repo",
    "discover-D06-inventory-only": "harbor-repo",
    "discover-D06-audit-handoff": "harbor-repo",
    "discover-negative": None,
}
PROVIDER_CASE = "discover-D05-missing-provider"
AUDIT_CASE = "discover-D06-audit-handoff"

# BEGIN FIXTURE HASHES (regenerate using the recipe in README.md)
FIXTURE_HASHES = {
    "empty-repo": {
        "README.md": "b22b28617c7d19b5e006b8d2d3faeebdea99500e15b6e8d6b56567f101f0768f",
        "support_utils.py": "fe7a3fbe8a3333e57b6c6e5289c423b13962145f478c75e911f8c1e445380ce3",
        "tests/test_support_utils.py": "b55be3b5bd6488096b3754396446e732622a767fa2247640f00a44b8cd04f8ae",
    },
    "external-repo": {"README.md": "8824fa86f491a7356f3cbbef9720c3fc1cc5c39c8ae92c8e16193febc49d6168"},
    "harbor-repo": {
        ".eval-author/readiness-before.json": "0ed28688989d18f8b0dd2b48c1f6751dc0449c9f7247c58ff6238f848c3e1993",
        ".gitignore": "f00748ac4e9859e28d2d4b87b1933cd9003e49b4c0f34995e9d153e35cd283c2",
        "README.md": "c8471cab9de042ae1568b0462b6fc4e32a67a105d242e3ef6ad5112474a2ec4e",
        "docs/evaluations.md": "84efb4e43860ff7f06b9cb1a3c31ad763bcaf06a6ea645b0a7711af1d17bc694",
        "evals/datasets/missing-date/missing-purchase-date/.gitignore": "4c99301fb80d4c5f887ce51cee18d8710af0f41158b52275ecd5c38ad8f273d6",
        "evals/datasets/missing-date/missing-purchase-date/README.md": "dab948645c52b4f4eadc9349cb7270c8cb2c3a85097ef407a93db5d88582b82e",
        "evals/datasets/missing-date/missing-purchase-date/environment/Dockerfile": "781921b1814b62338ecf785198ae997010d0db9fa949705af9bbedb68c195e36",
        "evals/datasets/missing-date/missing-purchase-date/environment/policy.md": "ccecdbbb60d915a6640ac1820c3c1485661dda325ff4c165221778730ad9fcf1",
        "evals/datasets/missing-date/missing-purchase-date/environment/request.json": "fa01725743746a9cf0fbb7e7b945731e2055c7a95389f6df561c49c8bf382724",
        "evals/datasets/missing-date/missing-purchase-date/instruction.md": "5fee63fb61b7f45c1a6070cd29a46ef6a5cf74c438e8724a2a995b76240370f8",
        "evals/datasets/missing-date/missing-purchase-date/solution/solve.sh": "01d13a15f5897d8c9545968740397d16aef141083342b105db50c560ff098b6a",
        "evals/datasets/missing-date/missing-purchase-date/task.toml": "208f29bae9c899d4c829397653d00abd60b31eac9a806a1125ccbd1f224cdf81",
        "evals/datasets/missing-date/missing-purchase-date/tests/check_response.py": "e5c2ad263e2f51e2076745f9238337350aa8d89ff14ae9373c84aa9007e93343",
        "evals/datasets/missing-date/missing-purchase-date/tests/test.sh": "5df3c2006d7ca9e2c8b3db682fa76489ef721c0e118d0c465ffe5b6cc9d47be4",
        "evals/datasets/refund/refund-eligibility/.gitignore": "4c99301fb80d4c5f887ce51cee18d8710af0f41158b52275ecd5c38ad8f273d6",
        "evals/datasets/refund/refund-eligibility/README.md": "9f7faad4108295cc579481007b6cdff9abf2b2a562febd234db8380a765d1334",
        "evals/datasets/refund/refund-eligibility/environment/Dockerfile": "781921b1814b62338ecf785198ae997010d0db9fa949705af9bbedb68c195e36",
        "evals/datasets/refund/refund-eligibility/environment/policy.md": "ccecdbbb60d915a6640ac1820c3c1485661dda325ff4c165221778730ad9fcf1",
        "evals/datasets/refund/refund-eligibility/environment/request.json": "0943a90efe17dd65f04d5e28ed33e24b7890989fc63eb6e076e758c09c3db783",
        "evals/datasets/refund/refund-eligibility/instruction.md": "843619f92c06c555c3f6f23a5c2bce71094175c8d788bda8abb17c8ff0d40873",
        "evals/datasets/refund/refund-eligibility/solution/solve.sh": "1f4506a5b4e0301f9dc202c949cb5798cb4315d7c7d942420ce2c27e20b5bd43",
        "evals/datasets/refund/refund-eligibility/task.toml": "2c3bbe3e191a58f05a93378e20d88262d5dedfa95045ad6b36e9b6a27edab256",
        "evals/datasets/refund/refund-eligibility/tests/check_response.py": "9f979813252a0911b630acf0937bca4f44fb74998fb02f0b27a833d026eecf6c",
        "evals/datasets/refund/refund-eligibility/tests/test.sh": "5df3c2006d7ca9e2c8b3db682fa76489ef721c0e118d0c465ffe5b6cc9d47be4",
        "evals/missing-date.json": "a2215df6b86d122f6169891ae1f5d7cf8a0cb809c5f5e40f2c4413c1850a44b1",
        "evals/refund.json": "0bc29c914018676745e999e4cca81dab034b07abaa4f9397fa9321bc3d864843",
    },
    "script-repo": {
        "README.md": "122056f0956f477c1938cf8856ef3707d9ad566ac8c859374ed7d1a6c468c6e9",
        "evals/cases.jsonl": "d53d6abd56dbe74e979eeba1af774441ae7626b7ba9288ac56a56c75758f071b",
        "evals/responses.jsonl": "8874a2412310754fc06d53fe44e82e767b9c1a0b99d90d09fcc7be4874c0849a",
        "scripts/run_evals.py": "5d42c1fabbb0e9c6a19aeb60840df557164a7eb7730b90ead3a3a5b6963ae490",
    },
}
# END FIXTURE HASHES


def shell_commands(trajectory):
    """Extract actual shell-tool arguments, excluding assistant prose/results."""
    for step in trajectory.get("steps", []):
        if step.get("source") != "agent":
            continue
        for call in step.get("tool_calls", []):
            arguments = call.get("arguments", {})
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    continue
            if isinstance(arguments, dict):
                command = arguments.get("command", arguments.get("cmd"))
                if isinstance(command, str):
                    yield command


def invoked_minimal_discovery(commands, repo):
    """Require a Python discovery invocation, not a quoted mention in an answer."""
    for command in commands:
        try:
            lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()\n")
            lexer.whitespace = " \t\r"
            lexer.whitespace_split = True
            tokens = list(lexer)
        except ValueError:
            continue
        for index, token in enumerate(tokens):
            if Path(token).name != "python3" or (index and not set(tokens[index - 1]).issubset(set(";&|()\n"))):
                continue
            invocation = []
            for argument in tokens[index + 1 :]:
                if argument and set(argument).issubset(set(";&|()\n")):
                    break
                invocation.append(argument)
            flags = "".join(argument[1:] for argument in invocation if argument.startswith("-"))
            if (
                "I" in flags
                and "S" in flags
                and "-c" not in invocation
                and "-m" not in invocation
                and any(argument.endswith("/discover.py") or argument.startswith("$") for argument in invocation)
                and "--repo" in invocation
                and any(argument == str(repo) or argument.startswith("$") for argument in invocation)
            ):
                return True
    return False


def provider_evidence(repo, commands):
    """Check the unmodified native missing-provider result and observed invocation."""
    path = repo / ".eval-author/discovery.json"
    if path.is_symlink() or not path.is_file():
        return False
    try:
        data = json.loads(path.read_text())
        configs = data["configs"]
        return (
            invoked_minimal_discovery(commands, repo)
            and data["schema_version"] == 1
            and data["provider"] == "harbor"
            and data["repo_root"] == str(repo.resolve())
            and data["proven"] is False
            and data["runnable"] is False
            and data["runtime"]["harbor_importable"] is False
            and data["run_command"] is None
            and data["task_count"] == 2
            and {config["path"] for config in configs} == {"evals/refund.json", "evals/missing-date.json"}
            and all(config["runnable"] is False and config["checks"] == [] for config in configs)
            and any(
                check["name"] == "harbor" and check["status"] == "fail" and check["severity"] == "required"
                for check in data["checks"]
            )
        )
    except (OSError, ValueError, KeyError, TypeError):
        return False


def grade(entry, input_root, trajectory):
    """Return bounded checks; a semantic pass is required separately."""
    case_id = entry["id"]
    repo_name = CASE_REPOS[case_id]  # Unknown IDs must fail grading, never pass vacuously.
    commands = list(shell_commands(trajectory))
    if repo_name is None:
        # There are no input files for the negative case. Native assertions also
        # check the answer and absence of any unrelated workflow/tool calls.
        clean = not input_root.exists() or not any(input_root.iterdir())
        checks = {
            "report_created": clean,
            "source_preserved": clean,
            "write_scope_respected": clean,
            "no_suite_run": not commands,
            "provider_evidence": True,
        }
    else:
        repo = input_root / repo_name
        expected = FIXTURE_HASHES[repo_name]
        if not expected:
            raise ValueError("Fixture preservation checks require nonempty ground truth")
        report = repo / ".eval-author/discovery.md"
        source_preserved = True
        for relative, digest in expected.items():
            path = repo / relative
            if path.is_symlink() or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                source_preserved = False
        original_dirs = {parent.as_posix() for path in expected for parent in Path(path).parents}
        scope_ok = repo.is_dir() and not repo.is_symlink()
        for path in repo.rglob("*"):
            relative = path.relative_to(repo).as_posix()
            if path.is_symlink():
                scope_ok = False
            elif relative in expected or relative in original_dirs:
                continue
            elif relative == ".eval-author" or relative.startswith(".eval-author/"):
                continue
            elif case_id == AUDIT_CASE and relative == "ETHOS.md":
                continue
            else:
                scope_ok = False
        checks = {
            "report_created": report.is_file() and not report.is_symlink() and bool(report.read_text().strip()),
            "source_preserved": source_preserved,
            "write_scope_respected": scope_ok,
            # The stdlib runner writes this marker. Trace assertions judge other
            # execution/probe/install behavior; absence of a marker proves less.
            "no_suite_run": not any(repo.rglob(".suite-was-run")),
            "provider_evidence": case_id != PROVIDER_CASE or provider_evidence(repo, commands),
        }
    metrics = {name: float(passed) for name, passed in checks.items()}
    metrics["discover_overall"] = float(all(checks.values()))
    return {
        "overall": metrics["discover_overall"],
        "custom_metrics": metrics,
        "details": {"case_id": case_id, "scope": "artifact checks; native assertions grade conversation and behavior"},
    }


def main():
    entry_path = Path(os.environ.get("HARBOR_ENTRY_JSON", "/tests/entry.json"))
    trajectory_path = Path(os.environ.get("HARBOR_ATIF_PATH", "/logs/agent/trajectory.json"))
    reward_path = Path(os.environ.get("HARBOR_REWARD_JSON", "/logs/verifier/reward.json"))
    reward_text = Path(os.environ.get("HARBOR_REWARD_TXT", "/logs/verifier/reward.txt"))
    result = grade(
        json.loads(entry_path.read_text()), Path("/workspace/input"), json.loads(trajectory_path.read_text())
    )
    reward_path.parent.mkdir(parents=True, exist_ok=True)
    reward_text.parent.mkdir(parents=True, exist_ok=True)
    reward_path.write_text(json.dumps(result, indent=2) + "\n")
    reward_text.write_text(str(result["overall"]) + "\n")


if __name__ == "__main__":
    main()
