# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Check real Make/pre-commit behavior without relying on Git's editor scratch file."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SIGNED_MESSAGE = "docs: fixture\n\nSigned-off-by: Example Contributor <example@example.com>\n"
UNSIGNED_MESSAGE = "docs: fixture without sign-off\n"


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True)


@pytest.fixture
def repository(tmp_path, monkeypatch):
    repo = tmp_path / "repository"
    repo.mkdir()
    git(repo, "init", "--quiet")
    git(repo, "config", "user.name", "Example Contributor")
    git(repo, "config", "user.email", "example@example.com")
    git(repo, "config", "commit.gpgsign", "false")
    git(repo, "config", "core.hooksPath", str(tmp_path / "no-hooks"))
    for name in ("Makefile", ".pre-commit-config.yaml", "pyproject.toml", "uv.lock"):
        shutil.copyfile(ROOT / name, repo / name)
    git(repo, "add", ".")

    # Reuse the test environment; the hook is local and needs no downloads.
    monkeypatch.setenv("UV_PROJECT_ENVIRONMENT", sys.prefix)
    monkeypatch.setenv("UV_NO_SYNC", "1")
    monkeypatch.setenv("UV_OFFLINE", "1")
    monkeypatch.setenv("UV_CACHE_DIR", str(tmp_path / "uv-cache"))
    monkeypatch.setenv("PRE_COMMIT_HOME", str(tmp_path / "pre-commit-cache"))
    return repo


def check(repo, message_file=None):
    command = ["make", "commit-check"]
    if message_file is not None:
        command.append(f"COMMIT_MSG={message_file}")
    return subprocess.run(command, cwd=repo, capture_output=True, text=True)


@pytest.mark.parametrize(
    "head_message,scratch_message,passes",
    [
        (SIGNED_MESSAGE, None, True),
        (SIGNED_MESSAGE, UNSIGNED_MESSAGE, True),
        (UNSIGNED_MESSAGE, SIGNED_MESSAGE, False),
        (UNSIGNED_MESSAGE, None, False),
    ],
)
def test_default_checks_head_not_editor_file(repository, head_message, scratch_message, passes):
    git(repository, "commit", "--quiet", "-m", head_message)
    scratch = repository / ".git" / "COMMIT_EDITMSG"
    if scratch_message is None:
        scratch.unlink()
    else:
        scratch.write_text(scratch_message)

    result = check(repository)

    assert (result.returncode == 0) is passes, result.stdout + result.stderr
    assert "Check commit is signed off (DCO)" in result.stdout
    if scratch_message is None:
        assert not scratch.exists()
    else:
        assert scratch.read_text() == scratch_message


@pytest.mark.parametrize("message,passes", [(SIGNED_MESSAGE, True), (UNSIGNED_MESSAGE, False)])
def test_prepared_message_overrides_head(repository, tmp_path, message, passes):
    git(repository, "commit", "--quiet", "-m", UNSIGNED_MESSAGE if passes else SIGNED_MESSAGE)
    prepared = tmp_path / "prepared message.txt"
    prepared.write_text(message)

    result = check(repository, prepared)

    assert (result.returncode == 0) is passes, result.stdout + result.stderr
    assert prepared.read_text() == message


def test_default_works_in_linked_worktree(repository, tmp_path):
    git(repository, "commit", "--quiet", "-m", SIGNED_MESSAGE)
    worktree = tmp_path / "linked worktree"
    git(repository, "worktree", "add", "--detach", str(worktree))
    assert (worktree / ".git").is_file()

    result = check(worktree)

    assert result.returncode == 0, result.stdout + result.stderr
