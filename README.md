# BPD-002: Basic Probe Driver

Multi-vendor probe integration framework for Moku platform fault injection development.

## Overview

**BPD-002** provides a vendor-agnostic probe driver framework that lets you integrate electromagnetic (EMFI), laser, RF, and voltage glitching probes with the full Moku FPGA platform family (Go, Lab, Pro, Delta). The architecture is composable:

- Python core (`bpd-core`) defines probe interfaces, validation, and registry tooling.
- Driver collection (`bpd-drivers`) implements probe-specific behavior (DS1120A today, more planned).
- VHDL layer (`bpd-vhdl`) delivers a reusable FPGA interface for probe control.
- Upstream libraries (`libs/`) capture authoritative platform and probe specifications.
- Tooling (`tools/`) automates register packing and VHDL generation via the Forge stack.

Current release: **v0.1.0** with DS1120A EMFI reference support. Overall workspace architecture is v2.0.0, featuring a flat split between `tools/` and `libs/`.

---

## Progressive Disclosure Navigation

This repository is organized around a repeatable three-tier documentation pattern so AI assistants keep context lean and authoritative.

### Authoritative Sources of Truth

Start with these Tier 1 quick-reference files:

- `llms.txt` (this repository) — high-level architecture, workflows, and navigation map.
- `tools/forge-codegen/llms.txt` — 23-type register system and YAML→VHDL workflow.
- `libs/forge-vhdl/llms.txt` — reusable VHDL utilities and CocoTB testing patterns.
- `libs/moku-models/llms.txt` — Moku platform specifications and configuration models.
- `libs/riscure-models/llms.txt` — DS1120A probe specification and wiring safety data.

> **Always load Tier 1 before escalating.**

### Three-Tier Context Model

- **Tier 1** — `llms.txt` quick references (≤1 k tokens): orientation, component map, entry points.
- **Tier 2** — `CLAUDE.md` deep dives (2–5 k tokens): design rationale, integration recipes, pitfalls.
- **Tier 3** — Source, tests, specialized docs: implementation details only when coding/debugging.

See `.claude/shared/CONTEXT_MANAGEMENT.md` for full strategy, decision trees, and anti-patterns.

### New Context Window Checklist

1. Load root `llms.txt` (orientation, authoritative pointers).
2. Pull the component-level `llms.txt` for the area you are touching.
3. Escalate to the matching `CLAUDE.md` only if you need design detail.
4. Inspect code, tests, or agent prompts once you are actively implementing.

This repeatable pattern keeps ≥90 % of the token budget available for real work.

---

## Repository Layout

| Area | Purpose | Tier 1 Reference | Tier 2 Deep Dive |
|------|---------|-----------------|------------------|
| `bpd/bpd-core/` | Probe interface protocols, registry, safety validation | `bpd/bpd-core/llms.txt` | `bpd/bpd-core/CLAUDE.md` |
| `bpd/bpd-drivers/` | Probe-specific drivers (DS1120A reference) | `bpd/bpd-drivers/llms.txt` | `bpd/bpd-drivers/CLAUDE.md` |
| `bpd/bpd-vhdl/` | Vendor-agnostic VHDL control FSM | `bpd/bpd-vhdl/llms.txt` | `bpd/bpd-vhdl/CLAUDE.md` |
| `libs/moku-models/` | Moku platform specs, deployment models | `libs/moku-models/llms.txt` | `libs/moku-models/CLAUDE.md` |
| `libs/riscure-models/` | Riscure probe specs and wiring validation | `libs/riscure-models/llms.txt` | `libs/riscure-models/CLAUDE.md` |
| `libs/forge-vhdl/` | Shared VHDL packages, CocoTB progressive tests | `libs/forge-vhdl/llms.txt` | `libs/forge-vhdl/CLAUDE.md` |
| `tools/forge-codegen/` | YAML→VHDL generator + 23-type register system | `tools/forge-codegen/llms.txt` | `tools/forge-codegen/CLAUDE.md` |
| `.claude/` | Agent prompts, coordination patterns, PDA governance | `llms.txt` & `.claude/shared/CONTEXT_MANAGEMENT.md` | Component prompt files |

### Component Highlights

- **`bpd-core`** — Defines `FIProbeInterface`, `ProbeCapabilities`, registry helpers, and `validate_probe_moku_compatibility()` for voltage safety.
- **`bpd-drivers`** — Implements DS1120A probe driver, planned laser/RF/voltage-glitching drivers follow the same protocol.
- **`bpd-vhdl`** — `fi_probe_interface.vhd` FSM handles arming, pulse activation, cooldown, and status flags with configurable generics.
- **`libs/moku-models`** — Pydantic models for platform metadata, routing validation, deployment serialization.
- **`libs/riscure-models`** — Probe electrical specifications, port voltage ranges, tip catalog, compatibility checks.
- **`libs/forge-vhdl`** — Voltage-domain packages (3.3 V, 5 V, ±5 V), LUT utilities, clock divider, CocoTB progressive testing harness.
- **`tools/forge-codegen`** — Register mapper with 23 strongly typed domains, YAML validation models, and Jinja2 templates for VHDL generation.

---

## Setup & Environment

```bash
./setup.sh                # Initialize submodules, create virtualenv, install deps
source .venv/bin/activate # Activate virtualenv
pytest                    # Run repository test suite
```

Requirements:

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) for dependency management
- Git with submodule support

---

## Common Workflows

### Create a New Probe Driver
1. Load `bpd/bpd-drivers/llms.txt` (Tier 1).
2. Review `bpd/bpd-drivers/CLAUDE.md` for driver patterns and DS1120A reference.
3. Implement driver following `FIProbeInterface`; validate with `bpd-core`.

### Validate Probe Against a Moku Platform
1. Load `bpd/bpd-core/llms.txt`.
2. Use `validate_probe_moku_compatibility()` with `moku-models` constants.
3. Reference `libs/riscure-models` for probe voltage ranges if needed.

### Integrate VHDL Interface
1. Load `bpd/bpd-vhdl/llms.txt` for interface overview.
2. Review `fi_probe_interface.vhd` and corresponding tests.
3. Use Forge codegen + forge-vhdl utilities to integrate with instrument firmware.

### Generate VHDL from YAML Spec
1. Load `tools/forge-codegen/llms.txt`.
2. Prepare YAML spec; run `python -m forge_codegen.generator.codegen spec.yaml --output-dir generated/`.
3. Leverage `libs/forge-vhdl` packages for voltage domain conversions.

### Wiring & Safety Checks
1. Load `libs/moku-models/llms.txt` to understand platform port characteristics.
2. Load `libs/riscure-models/llms.txt` for probe port ranges.
3. Validate wiring manually or via helper utilities before deployment.

---

## Additional Documentation

- `.claude/shared/CONTEXT_MANAGEMENT.md` — Full PDA strategy, anti-patterns, decision trees.
- `.claude/shared/ARCHITECTURE_OVERVIEW.md` — Architecture v2.0 summary.
- `docs/migration/VOLTAGE_TYPE_SYSTEM_DESIGN.md` — Voltage domain safety design.
- `docs/migration/voltage_types_reference.py` — Python reference for voltage type conversions.
- `ARCHITECTURE_V2_COMPLETE.md` — Migration history.
- `WORKFLOW_GUIDE.md` — Process guidance across teams.

---

## Contributing

1. Follow PDA navigation (Tier 1 → Tier 2 → Tier 3).
2. Keep new documentation aligned with llms/CLAUDE hierarchy.
3. Update relevant quick references when changing interfaces or workflows.
4. Run `pytest` (and CocoTB tests where applicable) before submitting changes.

---

**Status:** v0.1.0  
**Architecture:** v2.0.0 (tools/libs split)  
**License:** MIT
