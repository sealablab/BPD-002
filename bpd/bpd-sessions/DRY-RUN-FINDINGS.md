# Dry-Run Findings: YAML → FSM → CocoTB Workflow

**Session:** 2025-11-05-integration-testing
**Status:** 🔬 Active Discovery

---

## Kinks Discovered

### 🔴 KINK #1: Stale FSM Implementation (CRITICAL)

**Discovered:** 2025-11-05 (Initial audit phase)

**Problem:**
`bpd/bpd-vhdl/src/fi_probe_interface.vhd` exists but is **out of sync** with the current `bpd/bpd-specs/basic_probe_driver.yaml`.

**Root Cause:**
- The FSM was generated in an early iteration (commit 186e3d5, ~Nov 5 03:55 AM)
- The YAML spec was manually improved and refined afterward
- The FSM was never regenerated to match the improved spec

**Specific Mismatches:**

1. **State Encoding:**
   - FSM uses VHDL enums (violates forge-vhdl standards)
   - Should use `std_logic_vector(5 downto 0)` constants

2. **Missing Registers from YAML:**
   - `trigger_wait_timeout` (u16, seconds) - Not implemented
   - `auto_rearm_enable` (boolean) - Not implemented
   - `fault_clear` (boolean) - Not implemented
   - `trig_out_duration` (u16, nanoseconds) - Not implemented
   - `intensity_voltage` (s16, millivolts) - Not implemented
   - `intensity_duration` (u16, nanoseconds) - Not implemented
   - `cooldown_interval` (u24, microseconds) - Hard-coded as 255 cycles instead
   - All monitoring fields:
     - `probe_monitor_feedback` (s16, mV, read-only)
     - `monitor_enable` (boolean)
     - `monitor_threshold_voltage` (s16, mV)
     - `monitor_expect_negative` (boolean)
     - `monitor_window_start` (u32, ns)
     - `monitor_window_duration` (u32, ns)

3. **Port Mismatch:**
   - FSM has simple ports (trigger_in, arm, pulse_width, voltage_level)
   - YAML defines 13+ distinct register fields
   - No connection to generated `*_shim.vhd` register interface

4. **State Machine Differences:**
   - FSM has fixed 256-cycle cooldown
   - YAML specifies configurable `cooldown_interval` (1-500000 μs, 24-bit)

**Impact:**
- Cannot directly use existing FSM with current YAML spec
- Either:
  - **Option A:** Regenerate FSM from scratch (matches workflow goal)
  - **Option B:** Manually refactor FSM to match YAML (tedious, error-prone)
  - **Option C:** Treat as starting template, evolve incrementally

**Workflow Implications:**

✅ **GOOD NEWS:**
- This validates the need for automation!
- Manual sync is error-prone and tedious
- Confirms the workflow should be: YAML → FSM (regenerate fully)

⚠️ **DESIGN QUESTION:**
- Should generated FSM be **read-only** (always regenerate)?
- Or **template-based** (generate once, then hand-edit)?
- How do we handle custom logic that can't be auto-generated?

**Decision Points for Automation:**

1. **Regeneration Strategy:**
   - Always regenerate FSM from YAML (destroys manual edits)?
   - Generate into separate file, manual merge?
   - Use marker comments for "manual sections" (like forge does)?

2. **State Derivation:**
   - How do we infer states from YAML?
   - YAML has comments like "arming policy", "output drive", "monitoring"
   - Could these sections map to states?
   - Or explicitly add `states:` section to YAML?

3. **Register Mapping:**
   - Need clear rules: which registers are inputs vs outputs?
   - Which registers control FSM vs are controlled by FSM?
   - How to handle read-only feedback registers?

**Proposed Solutions:**

**Immediate (Dry-Run):**
- Treat existing FSM as obsolete
- Regenerate from scratch following forge-vhdl patterns
- Document every decision in the process
- This gives us the full workflow experience

**Long-term (Automation):**
- Add metadata to YAML:
  ```yaml
  # Possible enhancement
  fsm:
    states: [IDLE, ARMED, FIRING, COOLDOWN, FAULT]
    control_registers: [trigger_wait_timeout, auto_rearm_enable, ...]
    output_registers: [probe_monitor_feedback, ...]
  ```
- Or infer from existing structure (smarter parser)
- Generate FSM with clear separation:
  - `fi_probe_interface_generated.vhd` (auto-generated, don't edit)
  - `fi_probe_interface_custom.vhd` (manual extensions)

---

## Workflow Step Affected

**Step 2: FSM Generation**
- ⚠️ Cannot assume FSM doesn't exist
- ⚠️ Must handle stale/outdated FSM
- ⚠️ Need versioning or timestamp checks?

**Step 3: Register Interface Wiring**
- ⚠️ Existing FSM ports don't match generated register interface
- Need to wire ~13 registers, not 4 simple signals

---

## Action Items from This Kink

**For This Session (Manual Dry-Run):**
- [ ] Delete or rename existing `fi_probe_interface.vhd`
- [ ] Create fresh FSM following forge-vhdl standards
- [ ] Implement all 13 register fields from YAML
- [ ] Wire to generated `*_shim.vhd`
- [ ] Document every manual decision made

**For Future Automation:**
- [ ] Decide: Regenerate vs Template approach
- [ ] Add FSM metadata to YAML (or infer intelligently)
- [ ] Create detection for stale FSM (timestamp, version hash?)
- [ ] Define "generated" vs "custom" code boundaries

---

## Questions Raised

1. **Versioning:** How do we detect when YAML has changed and FSM needs regen?
2. **Partial Regen:** Can we regenerate just the register wiring, keep FSM logic?
3. **Custom Logic:** Where does probe-specific logic go if FSM is auto-generated?
4. **Testing:** Do tests also need regeneration when YAML changes?

---

## Positive Discoveries

✅ This proves the dry-run methodology is working!
✅ Found the issue early, before automation effort
✅ Real-world scenario: specs evolve, code gets stale
✅ Validates automation value proposition

---

## Kinks Discovered

### 🟡 KINK #2: CustomInstrument Wrapper Authority Unclear

**Discovered:** 2025-11-05 (During P3 phase planning)

**Problem:**
For Phase P3 (CocoTB integration testing), we need to wrap the entire system (FSM + register interface) in a **CustomInstrument wrapper** that matches what the Moku cloud compiler expects. However, it's unclear where the authoritative specification for this wrapper lives.

**Questions:**
1. What is the official name? (CustomInstrument vs CustomWrapper - "they are changing the name")
2. Where is the authoritative template/spec?
   - Moku cloud compiler documentation?
   - forge/forge-codegen repository?
   - Separate Moku SDK?
3. What are the required ports/signals?
4. How does it interface with the generated `*_shim.vhd` and `*_main.vhd`?
5. Are there example instantiations we can reference?

**Impact:**
- Blocks P3 (CocoTB integration test) until resolved
- Cannot create proper test harness without knowing wrapper structure
- May discover that wrapper template is also stale/non-existent

**Workflow Implications:**

⚠️ **CRITICAL FOR AUTOMATION:**
- Need to establish clear source of truth for wrapper
- Wrapper template should be versionable/trackable
- Wrapper changes could break generated code

**Where to Look:**
- [ ] Moku cloud compiler documentation
- [ ] forge-codegen repository (check for wrapper templates)
- [ ] Moku SDK / API documentation
- [ ] Example projects using CustomInstrument
- [ ] Contact Moku team for official spec?

**Proposed Solutions:**

**Immediate (For P3):**
- Search forge/forge-codegen for wrapper examples
- Check if generated code includes wrapper template
- Review Moku cloud compiler documentation
- If no authoritative source found, document this as a gap

**Long-term (For Automation):**
- Establish wrapper template as part of code generation
- Version wrapper template alongside YAML spec
- Include wrapper in YAML → VHDL → Test workflow
- Add wrapper compliance checks to validation

**Status:** 🔍 Investigation needed in P3

---

### 🟢 INSIGHT #1: Natural Sub-Agent Boundaries

**Discovered:** 2025-11-05 (During phase planning)

**Observation:**
The three phases map perfectly to specialized sub-agents with distinct domain expertise:

**P1 Agent: Python/Register Alignment Specialist**
- **Domain:** Python, register definitions, validation logic
- **Barely VHDL aware:** Only needs to understand register → hardware mapping conceptually
- **Knowledge:**
  - Python type system
  - Register field validation (ranges, units)
  - bpd-core/bpd-drivers/bpd-examples structure
  - YAML parsing (to extract register definitions)
- **Inputs:** `basic_probe_driver.yaml`
- **Outputs:** Aligned Python code (bpd-core, bpd-drivers, bpd-examples)

**P2 Agent: VHDL/FSM Implementation Specialist**
- **Domain:** VHDL, FSM design, forge-vhdl standards
- **Platform awareness:** Needs basic CustomInstrument wrapper knowledge (port structure)
- **Knowledge:**
  - forge-vhdl coding standards (std_logic_vector states, port order, etc.)
  - FSM design patterns
  - Register interface wiring
  - Unit conversions (mV, ns, μs, s → hardware counters)
  - Clock domain reasoning
- **Inputs:** `basic_probe_driver.yaml`, generated `*_shim.vhd`, CustomInstrument wrapper spec
- **Outputs:** Compliant FSM implementation

**P3 Agent: CocoTB/Integration Test Specialist**
- **Domain:** CocoTB testing, GHDL, progressive testing standards
- **Very CocoTB specific:** Deep knowledge of forge-vhdl testing patterns
- **Knowledge:**
  - CocoTB API and type constraints
  - forge-vhdl progressive testing (P1/P2/P3 levels)
  - GHDL output filtering
  - Test infrastructure patterns (test_base.py, constants files)
  - CustomInstrument wrapper instantiation in test harness
- **Inputs:** VHDL implementation, YAML spec, forge-vhdl test standards
- **Outputs:** Progressive test suite (P1/P2/P3)

**Workflow Implication:**
- Each agent has **minimal context overlap** (good for efficiency)
- Each agent has **deep domain expertise** (good for quality)
- Agents can be **developed/improved independently**
- Natural **checkpoint/validation** between agents

**Architecture Questions:**

**Where Should Agents Live?**

Option 1: **Repository-specific (`.claude/agents/`)**
```
.claude/
├── agents/
│   ├── p1-python-alignment.md
│   ├── p2-vhdl-implementation.md
│   └── p3-cocotb-testing.md
└── shared/
    └── ARCHITECTURE_OVERVIEW.md
```
✅ Co-located with project
✅ Version controlled with code
❌ Duplicates across projects?

Option 2: **Submodule-specific (libs/*/agents/)**
```
libs/forge-vhdl/agents/
├── vhdl-implementation-agent.md
└── cocotb-testing-agent.md

bpd/bpd-core/agents/
└── python-alignment-agent.md
```
✅ Lives with relevant code
✅ Reusable across projects using submodule
❌ Fragmented agent specs

Option 3: **Session-specific (bpd/bpd-sessions/agents/)**
```
bpd/bpd-sessions/
├── agents/
│   ├── p1-python-alignment-agent.md
│   ├── p2-vhdl-implementation-agent.md
│   └── p3-cocotb-testing-agent.md
├── SESSION-HANDOFF-2025-11-05.md
└── DRY-RUN-FINDINGS.md
```
✅ Co-located with session plans
✅ Easy to find during workflow
❌ Less discoverable for general use

Option 4: **Hybrid: Specs in `.claude/agents/`, Examples in sessions/**
```
.claude/
└── agents/
    ├── python-register-alignment-agent.md
    ├── vhdl-fsm-implementation-agent.md
    └── cocotb-integration-test-agent.md

bpd/bpd-sessions/
└── agent-usage-examples/
    ├── P1-python-alignment-run.md
    ├── P2-vhdl-implementation-run.md
    └── P3-cocotb-testing-run.md
```
✅ Reusable agent specs
✅ Concrete examples in sessions
✅ Clear separation: spec vs usage
✅ Most flexible

**Recommended:** **Option 4 (Hybrid)**

**Agent Spec Structure:**
```markdown
# Agent Name: [Domain] Specialist

## Domain Expertise
- Primary: [main domain]
- Secondary: [supporting domains]
- Minimal: [barely aware of]

## Knowledge Requirements
- Standards: [forge-vhdl, PEP-8, etc.]
- Tools: [CocoTB, GHDL, etc.]
- Patterns: [FSM design, progressive testing, etc.]

## Inputs (Required)
- File: path/to/source-of-truth
- File: path/to/dependency

## Outputs (Expected)
- File: path/to/generated-code
- File: path/to/tests

## Exit Criteria
- [ ] Checklist item 1
- [ ] Checklist item 2

## Common Kinks to Watch For
- Known issue 1
- Known issue 2

## Handoff Protocol
- What to commit
- What to document
- How to hand off to next agent
```

**Next Steps:**
1. After dry-run completes, create agent specs in `.claude/agents/`
2. Document actual usage in `bpd/bpd-sessions/agent-usage-examples/`
3. Refine agent boundaries based on what worked/didn't work
4. Consider: Could agents call each other? Or strictly sequential?

**Value Proposition:**
- **For humans:** Clear workflow with specialist roles
- **For AI:** Reduced context, focused expertise, better results
- **For automation:** Modular, testable, improvable components

---

**Next Kink ID:** #3
**Status:** Active - continuing dry-run

