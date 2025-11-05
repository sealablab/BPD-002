# Sub-Agent Architecture Proposal

**Date:** 2025-11-05
**Session:** session/2025-11-05-integration-testing
**Status:** 📋 Proposal (To be implemented after dry-run)

---

## Overview

The YAML → FSM → CocoTB workflow naturally decomposes into three specialized sub-agents, each with distinct domain expertise and minimal context overlap. This document proposes the structure and placement of these agents.

---

## Proposed Agent Structure

### Agent Placement (Following Existing Pattern)

**Location:** `.claude/agents/<agent-name>/agent.md`

**Existing Agents:**
- `.claude/agents/deployment-orchestrator/agent.md`
- `.claude/agents/hardware-debug/agent.md`

**New Agents (Proposed):**
```
.claude/agents/
├── python-register-alignment/
│   └── agent.md
├── vhdl-fsm-implementation/
│   └── agent.md
└── cocotb-integration-test/
    └── agent.md
```

---

## Agent P1: Python Register Alignment

**Directory:** `.claude/agents/python-register-alignment/`

**Purpose:** Align Python driver layer with YAML register specification

### Domain Expertise
- **Primary:** Python, register definitions, validation logic
- **Secondary:** YAML parsing, type conversions
- **Minimal:** VHDL awareness (conceptual register → hardware mapping only)

### Knowledge Requirements
- **Standards:** PEP-8, type hints, dataclasses
- **Libraries:** pydantic (validation), PyYAML (parsing)
- **Structure:** bpd-core, bpd-drivers, bpd-examples layout
- **Concepts:** Register fields, voltage/timing units, validation ranges

### Input Contract
- **Required:**
  - `bpd/bpd-specs/basic_probe_driver.yaml` (source of truth)
  - Existing Python code in:
    - `bpd/bpd-core/`
    - `bpd/bpd-drivers/`
    - `bpd/bpd-examples/`

### Output Contract
- **Delivers:**
  - Updated Python register definitions matching YAML
  - Validation logic for all 13 register fields
  - Unit conversion helpers (mV, ns, μs, s)
  - Updated examples demonstrating new fields

### Exit Criteria
- [ ] All 13 YAML register fields have Python accessors
- [ ] Voltage/timing ranges validated per YAML spec
- [ ] No references to obsolete register fields
- [ ] Python tests pass (if they exist)
- [ ] Code ready for VHDL backend integration

### Common Kinks to Watch For
- **Kink:** Naming mismatches (Python snake_case vs YAML kebab-case)
- **Kink:** Unit conversion confusion (when to convert vs pass through)
- **Kink:** Missing validation (ranges not enforced)

### Handoff to P2
- **Commit:** P1-aligned Python code
- **Document:** Any register field questions/ambiguities
- **Provide:** Summary of Python API for VHDL team

---

## Agent P2: VHDL FSM Implementation

**Directory:** `.claude/agents/vhdl-fsm-implementation/`

**Purpose:** Implement forge-vhdl compliant FSM from YAML specification

### Domain Expertise
- **Primary:** VHDL, FSM design, forge-vhdl standards
- **Secondary:** Register interface wiring, clock domain reasoning
- **Minimal:** CustomInstrument wrapper (port structure only)

### Knowledge Requirements
- **Standards:**
  - forge-vhdl coding standards (CRITICAL: `std_logic_vector` states, NOT enums)
  - Port order conventions
  - Signal naming prefixes (`ctrl_`, `cfg_`, `stat_`, `dbg_`)
- **Tools:** GHDL (compilation check), Vivado/synthesis awareness
- **Patterns:**
  - FSM state machines (state register vs next-state logic)
  - Counter/timeout logic (multiple time bases)
  - Comparator logic (monitoring thresholds)
  - Unit conversions (mV, ns, μs, s → hardware values)
- **Components:** `fsm_observer.vhd` integration

### Input Contract
- **Required:**
  - `bpd/bpd-specs/basic_probe_driver.yaml` (register spec)
  - `bpd/bpd-specs/generated/basic_probe_driver_custom_inst_shim.vhd` (register interface)
  - `bpd/bpd-specs/generated/basic_probe_driver_custom_inst_main.vhd` (register main)
  - `libs/forge-vhdl/CLAUDE.md` (authoritative standards)
  - `libs/forge-vhdl/docs/VHDL_CODING_STANDARDS.md` (detailed rules)
  - `libs/forge-vhdl/vhdl/debugging/fsm_observer.vhd` (FSM observer component)
- **Optional:**
  - CustomInstrument wrapper spec (for port compatibility)
  - Existing `fi_probe_interface.vhd` (for reference, but STALE)

### Output Contract
- **Delivers:**
  - `bpd/bpd-vhdl/src/fi_probe_interface.vhd` (FSM implementation)
  - FSM following forge-vhdl standards:
    - `std_logic_vector(5 downto 0)` state encoding
    - All 13 register fields wired
    - Timeout/counter logic for multiple time bases
    - Monitoring comparator logic
    - Safety interlocks
  - `fsm_observer.vhd` instantiation
  - Documentation of design decisions

### Exit Criteria
- [ ] FSM compiles with GHDL (no errors)
- [ ] All forge-vhdl coding standards followed
- [ ] All 13 YAML register fields implemented
- [ ] Clock domain and timing verified
- [ ] Unit conversions documented
- [ ] Ready for CocoTB test harness

### Common Kinks to Watch For
- **Kink:** State encoding with enums (FORBIDDEN - use std_logic_vector)
- **Kink:** Unit conversion errors (clock cycles vs real time)
- **Kink:** Counter bit widths (ensure sufficient range)
- **Kink:** Missing `when others` in case statements
- **Kink:** Port order violations

### Handoff to P3
- **Commit:** P2-aligned VHDL FSM
- **Document:** State encoding, counter widths, design decisions
- **Provide:** Entity port list for test harness wiring

---

## Agent P3: CocoTB Integration Test

**Directory:** `.claude/agents/cocotb-integration-test/`

**Purpose:** Create progressive test suite validating full system

### Domain Expertise
- **Primary:** CocoTB, GHDL, forge-vhdl progressive testing
- **Secondary:** VHDL (reading), CustomInstrument wrapper
- **Minimal:** Python (basic test scripting)

### Knowledge Requirements
- **Standards:**
  - forge-vhdl progressive testing (P1: <20 lines, P2: <50 lines, P3: <100 lines)
  - GHDL output filtering (AGGRESSIVE mode)
  - CocoTB type constraints (NO `real`, `boolean`, `time`)
- **Tools:**
  - CocoTB API
  - GHDL simulator
  - pytest runner
  - `ghdl_output_filter.py`
- **Patterns:**
  - Progressive test structure (P1/P2/P3 modules)
  - Test base class (`test_base.py`)
  - Constants files
  - Setup/teardown (clock, reset)
- **Components:**
  - CustomInstrument wrapper (test harness)
  - forge-vhdl test utilities

### Input Contract
- **Required:**
  - `bpd/bpd-vhdl/src/fi_probe_interface.vhd` (FSM from P2)
  - `bpd/bpd-specs/generated/*.vhd` (register interface)
  - `bpd/bpd-specs/basic_probe_driver.yaml` (for test values)
  - `libs/forge-vhdl/CLAUDE.md` (testing standards)
  - `libs/forge-vhdl/tests/test_base.py` (base class)
  - `libs/forge-vhdl/scripts/ghdl_output_filter.py` (output filter)
  - **CustomInstrument wrapper spec** (⚠️ KINK #2: Find this!)

### Output Contract
- **Delivers:**
  - `bpd/bpd-vhdl/tests/fi_probe_interface_tests/` directory
    - `fi_probe_interface_constants.py` (register addresses, test values)
    - `P1_fi_probe_interface_basic.py` (2-4 essential tests, <20 lines)
    - `P2_fi_probe_interface_intermediate.py` (5-10 tests, <50 lines)
    - `P3_fi_probe_interface_comprehensive.py` (15-25 tests, <100 lines)
  - Test harness wrapping FSM + register interface + CustomInstrument
  - Validation of Python → Register → FSM → Hardware flow

### Exit Criteria
- [ ] P1 tests passing (<20 line output)
- [ ] GHDL filter configured (AGGRESSIVE mode)
- [ ] Test structure follows forge-vhdl conventions
- [ ] All 13 register fields tested
- [ ] FSM state transitions validated
- [ ] Timeout/monitoring logic verified
- [ ] Ready for hardware deployment

### Common Kinks to Watch For
- **Kink:** CocoTB type access errors (`real`, `boolean` not accessible)
- **Kink:** P1 output exceeds 20 lines (too verbose)
- **Kink:** Missing GHDL filter (output overwhelming)
- **Kink:** Test wrapper doesn't match CustomInstrument spec
- **Kink:** Register address confusion

### Handoff (Session Complete)
- **Commit:** P3-complete test suite
- **Document:** Test coverage, findings, automation recommendations
- **Provide:** Summary in `DRY-RUN-FINDINGS.md`

---

## Agent Orchestration

### Sequential Workflow

```
User
  ↓
[P1: Python Register Alignment]
  ↓ (commit, close window, reopen)
[P2: VHDL FSM Implementation]
  ↓ (commit, close window, reopen)
[P3: CocoTB Integration Test]
  ↓
Done
```

### Phase Transition Protocol

**After Each Agent:**
1. Agent completes work
2. Commits with phase-specific message
3. Updates `DRY-RUN-FINDINGS.md` with any kinks
4. User closes Claude Code window
5. User opens fresh window
6. Next agent reads:
   - `SESSION-HANDOFF-2025-11-05.md` (context)
   - `DRY-RUN-FINDINGS.md` (accumulated kinks)
   - Output from previous agent

**Why Fresh Windows?**
- Validates documentation quality (can new agent pick up from docs alone?)
- Reduces token usage / context pollution
- Simulates real session handoffs
- Tests agent isolation / modularity

---

## Future Enhancements

### Agent Composition (Future)

Could agents call each other?

**Example:**
```python
# P2 agent discovers it needs Python context
# Calls P1 agent as sub-task
result = invoke_agent("python-register-alignment", {
    "task": "explain register field 'monitor_threshold_voltage'",
    "context": "VHDL implementation needs unit conversion"
})
```

**Benefits:**
- More dynamic collaboration
- Reuse of agent expertise

**Risks:**
- Complexity
- Context leakage

**Decision:** Start with sequential, evaluate agent composition later

---

## Implementation Plan

**After Dry-Run Completes:**

1. **Create Agent Specs:**
   - Write `.claude/agents/python-register-alignment/agent.md`
   - Write `.claude/agents/vhdl-fsm-implementation/agent.md`
   - Write `.claude/agents/cocotb-integration-test/agent.md`

2. **Create Usage Examples:**
   - `bpd/bpd-sessions/agent-usage-examples/P1-python-alignment-run.md`
   - `bpd/bpd-sessions/agent-usage-examples/P2-vhdl-implementation-run.md`
   - `bpd/bpd-sessions/agent-usage-examples/P3-cocotb-testing-run.md`

3. **Test Agent Workflow:**
   - Execute P1 manually, document experience
   - Refine agent spec based on findings
   - Repeat for P2 and P3

4. **Integrate with Session Workflow:**
   - Update `NEXT-SESSION.md` to reference agents
   - Add agent invocation examples
   - Document agent selection criteria

---

## Value Proposition

### For Humans
- **Clear roles:** Each agent has a specific job
- **Manageable scope:** No single agent is overwhelmed
- **Easy handoffs:** Clean boundaries between phases

### For AI Agents
- **Reduced context:** Only load domain-relevant knowledge
- **Deep expertise:** Specialized prompts for each domain
- **Better results:** Focus leads to higher quality output

### For Automation
- **Modular:** Each agent can be improved independently
- **Testable:** Clear inputs/outputs for validation
- **Composable:** Agents can potentially call each other

---

**Status:** 📋 Proposal (awaiting dry-run validation)
**Next Steps:** Complete dry-run, then implement agent specs
**Created:** 2025-11-05
**Author:** johnycsh + Claude Code


---

## ✅ IMPLEMENTATION UPDATE (2025-11-05)

**Decision Made:** Agents placed in `bpd/agents/` (experimental location)

**Created:**
- `bpd/agents/python-register-alignment/agent.md`
- `bpd/agents/vhdl-fsm-implementation/agent.md`
- `bpd/agents/cocotb-integration-test/agent.md`

**Rationale:**
- Conservative approach (doesn't pollute top-level)
- Clearly experimental (WIP from dry-run)
- Easy to promote to `.claude/agents/` if successful

**Next Steps:**
- Execute dry-run using these agents
- Validate agent boundaries and handoffs
- Promote to `.claude/agents/` if proven successful

**Status:** ✅ Agents created, ready for dry-run validation

