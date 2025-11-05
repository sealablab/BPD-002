# Codex Support Guide

**Audience:** Codex agents (GPT-5 based) collaborating within BPD-002  
**Relation:** Supplements `.claude/shared/CONTEXT_MANAGEMENT.md`; keep both in sync.

---

## Purpose

Equip Codex with a reusable navigation routine that mirrors the Progressive Disclosure Architecture (PDA) already defined for Claude agents. The goal is to minimize context bloat, maximize reuse of authoritative docs, and keep Codex-specific workflows repeatable across sessions.

---

## Core Principles

1. **Honor Tiered Loading** — Follow the Tier 1 → Tier 2 → Tier 3 sequence documented in `.claude/shared/CONTEXT_MANAGEMENT.md`. Never skip Tier 1.
2. **Promote Authoritative Sources** — When citing implementation details, point back to the four primary `llms.txt` files listed in the root `llms.txt` (lines 120–177).
3. **Minimize Guesswork** — If data is not in the loaded context, pause and load the relevant `CLAUDE.md` or source file rather than inferring.
4. **Stay Component-Scoped** — Work inside the component owning the truth (e.g., probe specs live in `libs/riscure-models`, not in drivers).
5. **Surface Gaps Early** — Ask for clarification whenever a workflow or requirement is ambiguous; Codex is expected to prompt for missing detail.

---

## Standard Codex Session Flow

1. **Initialize Context**
   - Load root `llms.txt`.
   - Review `.claude/shared/CONTEXT_MANAGEMENT.md` to reaffirm the tier strategy.
   - Record any TODOs or open questions discovered in those files.
2. **Component Discovery**
   - Identify the component(s) in scope via the “Repository Structure” table in `llms.txt`.
   - Load each relevant component `llms.txt` before reading other material.
3. **Design Readiness**
   - When design guidance is required, escalate to the matching `CLAUDE.md`.
   - Capture key constraints, required data models, and integration points in the working notes.
4. **Implementation Prep**
   - Load only the specific source/test files needed for the active change.
   - Reference voltage/type safety rules from `docs/migration/VOLTAGE_TYPE_SYSTEM_DESIGN.md` when touching hardware-facing code.
5. **Execution & Validation**
   - Implement or refactor code in the minimal surface area.
   - Run targeted tests (`pytest`, CocoTB, Forge codegen scripts) scoped to the change.
6. **handoff Summary**
   - Summarize modifications with file+line references.
   - Suggest follow-up tests or docs updates if they fall outside the current scope.

---

## Codex-Specific Developer Workflows

### A. Rapid Driver Enhancements

1. Load:
   - `bpd/bpd-drivers/llms.txt`
   - `bpd/bpd-core/CLAUDE.md` (protocol details)
   - `libs/riscure-models/CLAUDE.md` (if electrical specs required)
2. Checklist:
   - Extend or implement `FIProbeInterface`.
   - Update driver registry entries.
   - Add or adjust tests in `bpd/bpd-drivers/tests/`.
3. Validation:
   - Run targeted `pytest` modules.
   - Confirm `validate_probe_moku_compatibility()` still passes with new capabilities.

### B. Forge Codegen Extensions

1. Load:
   - `tools/forge-codegen/llms.txt`
   - `tools/forge-codegen/CLAUDE.md`
   - `.claude/shared/ARCHITECTURE_OVERVIEW.md` (for cross-component impacts)
2. Checklist:
   - Modify type definitions or templates in isolation.
   - Regenerate fixtures/examples.
   - Run `uv run python tests/run.py` for impacted components.

### C. VHDL Interface Adjustments

1. Load:
   - `bpd/bpd-vhdl/llms.txt`
   - `bpd/bpd-vhdl/CLAUDE.md`
   - `libs/forge-vhdl/CLAUDE.md` for supporting utilities/tests.
2. Checklist:
   - Update `fi_probe_interface.vhd` or associated packages.
   - Ensure CocoTB progressive tests cover changes (`tests/run.py` usage).
   - Verify voltage domains align with the Forge packages.

### D. Cross-Component Integration

1. Combine relevant Tier 1 and Tier 2 docs for each component involved.
2. Maintain a scratchpad of assumptions; validate them by citing file+line references.
3. Use `.claude/agents/` prompts for orchestration patterns if coordination is required.

> **Workflow companion:** See `.claude/workflows/codex-session-bootstrap.md` for a step-by-step session checklist.

---

## Communication Expectations

- **Summaries** — Lead with actionable findings, then context.
- **File References** — Use workspace-relative paths with line numbers (`path/to/file.py:42`).
- **Follow-Up Questions** — Ask as soon as missing information blocks progress.
- **Token Stewardship** — Note when Tier 2/Tier 3 loading may exceed practical context budgets.

---

## Quick Reference Index

- Navigation primer: `llms.txt`
- Context strategy: `.claude/shared/CONTEXT_MANAGEMENT.md`
- Architecture overview: `.claude/shared/ARCHITECTURE_OVERVIEW.md`
- Voltage type system: `docs/migration/VOLTAGE_TYPE_SYSTEM_DESIGN.md`
- Forge testing guidance: `libs/forge-vhdl/CLAUDE.md`
- Workflow guide: `WORKFLOW_GUIDE.md`

Keep this file synchronized with updates to the Tier 1/Tier 2 documentation. If the PDA structure evolves, update both this guide and the root `llms.txt` “Authoritative Sources” section in the same change.
