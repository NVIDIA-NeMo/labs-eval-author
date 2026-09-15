# Migration provenance

Imported on 2026-09-15 from
[`NVIDIA-NeMo/nemo-platform`, `plugins/nemo-eval-author`](https://github.com/NVIDIA-NeMo/nemo-platform/tree/3ac3d6adbfc76ad2f93a9f9713e0f1753fa3105b/plugins/nemo-eval-author).

- Source branch: `main`, fetched directly from GitHub before extraction.
- Source commit: `3ac3d6adbfc76ad2f93a9f9713e0f1753fa3105b`.
- Recent merges included:
  - [#1943: help users build a working starter suite](https://github.com/NVIDIA-NeMo/nemo-platform/pull/1943).
  - [#2066: authoring loop, per-check proof, and bounded trace-environment repair](https://github.com/NVIDIA-NeMo/nemo-platform/pull/2066).

The source directory was extracted with `git archive` at this exact commit and
placed at the repository root. No monorepo Git history was imported.
All skill files, scripts, schemas, examples, templates, and tests are unchanged.

## Standalone repository changes

- Renamed the non-installable uv project to `labs-eval-author` and added a
  development dependency group and lockfile. Harbor is pinned to `0.20.0`,
  matching the source monorepo lockfile. MCP stays on the source-compatible
  1.x API; MCP 2.x renames fields used by the imported integration tests.
- Preserved the source Ruff rules and 120-character line length.
- Updated development instructions, test paths, and the external Experimentalist link.
- Added CI for Python 3.12 and 3.13 and ignored local runtime artifacts.
- Included the source Apache-2.0 license and applicable root notice. No other
  monorepo components or fixture corpus data were copied.
