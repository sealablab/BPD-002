# Session Handoff: 2025-11-05 - BPD YAML Authority & VHDL Alignment

**Date:** 2025-11-05
**Branch:** `session/2025-11-05-integration-testing`
**Status:** 🎯 Active - Ground Truth Established
**Type:** Workflow Dry-Run / Architecture Alignment

---

## Executive Summary

This session establishes **`bpd/bpd-specs/basic_probe_driver.yaml`** as the **single source of truth** for the Basic Probe Driver RTL interface specification. Early VHDL code generated before the YAML was refined needs to be brought into alignment with this authoritative specification.

**Key Insight:** We discovered that early code generation created VHDL that is now **stale and non-compliant** with both:
1. The refined YAML specification
2. The forge-vhdl coding standards

This session documents the gap and begins the alignment work as a **dry-run** for future automation.

---

## Source of Truth: The YAML Specification

### Primary Authority

**File:** `bpd/bpd-specs/basic_probe_driver.yaml`

**Why This is Authoritative:**
- Heavily commented with operational intent
- Captures domain knowledge (probe control flow, safety requirements)
- Defines all register fields with units, ranges, and defaults
- Serves as input to forge-codegen tooling
- Maintained by humans with probe expertise

**Generated Artifacts (DO NOT EDIT):**
- `bpd/bpd-specs/generated/basic_probe_driver_custom_inst_shim.vhd`
- `bpd/bpd-specs/generated/basic_probe_driver_custom_inst_main.vhd`

These are **read-only outputs** from forge-codegen. They wire Moku platform registers to application-specific signals defined in the YAML.

---

## The Gap: Early Code vs Current Spec

### What Exists (Stale)

**File:** `bpd/bpd-vhdl/src/fi_probe_interface.vhd`

**Created:** Initial commit (186e3d5), ~Nov 5 2025 03:55 AM
**Status:** ⚠️ **OBSOLETE** - predates refined YAML spec

**Problems:**
1. **Non-compliant with forge-vhdl standards:**
   - Uses VHDL `enum` types for states (violates Verilog portability)
   - Should use `std_logic_vector(5 downto 0)` constants
   - Port order doesn't follow forge-vhdl conventions

2. **Missing functionality from current YAML:**
   - Only implements 4 simple control signals
   - YAML defines 13+ register fields with specific behaviors
   - Missing: timeout logic, auto-rearm, fault acknowledgement
   - Missing: monitoring infrastructure (6 fields)
   - Missing: proper unit conversions (mV, ns, μs, s)

3. **Not wired to generated register interface:**
   - Standalone entity with generic ports
   - No integration with `*_shim.vhd` or `*_main.vhd`
   - Cannot be controlled via Moku registers

4. **Hard-coded parameters:**
   - Cooldown fixed at 255 cycles
   - YAML specifies 1-500000 μs configurable cooldown (24-bit)

### What Needs to Exist (Target)

**Goal:** FSM implementation that:
1. ✅ Follows forge-vhdl FSM coding standards (`std_logic_vector` states)
2. ✅ Implements **all 13 register fields** from YAML
3. ✅ Wires to generated register interface (`*_shim.vhd`)
4. ✅ Includes `fsm_observer.vhd` for hardware debugging
5. ✅ Has progressive CocoTB tests (P1/P2/P3)
6. ✅ Handles all units correctly (mV, ns, μs, s)
7. ✅ Implements safety features (timeouts, faults, cooldown)

---

## YAML Register Inventory (13 Fields)

From `bpd/bpd-specs/basic_probe_driver.yaml`:

### Arming & Lifecycle (3 fields)
| Field | Type | Units | Range | Purpose |
|-------|------|-------|-------|---------|
| `trigger_wait_timeout` | u16 | seconds | 0-3600 | Max wait in ARMED before timeout |
| `auto_rearm_enable` | bool | - | - | Re-enter ARMED after cooldown (vs IDLE) |
| `fault_clear` | bool | - | - | Write 1 to clear fault state |

### Output Drive Controls (5 fields)
| Field | Type | Units | Range | Purpose |
|-------|------|-------|-------|---------|
| `trig_out_voltage` | s16 | mV | -5000 to 5000 | Voltage for trigger output line |
| `trig_out_duration` | u16 | ns | 20-50000 | Trigger pulse width |
| `intensity_voltage` | s16 | mV | -5000 to 5000 | Power/intensity control voltage |
| `intensity_duration` | u16 | ns | 20-50000 | Intensity pulse width |
| `cooldown_interval` | u24 | μs | 1-500000 | Enforced delay between pulses |

### Probe Monitoring (6 fields)
| Field | Type | Units | Range | Purpose |
|-------|------|-------|-------|---------|
| `probe_monitor_feedback` | s16 | mV | -5000 to 5000 | Current monitor (read-only) |
| `monitor_enable` | bool | - | - | Enable threshold checking |
| `monitor_threshold_voltage` | s16 | mV | -5000 to 5000 | Threshold for comparator |
| `monitor_expect_negative` | bool | - | - | Negative-going = fired |
| `monitor_window_start` | u32 | ns | 0-2e9 | Delay before monitoring |
| `monitor_window_duration` | u32 | ns | 100-2e9 | Monitoring window length |

### TOTAL: 13 register fields (not counting internal state)

---

## The Alignment Task: Three-Phase Approach

### Phase P1: Python Layer Alignment (bpd-core, bpd-drivers, bpd-examples)

**Scope:** Bring Python driver code into alignment with current YAML spec

**Deliverables:**
- [ ] Review `bpd-core/` for stale register definitions
- [ ] Update `bpd-drivers/` (DS1120A driver) to match YAML fields
- [ ] Align `bpd-examples/` with new register structure
- [ ] Update any validation logic (voltage ranges, timing limits)
- [ ] Ensure all 13 YAML register fields have Python accessors
- [ ] Run Python tests if they exist

**Completion Criteria:**
- All Python code aligned with `basic_probe_driver.yaml`
- No references to old/missing register fields
- Python layer ready for VHDL backend

**Commit Strategy:**
```bash
git add bpd/bpd-core/ bpd/bpd-drivers/ bpd/bpd-examples/
git commit -m "P1: Align Python layer with basic_probe_driver.yaml spec

- Update register field definitions to match YAML
- Add missing fields (monitoring, timing controls)
- Remove obsolete fields from early iteration
- Validate voltage/timing ranges per YAML

Phase P1 complete. Ready for P2 (VHDL alignment).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Exit Criteria:**
✅ P1 commit merged
✅ User starts fresh Claude Code window for P2

---

### Phase P2: VHDL RTL Alignment (bpd-vhdl)

**Scope:** Create forge-vhdl compliant FSM that implements YAML spec

**Deliverables:**
- [ ] Analyze generated `*_shim.vhd` register interface
- [ ] Rename/archive stale `fi_probe_interface.vhd`
- [ ] Design FSM states from YAML operational flow
- [ ] Implement FSM following forge-vhdl standards
  - [ ] `std_logic_vector` states (NOT enums)
  - [ ] All 13 register fields wired
  - [ ] Timeout/counter logic (multiple time bases)
  - [ ] Monitoring comparator logic
  - [ ] Safety interlocks
- [ ] Integrate `fsm_observer.vhd` for hardware debugging
- [ ] Wire FSM to generated register interface
- [ ] Handle unit conversions (mV, ns, μs, s → hardware values)

**Completion Criteria:**
- FSM compiles (GHDL or synthesis check)
- Follows forge-vhdl coding standards
- Implements all YAML register fields
- Ready for CocoTB testing

**Commit Strategy:**
```bash
git add bpd/bpd-vhdl/
git commit -m "P2: Implement YAML-aligned FSM following forge-vhdl standards

- Archive stale fi_probe_interface.vhd (pre-YAML refinement)
- Implement all 13 register fields from basic_probe_driver.yaml
- Use std_logic_vector state encoding (Verilog compatible)
- Add timeout logic, monitoring, safety interlocks
- Wire to generated register interface (*_shim.vhd)
- Integrate fsm_observer.vhd for hardware debug

Phase P2 complete. Ready for P3 (CocoTB integration test).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Exit Criteria:**
✅ P2 commit merged
✅ User starts fresh Claude Code window for P3

---

### Phase P3: CocoTB Integration Test (End-to-End Validation)

**Scope:** Create full-system CocoTB test using CustomInstrument wrapper

**Deliverables:**
- [ ] **FIRST:** Locate authoritative CustomInstrument wrapper spec
  - ⚠️ **KINK #2:** Need to find/establish source of truth for this
  - Check Moku cloud compiler docs
  - Check forge/forge-codegen for wrapper templates
  - Document findings in `DRY-RUN-FINDINGS.md`
- [ ] Create CocoTB test harness that wraps entire system
  - [ ] FSM + generated register interface + CustomInstrument wrapper
  - [ ] Maps to Moku cloud compiler expectations
- [ ] Implement progressive tests (P1/P2/P3 levels)
  - [ ] P1: Basic FSM state transitions (<20 line output)
  - [ ] P2: Register read/write, timeout logic
  - [ ] P3: Full monitoring, edge cases
- [ ] Create test infrastructure
  - [ ] Test constants file (register addresses, test values)
  - [ ] Test utilities (clock setup, reset, register access)
  - [ ] Base class integration with forge-vhdl patterns
- [ ] Validate end-to-end flow:
  - Python → Registers → FSM → Hardware Outputs

**Completion Criteria:**
- P1 CocoTB tests passing (<20 line output)
- Full system integration validated
- CustomInstrument wrapper correctly instantiated
- Ready for deployment to Moku hardware

**Commit Strategy:**
```bash
git add bpd/bpd-vhdl/tests/
git commit -m "P3: Add CocoTB integration tests for full BPD system

- Create CustomInstrument wrapper test harness
- Implement progressive tests (P1/P2/P3)
- Validate Python → Register → FSM → Hardware flow
- Follow forge-vhdl testing standards (aggressive filtering)

Phase P3 complete. System ready for hardware deployment.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Exit Criteria:**
✅ P3 commit merged
✅ Full dry-run workflow complete
✅ Findings documented for automation

---

## Phase Transition Protocol

**Between Each Phase:**
1. Commit phase work with descriptive message
2. Update `DRY-RUN-FINDINGS.md` with any kinks discovered
3. User closes Claude Code window
4. User opens fresh Claude Code window (clean context)
5. New session reads:
   - `SESSION-HANDOFF-2025-11-05.md` (this file)
   - `DRY-RUN-FINDINGS.md` (accumulated kinks)
   - Relevant code from completed phase

**Why Fresh Windows?**
- Simulates handoff between sessions
- Tests documentation quality (is context clear?)
- Reduces token usage / context pollution
- Validates that session files are truly authoritative

---

## Kinks to Watch For

### Already Discovered:
- **Kink #1:** Stale FSM from early iteration (documented)

### Expected to Discover:
- **Kink #2:** CustomInstrument wrapper authority unclear (P3)
- **Kink #?:** Python register field naming mismatches?
- **Kink #?:** Unit conversion ambiguities (mV → digital)?
- **Kink #?:** Register address mapping (how are addresses assigned)?
- **Kink #?:** CocoTB type compatibility issues?

All kinks get documented in `DRY-RUN-FINDINGS.md` as discovered.

---

## Session History Context

### Session Workflow Pattern

This repository uses `bpd/bpd-sessions/` to maintain a **linear work history**:

```
bpd/bpd-sessions/
├── NEXT-SESSION.md              # Template for planning future sessions
├── SESSION-HANDOFF-YYYY-MM-DD.md  # Handoff docs (like this one)
├── YYYY-MM-DD-description.md    # Dated session plans
├── WORKFLOW-DRY-RUN-PLAN.md     # Experimental workflow plans
└── DRY-RUN-FINDINGS.md          # Discovered issues/patterns
```

**Purpose:**
- Provide context for humans and AI agents
- Document decision rationale
- Track evolution of design thinking
- Enable handoffs between sessions
- Capture institutional knowledge

**Current Session Files:**
- `SESSION-HANDOFF-2025-11-05.md` (this file) - Authority establishment
- `2025-11-05-integration-testing.md` - Detailed session plan
- `WORKFLOW-DRY-RUN-PLAN.md` - Automation workflow design
- `DRY-RUN-FINDINGS.md` - Kinks and discoveries

### Session Branches

**Branch:** `session/2025-11-05-integration-testing`

Work is done in dated session branches to enable:
- Parallel experimentation
- Easy rollback if needed
- Clear merge points to main
- Git history that mirrors session history

---

## Key Design Questions

### For This Session (Manual Work)

1. **State Mapping:**
   - How do YAML registers map to FSM states?
   - Infer from comments or explicit definition needed?

2. **Timing Conversions:**
   - YAML has ns, μs, s - how to handle different time bases?
   - Clock domain is 125 MHz (8 ns period)
   - Need counter bit widths for each time scale

3. **Monitoring Logic:**
   - Comparator threshold + window timing
   - Polarity control (expect negative vs positive)
   - Integration with FSM (affects state transitions?)

4. **Register Interface:**
   - Which registers are inputs to FSM?
   - Which are outputs from FSM?
   - Read-only vs read-write semantics

### For Future Automation

1. **YAML Enhancements:**
   - Add explicit FSM metadata?
   - Or rely on inference from existing structure?

2. **Code Generation Strategy:**
   - Full regeneration (destroys manual edits)?
   - Template-based (generate once, manual thereafter)?
   - Marked regions (auto-gen + manual sections)?

3. **Versioning:**
   - How to detect when YAML changes require VHDL regen?
   - Timestamp? Hash? Semantic version?

4. **Validation:**
   - How to verify generated code matches YAML intent?
   - Automated compliance checks?

---

## References

### Authoritative Specifications
- **Primary:** `bpd/bpd-specs/basic_probe_driver.yaml` - RTL interface spec
- **Standards:** `libs/forge-vhdl/CLAUDE.md` - FSM coding standards
- **Standards:** `libs/forge-vhdl/docs/VHDL_CODING_STANDARDS.md` - Detailed rules

### Generated Code (Read-Only)
- `bpd/bpd-specs/generated/basic_probe_driver_custom_inst_shim.vhd`
- `bpd/bpd-specs/generated/basic_probe_driver_custom_inst_main.vhd`

### Implementation (To Be Aligned)
- `bpd/bpd-vhdl/src/fi_probe_interface.vhd` ⚠️ STALE
- `bpd/bpd-vhdl/tests/test_fi_interface.py` ⚠️ NEEDS UPDATE

### Reference Components
- `libs/forge-vhdl/vhdl/debugging/fsm_observer.vhd` - FSM debugging
- `libs/forge-vhdl/tests/test_base.py` - Progressive testing base class

### Session Documentation
- `bpd/bpd-sessions/2025-11-05-integration-testing.md` - Detailed plan
- `bpd/bpd-sessions/WORKFLOW-DRY-RUN-PLAN.md` - Automation design
- `bpd/bpd-sessions/DRY-RUN-FINDINGS.md` - Issues discovered

---

## Success Criteria

### Minimum (Learning Goal)
- [ ] Understand gap between early code and current YAML
- [ ] Document alignment requirements
- [ ] Execute at least one manual alignment step
- [ ] Capture findings for future automation

### Target (Functional Goal)
- [ ] FSM implements all 13 YAML register fields
- [ ] FSM follows forge-vhdl standards
- [ ] FSM wired to generated register interface
- [ ] At least P1 basic tests passing

### Stretch (Automation Goal)
- [ ] Full P1/P2 test suite passing
- [ ] FSM observer integrated
- [ ] Clear automation roadmap documented
- [ ] Template files ready for codegen

---

## Next Steps

**Immediate:**
1. Analyze generated `*_shim.vhd` structure
2. Design FSM states from YAML operational flow
3. Decide: rename stale FSM to `.old` or delete?

**This Session:**
1. Manually implement YAML-aligned FSM
2. Wire to register interface
3. Create progressive tests
4. Document all decisions in `DRY-RUN-FINDINGS.md`

**Future Sessions:**
1. Codify workflow into automation tool (slash command or agent)
2. Create templates for YAML → FSM → Tests
3. Implement validation/compliance checks

---

## For AI Agents Reading This

**Context:**
You are joining mid-session on a workflow dry-run. The goal is to manually execute a workflow we eventually want to automate, documenting pain points along the way.

**Ground Truth:**
- `bpd/bpd-specs/basic_probe_driver.yaml` is the authoritative specification
- Early generated code in `bpd/bpd-vhdl/` is obsolete
- We need to bring VHDL into alignment with YAML

**Standards:**
- Follow `libs/forge-vhdl/CLAUDE.md` for all VHDL/testing patterns
- Use `std_logic_vector` for FSM states (NOT enums)
- Implement progressive testing (P1/P2/P3)

**Approach:**
- This is a **learning exercise** (dry-run)
- Document every decision in `DRY-RUN-FINDINGS.md`
- We're optimizing for understanding, not perfection
- Ask questions if YAML intent is unclear

**Session Files:**
- Read `bpd/bpd-sessions/` directory for full context
- Update `DRY-RUN-FINDINGS.md` when you discover kinks
- Reference this handoff for source of truth

---

**Last Updated:** 2025-11-05
**Author:** johnycsh + Claude Code
**Session:** session/2025-11-05-integration-testing
**Purpose:** Establish ground truth and document alignment task
