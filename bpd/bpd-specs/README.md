# BPD Specs Workspace

This directory keeps the forge-codegen sources and generated artifacts for BPD-002.

- `basic_probe_driver.yaml` — heavily documented register specification consumed by forge-codegen.
- `generated/` — output VHDL produced by running `uv run python -m forge_codegen.generator.codegen` against the spec (shim is overwritten on each run; main template is kept if it already exists).

Run codegen from the repository root:

```bash
UV_CACHE_DIR=.uv-cache PYTHONPATH=tools/forge-codegen \
uv run python -m forge_codegen.generator.codegen \
    bpd/bpd-specs/basic_probe_driver.yaml \
    --output-dir bpd/bpd-specs/generated \
    --template-dir tools/forge-codegen/forge_codegen/templates
```

All paths are relative to the repo root so the command works regardless of the current branch.
