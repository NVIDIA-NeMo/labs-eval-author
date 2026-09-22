#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Read-only validation bridge, run with the user's Gym Python (v0.6.0+)."""

from __future__ import annotations

import argparse
import contextlib
import importlib
import importlib.metadata
import io
import json
import os
from pathlib import Path


def inspect(repo: Path, config: Path, manifest: Path | None) -> dict:
    # Gym stays isolated in its own interpreter; it is not a mandatory Harbor dependency.
    gym = importlib.import_module("nemo_gym")
    global_config = importlib.import_module("nemo_gym.global_config")
    OmegaConf = importlib.import_module("omegaconf").OmegaConf
    GlobalConfigDictParser = global_config.GlobalConfigDictParser
    GlobalConfigDictParserConfig = global_config.GlobalConfigDictParserConfig

    runtime = {"checked": True, "version": importlib.metadata.version("nemo-gym")}
    os.environ[gym.NEMO_GYM_EXTRA_ROOTS_ENV_VAR_NAME] = str(repo)
    os.chdir(repo)
    if manifest:
        validate_environment = importlib.import_module("nemo_gym.environment.validation").validate_environment

        evidence = validate_environment(manifest, config, sync=False).to_dict()
        return {
            "status": "manifest_validated",
            "runtime": runtime,
            "evidence": evidence,
            "runtime_readiness": "not_checked",
            "execution": "not_run",
        }
    parser = GlobalConfigDictParser()
    resolved = parser.parse(
        GlobalConfigDictParserConfig(
            initial_global_config_dict=OmegaConf.create({"config_paths": [str(config)]}),
            skip_load_from_cli=True,
            skip_load_from_dotenv=True,
            offline=True,
        )
    )
    servers = parser.filter_for_server_instance_configs(resolved)
    return {
        "status": "config_validated",
        "runtime": runtime,
        "components": [{"name": server.name, "role": server.SERVER_TYPE} for server in servers],
        "runtime_readiness": "not_checked",
        "execution": "not_run",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    repo = args.repo.resolve()
    config = (repo / args.config).resolve()
    manifest = (repo / args.manifest).resolve() if args.manifest else None
    try:
        for path in (config, manifest):
            if path is not None and not path.is_relative_to(repo):
                raise ValueError("configuration must belong to the selected repository")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            report = inspect(repo, config, manifest)
    except ImportError:
        report = {"status": "unavailable", "error": "Gym v0.6.0+ is required in the selected interpreter"}
    except Exception as exc:
        # Do not echo interpolated configuration values, credentials, or dataset records.
        report = {
            "status": "failed",
            "error_type": type(exc).__name__,
            "error": "Gym rejected this configuration; inspect locally with gym env validate",
        }
    print(json.dumps(report))
    return 0 if report["status"] in {"manifest_validated", "config_validated"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
