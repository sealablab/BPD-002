# Session Plan: 2025-11-05 - Integration Testing & Workflow Dry-Run

**Branch:** `session/2025-11-05-integration-testing`
**Focus:** Dry-run the YAML→FSM→CocoTB workflow to identify kinks before codification
**Status:** 🟡 Active - Workflow Discovery Phase

---

## Session Context

### What We Just Completed
- ✅ Committed `bpd/bpd-specs/basic_probe_driver.yaml` - Heavily commented register specification
- ✅ Generated VHDL register interfaces via forge codegen:
  - `bpd/bpd-specs/generated/basic_probe_driver_custom_inst_shim.vhd` (11.8 KB)
  - `bpd/bpd-specs/generated/basic_probe_driver_custom_inst_main.vhd` (10.1 KB)
- ✅ Explored `libs/forge-vhdl/` to understand authoritative FSM and CocoTB patterns

### Current Session Goals (DRY RUN PHASE)

**PRIMARY OBJECTIVE:** Manually execute the workflow we want to automate, documenting pain points and decision points along the way.

This is **NOT** about getting everything perfect - it's about:
1. Discovering where human decisions are needed
2. Identifying what can be automated vs what needs templates
3. Finding the kinks in the process
4. Creating examples for future codegen

---

## The Workflow We're Dry-Running

### Desired Automated Workflow (Future State)

**Input:** `basic_probe_driver.yaml` (register specification)

**Process:**
1. **Parse YAML** → Extract control registers, state transitions, timing parameters
2. **Generate FSM States** → Map register fields to FSM states (using `std_logic_vector`)
3. **Generate State Logic** → Create next-state logic based on register controls
4. **Wire Register Interface** → Connect generated `*_shim.vhd` ports to FSM signals
5. **Add FSM Observer** → Instantiate `fsm_observer.vhd` for hardware debugging
6. **Generate CocoTB Tests** → Create P1/P2 test structure automatically

**Output:**
- `fi_probe_interface.vhd` (FSM implementation)
- `fi_probe_interface_tests/P1_fi_probe_interface_basic.py`
- Test constants and infrastructure

### Manual Dry-Run (This Session)

We'll execute each step manually, documenting:
- What information we need from the YAML
- What decisions we make and why
- What patterns emerge that could be templated
- What's hard-coded vs parameterizable
- Where we get stuck or confused

---

## Technical Context

### Current State

**✅ What We Have:**
- `bpd/bpd-specs/basic_probe_driver.yaml` - Source of truth for register interface
- `bpd/bpd-specs/generated/basic_probe_driver_custom_inst_shim.vhd` - Generated register shim
- `bpd/bpd-specs/generated/basic_probe_driver_custom_inst_main.vhd` - Generated register main
- `libs/forge-vhdl/` - Authoritative VHDL patterns, CocoTB infrastructure, FSM observer

**⚠️ What We Need to Create (Manually, This Session):**
- `bpd/bpd-vhdl/src/fi_probe_interface.vhd` - FSM implementation (may already exist, needs review)
- `bpd/bpd-vhdl/tests/fi_probe_interface_tests/` - Test directory structure
- `bpd/bpd-vhdl/tests/fi_probe_interface_tests/fi_probe_interface_constants.py`
- `bpd/bpd-vhdl/tests/fi_probe_interface_tests/P1_fi_probe_interface_basic.py`

**⚠️ What We Need to Verify:**
- Does `fi_probe_interface.vhd` exist? If so, what state is it in?
- Does it follow forge-vhdl FSM standards?
- How do we wire it to the generated register interface?

### Key Files to Touch

**Specification:**
- `bpd/bpd-specs/basic_probe_driver.yaml` - Read-only reference

**Generated Code (DO NOT EDIT):**
- `bpd/bpd-specs/generated/basic_probe_driver_custom_inst_shim.vhd` - Register interface
- `bpd/bpd-specs/generated/basic_probe_driver_custom_inst_main.vhd` - Register main

**Implementation (TO CREATE/EDIT):**
- `bpd/bpd-vhdl/src/fi_probe_interface.vhd` - FSM core (manual for now)

**Testing (TO CREATE):**
- `bpd/bpd-vhdl/tests/fi_probe_interface_tests/` - Test infrastructure
- `bpd/bpd-vhdl/tests/run.py` - May need updates

**Reference Standards:**
- `libs/forge-vhdl/CLAUDE.md` - Authoritative testing guide
- `libs/forge-vhdl/docs/VHDL_CODING_STANDARDS.md` - FSM patterns
- `libs/forge-vhdl/vhdl/debugging/fsm_observer.vhd` - FSM observer component

### FSM States (Derived from YAML)

Based on `basic_probe_driver.yaml` comments and register fields:

```vhdl
-- State encoding (6-bit for fsm_observer compatibility)
constant STATE_IDLE     : std_logic_vector(5 downto 0) := "000000";  -- Safe idle
constant STATE_ARMED    : std_logic_vector(5 downto 0) := "000001";  -- Waiting for trigger
constant STATE_FIRING   : std_logic_vector(5 downto 0) := "000010";  -- Pulses active
constant STATE_COOLDOWN : std_logic_vector(5 downto 0) := "000011";  -- Enforcing cooldown
constant STATE_FAULT    : std_logic_vector(5 downto 0) := "111111";  -- Sticky fault (needs ack)
```

### Register Field → FSM Control Mapping

From `basic_probe_driver.yaml`:

**Arming/Lifecycle:**
- `trigger_wait_timeout` → Timeout counter in ARMED state → FAULT
- `auto_rearm_enable` → COOLDOWN → (ARMED if true, IDLE if false)
- `fault_clear` → FAULT → IDLE (requires write of 1)

**Output Controls:**
- `trig_out_voltage` → DAC value during FIRING
- `trig_out_duration` → Pulse width for trigger output
- `intensity_voltage` → DAC value during FIRING
- `intensity_duration` → Pulse width for intensity output
- `cooldown_interval` → Dwell time in COOLDOWN state

**Monitoring:**
- `probe_monitor_feedback` → ADC input (read-only)
- `monitor_enable` → Enable threshold checking
- `monitor_threshold_voltage` → Comparator setpoint
- `monitor_expect_negative` → Comparator polarity
- `monitor_window_start` → Delay before checking
- `monitor_window_duration` → Checking window length

---

## Session Approach

### Phase 1: Discovery (Current)
1. ✅ Reviewed forge-vhdl standards and patterns
2. ✅ Created session handoff document
3. ⏳ Create PLAN file documenting dry-run approach
4. ⏳ Audit what exists in `bpd/bpd-vhdl/src/` and `bpd/bpd-vhdl/tests/`

### Phase 2: Manual Implementation
1. Create/modify `fi_probe_interface.vhd` following forge-vhdl FSM standards
2. Wire register interface to FSM
3. Instantiate `fsm_observer.vhd` for debugging
4. Document decisions and pain points

### Phase 3: Testing Infrastructure
1. Create test directory structure
2. Write constants file
3. Write P1 basic tests
4. Run tests, iterate

### Phase 4: Documentation Harvest
1. Document what worked, what didn't
2. Identify automation opportunities
3. Create templates for future codegen
4. Write up findings for future slash command/agent

---

## Success Criteria

### Minimum Viable Dry-Run
- [ ] FSM exists and follows forge-vhdl standards
- [ ] FSM is wired to generated register interface
- [ ] At least one P1 test passes
- [ ] We have documented pain points and decision points

### Stretch Goals
- [ ] Full P1 test suite passing (<20 lines output)
- [ ] FSM observer integrated and working
- [ ] Clear documentation of what can be automated
- [ ] Template files ready for future codegen

---

## Pain Points to Document

As we work, we'll track:
- **Decision Points:** Where did we have to make a choice? Could it be automated?
- **Missing Information:** What did we need that wasn't in the YAML?
- **Tedious Patterns:** What felt repetitive and could be templated?
- **Gotchas:** Where did we get stuck? What was unclear?
- **Happy Accidents:** What worked better than expected?

---

## Next Session Prep

**If this dry-run succeeds:**
- Next focus: Codify workflow into slash command or agent
- Need: Template engine, YAML parser, code generator
- Consider: Python script vs LLM-based agent

**If we discover blockers:**
- Fallback: Iterate on manual process until it's smooth
- Alternative: Simplify workflow, reduce scope
- Escalate: Review with domain expert if architectural questions arise

---

## Session Log

**Started:** 2025-11-05 (session branch created)
**Current Phase:** Phase 1 - Discovery
**Status:** Creating foundational documents before manual implementation

### Work Items Completed
- Explored `libs/forge-vhdl/` using Task agent
- Identified FSM patterns and CocoTB standards
- Created session handoff document
- Mapped YAML registers to FSM states and controls

### Issues Encountered
- None yet (just starting)

### Follow-up Tasks
- Create PLAN file
- Audit existing VHDL in `bpd/bpd-vhdl/`
- Begin manual FSM implementation

---

## References

**Key Documentation:**
- `libs/forge-vhdl/CLAUDE.md` - Authoritative testing and design guide
- `libs/forge-vhdl/docs/VHDL_CODING_STANDARDS.md` - FSM coding standards
- `libs/forge-vhdl/docs/COCOTB_TROUBLESHOOTING.md` - Testing debugging

**Key Components:**
- `libs/forge-vhdl/vhdl/debugging/fsm_observer.vhd` - FSM observer for hardware debug
- `libs/forge-vhdl/tests/test_base.py` - CocoTB test base class

**Specification:**
- `bpd/bpd-specs/basic_probe_driver.yaml` - Register specification (source of truth)

**Generated Code:**
- `bpd/bpd-specs/generated/basic_probe_driver_custom_inst_shim.vhd`
- `bpd/bpd-specs/generated/basic_probe_driver_custom_inst_main.vhd`

---

**Last Updated:** 2025-11-05
**Session Owner:** johnycsh + Claude Code
**Session Type:** Workflow Discovery / Dry-Run
