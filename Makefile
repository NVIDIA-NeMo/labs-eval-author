# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

.PHONY: update-copyright-headers
update-copyright-headers: ## Add the NVIDIA Apache-2.0 header to NVIDIA-authored files
	uv run --locked python tools/check_copyright_headers.py --fix-nvidia

.PHONY: check-copyright-headers
check-copyright-headers: ## Check copyright and license headers
	uv run --locked python tools/check_copyright_headers.py

.PHONY: update-licenses
update-licenses: ## Update the OSV dependency license disclosures
	uv run --locked python tools/generate_third_party_licenses.py

.PHONY: check-licenses
check-licenses: ## Check that the third-party dependency license disclosures are current
	uv run --locked python tools/generate_third_party_licenses.py --check

COMMIT_MSG ?=

.PHONY: hooks
hooks: ## Install the DCO commit-message hook
	uv run --locked pre-commit install

.PHONY: commit-check
commit-check: ## Check HEAD's message (override COMMIT_MSG for a prepared message)
	@set -eu; \
	message_file="$(COMMIT_MSG)"; \
	if [ -z "$$message_file" ]; then \
		message_file=$$(mktemp); \
		trap 'rm -f "$$message_file"' EXIT; \
		git log -1 --format=%B HEAD > "$$message_file"; \
	fi; \
	uv run --locked pre-commit run --hook-stage commit-msg --commit-msg-filename "$$message_file"
