# Workflow Dry-Run Plan: YAML → FSM → CocoTB

**Purpose:** Execute the desired automation workflow manually to discover kinks, pain points, and automation opportunities.

**Status:** 🔬 Experimental / Discovery Phase

**Session:** 2025-11-05-integration-testing

---

## The Big Picture

We want to eventually **automate** the creation of FSM-based custom instruments from YAML register specifications. But before we write any automation code, we need to:

1. **Understand the workflow deeply** by doing it manually
2. **Identify decision points** that need human input vs can be automated
3. **Find the pain points** and smooth them out
4. **Create reference examples** that serve as templates for future codegen

**This is a deliberate dry-run, not production work.**

---

## Target Workflow (What We Want to Automate)

### Input
```
bpd/bpd-specs/basic_probe_driver.yaml
    ↓
```

### Transformation Steps

**Step 1: YAML Analysis**
- Parse register definitions
- Extract state machine implications from comments and register names
- Identify control signals, status signals, timing parameters
- Map registers to FSM states and transitions

**Step 2: FSM Generation**
- Generate state constants (std_logic_vector, forge-vhdl compliant)
- Generate state transition logic
- Generate timeout/counter logic
- Generate output control logic

**Step 3: Register Interface Wiring**
- Connect generated `*_shim.vhd` ports to FSM signals
- Map control registers to FSM inputs
- Map status registers to FSM outputs
- Handle read-only vs read-write semantics

**Step 4: Debug Infrastructure**
- Instantiate `fsm_observer.vhd` with appropriate state mapping
- Configure voltage encoding for oscilloscope visibility
- Wire to Moku debug channel

**Step 5: Test Generation**
- Create test directory structure (following forge-vhdl conventions)
- Generate constants file with register addresses and test values
- Generate P1 basic tests (reset, basic state transitions)
- Generate P2 intermediate tests (edge cases, timeouts)

### Output
```
bpd/bpd-vhdl/src/fi_probe_interface.vhd                          # FSM implementation
bpd/bpd-vhdl/tests/fi_probe_interface_tests/                     # Test infrastructure
    ├── fi_probe_interface_constants.py                          # Shared constants
    ├── P1_fi_probe_interface_basic.py                           # Basic tests
    └── P2_fi_probe_interface_intermediate.py                    # Extended tests
```

---

## Dry-Run Methodology

### How We'll Execute This

**Phase 1: Pre-Implementation Audit**
1. Survey what already exists in `bpd/bpd-vhdl/`
2. Understand the generated register code structure
3. Identify gaps between generated code and FSM needs

**Phase 2: Manual FSM Creation**
1. Analyze YAML to determine FSM requirements
   - **Document:** What information did we extract? How did we extract it?
2. Write FSM following forge-vhdl standards
   - **Document:** What decisions did we make? What was ambiguous?
3. Wire FSM to generated register interface
   - **Document:** What was tedious? What was tricky?
4. Add fsm_observer instance
   - **Document:** What needed configuration? What was boilerplate?

**Phase 3: Manual Test Creation**
1. Create test directory structure
   - **Document:** What's the pattern? Can it be templated?
2. Write constants file
   - **Document:** Where did these values come from? YAML? Manual?
3. Write P1 tests
   - **Document:** What's the test pattern? Can we generate this?
4. Run tests, iterate
   - **Document:** What broke? What assumptions were wrong?

**Phase 4: Harvest Insights**
1. Review all documentation/notes
2. Identify:
   - **Automatable:** Clear patterns, deterministic transformations
   - **Template-able:** Structure is fixed, values are parameterized
   - **Human-Required:** Design decisions, edge cases, domain knowledge
3. Create templates/examples for future codegen

---

## What We're Looking For

### Decision Points (Can These Be Automated?)

**State Naming:**
- Do state names come from YAML comments?
- Do we infer them from register field names?
- Do we need a naming convention?

**State Transitions:**
- Can we infer transitions from register fields like `auto_rearm_enable`?
- Do we need explicit state machine diagrams in YAML?
- How do we handle edge cases (faults, timeouts)?

**Timing Logic:**
- Registers like `trigger_wait_timeout` imply counters - how do we generate these?
- What bit widths? Derived from max_value in YAML?
- What clock domains?

**Register Mapping:**
- Which registers are inputs to FSM vs outputs from FSM?
- How do we handle read-modify-write registers?
- What about default values?

### Pain Points (What's Tedious or Error-Prone?)

**Boilerplate Code:**
- Entity declarations (port lists)
- Signal declarations
- Clock/reset logic
- Generic state machine structure

**Wiring:**
- Connecting dozens of register fields to FSM signals
- Type conversions (std_logic_vector ↔ signed/unsigned)
- Width matching

**Testing:**
- Writing repetitive test setup/teardown
- Calculating register addresses
- Encoding/decoding register values

### Patterns (What's Reusable?)

**FSM Structure:**
- State register vs next-state logic separation
- Reset behavior
- Enable hierarchy

**Register Interface:**
- How do control registers drive FSM?
- How does FSM update status registers?

**Test Structure:**
- Common test patterns (reset, basic operation, edge cases)
- Assertion patterns
- Clock/reset utilities

---

## Success Metrics

### Minimum Success (We Learn Something)
- [ ] We complete at least one step of the workflow manually
- [ ] We document what we did and why
- [ ] We identify at least 3 things that could be automated

### Good Success (We Have a Working Example)
- [ ] FSM exists and compiles
- [ ] At least one test passes
- [ ] We have a clear list of automatable vs manual tasks

### Great Success (We Have a Codegen Blueprint)
- [ ] Full working FSM with tests
- [ ] Detailed documentation of every decision
- [ ] Template files ready for parameterization
- [ ] Clear roadmap for automation tool

---

## Key Questions to Answer

**During YAML Analysis:**
1. Is all necessary information present in the YAML?
2. What needs to be inferred vs explicitly stated?
3. Are the comments sufficient for state machine derivation?

**During FSM Creation:**
1. What's the right level of abstraction for the FSM?
2. How do we balance generated code vs hand-written logic?
3. What needs to be configurable via generics?

**During Register Wiring:**
1. Is the generated register interface complete?
2. Do we need to modify `*_main.vhd` or just instantiate it?
3. How do we handle bi-directional signals?

**During Test Creation:**
1. Can we generate meaningful tests from YAML alone?
2. What domain knowledge is required for good test cases?
3. How do we validate timing-sensitive behavior?

---

## Deliverables from This Dry-Run

### Immediate Artifacts
- [ ] Working `fi_probe_interface.vhd` (or attempt with notes on blockers)
- [ ] Test infrastructure (even if incomplete)
- [ ] Session notes documenting the process

### Knowledge Artifacts
- [ ] Decision log (what choices we made and why)
- [ ] Pain point list (what was hard, tedious, or error-prone)
- [ ] Pattern catalog (reusable structures we identified)
- [ ] Automation opportunities (what could be codegen'd)

### Future-Facing Artifacts
- [ ] Template files (with `{{PLACEHOLDERS}}` for codegen)
- [ ] Validation rules (what to check in automated output)
- [ ] Design document for automation tool
- [ ] Possibly: Initial slash command or agent spec

---

## Anti-Goals (What We're NOT Doing)

**We are NOT:**
- ❌ Building production-quality code (this is a learning exercise)
- ❌ Optimizing for performance (we're optimizing for understanding)
- ❌ Writing the automation tool yet (we're discovering requirements)
- ❌ Covering every edge case (we're finding the happy path first)

**We ARE:**
- ✅ Learning by doing
- ✅ Documenting everything
- ✅ Finding the friction points
- ✅ Building examples for future reference

---

## Timeline & Checkpoints

**Checkpoint 1: Audit Complete**
- Know what exists, what needs creation
- Understand generated code structure
- Ready to start manual FSM work

**Checkpoint 2: FSM Drafted**
- Have working (or compiling) FSM
- Documented all design decisions
- Identified register wiring approach

**Checkpoint 3: Tests Created**
- Have test infrastructure in place
- At least one test running (pass or fail)
- Documented test generation process

**Checkpoint 4: Retrospective**
- Reviewed all notes and artifacts
- Categorized work into automatable/manual/template-able
- Outlined next steps toward automation

---

## Notes Section (To Be Filled During Dry-Run)

### Design Decisions
_As we make decisions, document them here with rationale._

### Pain Points Encountered
_Track what was frustrating, tedious, or confusing._

### Insights & Discoveries
_Unexpected learnings, happy accidents, "aha!" moments._

### Automation Opportunities
_Specific tasks that could be automated with high confidence._

---

**Created:** 2025-11-05
**Session:** session/2025-11-05-integration-testing
**Type:** Experimental / Discovery
**Outcome:** TBD (will be updated at session end)
