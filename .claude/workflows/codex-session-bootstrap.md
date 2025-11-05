# Codex Session Bootstrap

**Purpose:** Standard operating workflow for Codex (GPT-5) agents working in BPD-002  
**Allies:** `.claude/shared/CODEX_SUPPORT.md`, `.claude/shared/CONTEXT_MANAGEMENT.md`

---

## 0. Preconditions

- Ensure you are on an approved branch (create `feature/*` when starting new work).
- Confirm shell, sandbox, and approval policies before running commands.
- Have `uv` and Git submodules initialized (`./setup.sh`) if you plan to run tests or codegen.

---

## 1. Context Initialization (Tier 1)

1. Load root `llms.txt` for project map and authoritative sources.
2. Review `.claude/shared/CODEX_SUPPORT.md` for Codex-specific guidance.
3. If this is the first task in a session, skim `.claude/shared/CONTEXT_MANAGEMENT.md` to refresh the PDA pattern.

**Deliverables:** Scratchpad with relevant components and Tier 2 targets.

---

## 2. Component Scoping

For each directory involved (e.g., `bpd/bpd-core`, `libs/moku-models`):

1. Load the component’s `llms.txt`.
2. Note required `CLAUDE.md` files for escalation.
3. Capture integration touchpoints (registry functions, validation helpers, VHDL modules).

**Tip:** The BPD application exposes three `llms.txt` siblings under `bpd/` (core/drivers/vhdl); keep them synchronized and reference them explicitly in summaries.

---

## 3. Design Escalation (Tier 2)

Only when design or architectural context is needed:

1. Load the relevant `CLAUDE.md`.
2. Extract constraints, workflows, and pitfalls.
3. Cross-reference `.claude/shared/ARCHITECTURE_OVERVIEW.md` if the change spans multiple subsystems.

**Output:** Clear list of requirements before touching code.

---

## 4. Implementation Planning

1. Identify exact files/tests to modify (Tier 3).
2. Plan validation steps:
   - Python: `pytest`, targeted modules.
   - VHDL: CocoTB progressive tests (`uv run python libs/forge-vhdl/tests/run.py ...`).
   - Codegen: `python -m forge_codegen.generator.codegen`.
3. Document any dependencies (e.g., needing updated probe specs from `libs/riscure-models`).

---

## 5. Execution

1. Edit code with minimal surface area.
2. Keep comments high-signal; align with existing style.
3. Update `llms.txt` or `CLAUDE.md` when new workflows/exports are added.
4. Run planned tests; capture summaries, not raw logs.

---

## 6. Handoff Summary

Your final response should:

- Lead with the change impact and component references (`path/to/file:line`).
- Mention newly consulted Tier 2 docs or tests run.
- Suggest next actions (tests, review, deployment) when relevant.
- Flag unresolved questions or assumptions.

---

## 7. Maintenance Hooks

- Sync changes with `.claude/shared/CODEX_SUPPORT.md` when workflows evolve.
- If documentation diverges, update component `llms.txt` so Tier 1 remains authoritative.
- Avoid duplicating content already in `CLAUDE.md`; link instead.

---

Following this workflow keeps Codex aligned with the CLAUDE-driven PDA architecture while preserving repeatable, low-token navigation across the monorepo.
