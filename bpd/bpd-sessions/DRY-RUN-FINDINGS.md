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

**Status:** ✅ RESOLVED - User provided authoritative interface

**Resolution:** (2025-11-05, during P2 phase)

User provided the **SimpleCustomInstrument** entity definition, which is the wrapper interface that Moku cloud compiler expects:

```vhdl
entity SimpleCustomInstrument is
    Port (
        Clk   : in std_logic;
        Reset : in std_logic;

        -- ADC Inputs (from Moku analog inputs)
        InputA : in signed(15 downto 0);
        InputB : in signed(15 downto 0);
        InputC : in signed(15 downto 0);

        -- DAC Outputs (to Moku analog outputs)
        OutputA : out signed(15 downto 0);
        OutputB : out signed(15 downto 0);
        OutputC : out signed(15 downto 0);

        -- Control Registers (CR0-CR15)
        Control0  : in std_logic_vector(31 downto 0);
        Control1  : in std_logic_vector(31 downto 0);
        -- ... through ...
        Control15 : in std_logic_vector(31 downto 0)
    );
end SimpleCustomInstrument;
```

**Key Findings:**

1. **Register Mapping:**
   - CR0-CR5: Reserved for VOLO control system
   - CR6-CR12: Application registers (our 13 YAML fields)
   - CR13-CR15: Unused
   - Generated shim maps Control6-12 → app_reg_6-12 → typed signals

2. **Architecture Layers:**
   ```
   SimpleCustomInstrument (top-level wrapper)
       └─ instantiates → basic_probe_driver_custom_inst_shim.vhd
           └─ instantiates → basic_probe_driver_custom_inst_main.vhd (FSM)
   ```

3. **For P2 (VHDL FSM):**
   - Implement FSM in `basic_probe_driver_custom_inst_main.vhd`
   - Shim already handles Control→app_reg→typed signal mapping
   - No need to modify shim (generated, read-only)

4. **For P3 (CocoTB Testing):**
   - Create SimpleCustomInstrument wrapper
   - Wire Control6-12 to shim's app_reg_6-12 inputs
   - This becomes the DUT for CocoTB tests

**P2 Action:** Continue with FSM implementation in `_main.vhd` template.

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

### 🟢 KINK #3: Python Layer Had No Register Definitions (RESOLVED)

**Discovered:** 2025-11-05 (During P1 - Python Register Alignment)

**Problem:**
The existing Python codebase (`bpd-core`, `bpd-drivers`, `bpd-examples`) had **no implementation of the 13 YAML register fields**. The code only provided:
- Generic probe interface (`set_voltage`, `set_pulse_width`, `arm`, etc.)
- Basic validation helpers
- DS1120A driver stub

**Missing:**
- All 13 register field definitions from `basic_probe_driver.yaml`
- Validation logic for YAML-specified ranges
- Unit conversion helpers (mV, ns, μs, s ↔ hardware)
- Examples demonstrating full register interface

**Root Cause:**
The Python layer was created as a generic probe abstraction before the YAML spec was finalized with specific register fields.

**Resolution (P1 Phase):**
Created complete Python implementation:

**Files Created:**
- `bpd/bpd-core/src/bpd_core/registers.py` - All 13 register fields with validation
- `bpd/bpd-examples/basic_probe_driver_example.py` - Comprehensive example

**Files Modified:**
- `bpd/bpd-core/src/bpd_core/__init__.py` - Export `BasicProbeDriverRegisters`
- `bpd/bpd-core/src/bpd_core/validation.py` - Add unit conversion helpers

**Implementation Details:**

1. **Register Class:** `BasicProbeDriverRegisters`
   - All 13 fields as properties with getters/setters
   - Validation enforces YAML min/max ranges
   - Defaults match YAML `default_value` exactly
   - Read-only `probe_monitor_feedback` (hardware updates via internal method)

2. **Validation:**
   - Voltage ranges: -5000 to 5000 mV
   - Timing ranges per YAML spec (ns, μs, s)
   - Type checking (bool fields reject non-bool)
   - Clear error messages with actual values

3. **Unit Conversion Helpers:**
   - `mV_to_volts()` / `volts_to_mV()`
   - `ns_to_cycles()` / `cycles_to_ns()`
   - `us_to_cycles()` / `cycles_to_us()`
   - `s_to_cycles()` / `cycles_to_s()`
   - All assume 125 MHz clock (configurable parameter)

4. **Example Code:**
   - Demonstrates all 13 fields grouped by purpose
   - Shows validation in action (catches invalid values)
   - Includes unit conversion examples
   - Exports full register dump via `to_dict()`

**Workflow Implications:**

✅ **GOOD NEWS:**
- Python layer now 100% aligned with YAML spec
- P2 agent can reference this as the API contract
- Clear boundary: Python uses real units (mV, ns), VHDL does conversion

⚠️ **DESIGN DECISIONS:**

1. **Unit Boundary:**
   - **Decision:** Python keeps real units (mV, ns, μs, s)
   - **Rationale:** More intuitive for users, matches YAML
   - **Conversion:** Happens at hardware boundary (VHDL FSM)

2. **Read-Only Feedback:**
   - **Decision:** `probe_monitor_feedback` has no public setter
   - **Rationale:** This is an output from hardware
   - **Implementation:** Internal `_set_probe_monitor_feedback()` for hardware updates

3. **Validation Strictness:**
   - **Decision:** Raise exceptions on invalid values
   - **Rationale:** Fail fast, prevent unsafe hardware configs
   - **Alternative considered:** Clamp values silently (rejected - hides errors)

**Questions for P2 (VHDL Agent):**

1. **Clock Frequency:** Assuming 125 MHz (Moku default) - is this correct for all platforms?
2. **Unit Conversion:** Should VHDL FSM use `ns/μs/s` directly or convert to cycles?
3. **Register Interface:** How do 13 fields map to generated `*_shim.vhd` ports?
4. **Read-Only Registers:** How does hardware write to `probe_monitor_feedback`?

**Commit:** f1610c5 - "P1: Align Python layer with basic_probe_driver.yaml spec"

**Status:** ✅ P1 COMPLETE - Ready for P2 handoff

---

### 🟡 KINK #4: Claude Code Web Sandbox Branch Isolation (WORKFLOW)

**Discovered:** 2025-11-05 (During P1 git push attempt)

**Problem:**
Claude Code web edition uses a **sandbox git proxy** that enforces branch naming conventions. This caused confusion when trying to push commits from the "natural" session branch.

**Symptoms:**
- User created branch: `session/2025-11-05-integration-testing-claude-web-ai`
- Claude Code works on this branch fine (commits succeed)
- `git push` fails with **HTTP 403 error**
- Confusing because branch exists on remote

**Root Cause:**
Claude Code web sandbox creates an **isolation layer** for safety:
- Sandbox allows only branches matching pattern: `claude/<name>-<session_id>`
- Session ID is auto-generated (e.g., `011CUq6RLYd9Bum3CJ6SbCyL`)
- User-created branches (e.g., `session/*`) can't push directly
- Remote proxy at `127.0.0.1:<port>` enforces this

**The Sandbox Setup:**
```
User's GitHub Repo (sealablab/BPD-002)
          ↓ (cloned into sandbox)
Local Proxy (127.0.0.1:<port>/git/sealablab/BPD-002)
          ↓ (branch filtering)
Claude's Workspace
   - Can read: any branch
   - Can commit: any local branch
   - Can push: ONLY claude/<name>-<session_id>
```

**What We Encountered:**

1. **User's Intent:**
   - Work on `session/2025-11-05-integration-testing-claude-web-ai`
   - This branch has all the planning docs and context
   - Natural choice for the session

2. **Sandbox Reality:**
   - Sandbox **also** created `claude/integration-testing-web-ai-011CUq6RLYd9Bum3CJ6SbCyL`
   - Claude can read/work on ANY branch
   - But can only **push** to the `claude/` branch

3. **Initial Attempt:**
   ```bash
   git push -u origin session/2025-11-05-integration-testing-claude-web-ai
   # ERROR: HTTP 403
   ```

4. **The Fix:**
   ```bash
   # Switch to the claude/ branch
   git checkout claude/integration-testing-web-ai-011CUq6RLYd9Bum3CJ6SbCyL

   # Cherry-pick commits from session branch
   git cherry-pick f1610c5 c8bea21

   # Now push succeeds
   git push -u origin claude/integration-testing-web-ai-011CUq6RLYd9Bum3CJ6SbCyL
   # ✓ SUCCESS
   ```

**Workflow Implications:**

⚠️ **For Users (Outside World):**

**Strategy 1: Work on session branch, sync later (RECOMMENDED)**
- Let Claude work on your meaningful branch (`session/*`, `feature/*`, etc.)
- Commits happen locally on that branch
- At end of session: **YOU** handle merging to main/desired branch
- Pros: Clean history, meaningful branch names
- Cons: User must manually handle git after session

**Strategy 2: Accept the claude/ branch**
- Let Claude work directly on `claude/<name>-<session_id>`
- Commits auto-push during session
- After session: merge `claude/*` branch to main
- Pros: Auto-push works, no manual git
- Cons: Opaque branch names, harder to track history

**Strategy 3: Hybrid approach (what we did)**
- Claude works on meaningful branch locally
- At completion points, cherry-pick to `claude/` branch
- Push the `claude/` branch for backup
- User later merges from meaningful branch
- Pros: Best of both worlds
- Cons: Some manual git juggling

⚠️ **For Claude (AI Agents):**

**Detection:**
When `git push` fails with 403:
1. Check current branch name
2. Look for `claude/<name>-<session_id>` branch
3. Switch to that branch
4. Cherry-pick recent commits
5. Retry push

**Better pattern:**
```bash
# At session start, detect the situation
CURRENT_BRANCH=$(git branch --show-current)
CLAUDE_BRANCH=$(git branch -a | grep 'claude/.*-[A-Za-z0-9]\{24\}$' | head -1 | sed 's/.*\///')

if [[ "$CURRENT_BRANCH" != "$CLAUDE_BRANCH" ]]; then
    echo "⚠️  Working on $CURRENT_BRANCH but can only push to $CLAUDE_BRANCH"
    echo "Strategy: Commit locally, cherry-pick to $CLAUDE_BRANCH for push"
fi
```

**Documentation Pattern:**
```markdown
## Git Workflow Note (Claude Code Web Edition)

This session uses Claude Code web sandbox, which isolates pushes to:
- Branch: `claude/integration-testing-web-ai-011CUq6RLYd9Bum3CJ6SbCyL`

Work happens on: `session/2025-11-05-integration-testing-claude-web-ai`
Commits synced to `claude/` branch for pushing.

After session, user should merge from session branch (cleaner history).
```

**Why This Design Makes Sense:**

1. **Safety:** Prevents Claude from pushing to `main` or other critical branches
2. **Isolation:** Each session gets unique branch, easy to track/rollback
3. **Audit Trail:** Session ID in branch name enables tracking
4. **Collaboration:** Multiple concurrent sessions won't conflict

**However, it creates UX friction:**
- Branch names are opaque (session ID not meaningful)
- Users must understand the isolation model
- Extra git commands needed (cherry-pick, merge)

**Recommendation for Future:**

**For Repository Setup:**
Add to repository root: `.claude-code/README.md`
```markdown
## Working with Claude Code Web Edition

This repo may be accessed by Claude Code web sandbox.

### Branch Naming
- Sandbox pushes to: `claude/<name>-<session_id>`
- Session IDs are auto-generated (24 char alphanumeric)

### After Claude Session
1. Review commits on `claude/<name>-<session_id>` branch
2. Merge to main or feature branch as appropriate
3. Delete `claude/` branch after merge (or keep for audit)

### Branch Cleanup
```bash
# List all claude/ branches
git branch -r | grep claude/

# Delete merged claude/ branches
git push origin --delete claude/<name>-<session_id>
```
```

**Status:** ✅ WORKAROUND FOUND - Documented for future sessions

---

### 🟢 KINK #5: GHDL Installation Blocker for VHDL Testing (RESOLVED)

**Discovered:** 2025-11-05 (During P2 preparation)

**Problem:**
GHDL (VHDL compiler/simulator) is **required** for P2 (VHDL FSM implementation) and P3 (CocoTB testing), but it's not installable via pip/uv. This is a **system-level dependency** that blocks VHDL development workflow.

**Why This is a Blocker:**
- CocoTB (already in dependencies) needs GHDL backend to simulate VHDL
- Cannot compile/test VHDL code without GHDL
- Not documented anywhere in project setup
- New developers would hit this wall immediately

**Root Cause:**
GHDL is a compiled binary (C++/Ada) with system dependencies:
- Requires LLVM or GCC compiler infrastructure
- Platform-specific builds (x86, ARM)
- Too large/complex for PyPI distribution
- Must be installed via system package manager

**Impact on Workflow:**
```
P1: Python ✅ (works fine)
    ↓
P2: VHDL FSM ❌ (blocked without GHDL)
    ↓
P3: CocoTB Tests ❌ (blocked without GHDL)
```

---

## ✅ RESOLUTION: Comprehensive GHDL Setup Solution

### Step 1: Installation Documentation

**Created:** `docs/GHDL_SETUP.md`

**Contents:**
- Quick install command (copy-paste ready)
- Backend options explained (LLVM/mcode/GCC)
- CocoTB integration guide
- Troubleshooting common issues
- CI/CD examples for GitHub Actions

**Quick Install (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install -y ghdl-llvm  # Recommended: LLVM backend
```

**Verify Installation:**
```bash
ghdl --version
# Should show: GHDL 2.0.0 ... llvm code generator
```

---

### Step 2: Project Integration

**Modified:** `pyproject.toml`

**Added optional dependency group:**
```toml
# VHDL SIMULATION EXTRAS
# NOTE: Requires GHDL system package (not installable via pip)
# Install GHDL: sudo apt-get install ghdl-llvm
# See: docs/GHDL_SETUP.md

[project.optional-dependencies.vhdl-dev]
pytest-cov = ">=4.0.0"  # Coverage for VHDL test Python wrappers
```

**Why optional-dependencies?**
- Clearly separates Python deps from system deps
- Documents that GHDL is required but not pip-installable
- Points developers to installation guide
- Follows uv best practices for "extras"

**Usage:**
```bash
# Install with VHDL development extras
uv sync --extra vhdl-dev
```

---

### Step 3: Developer Experience Enhancement

**Modified:** `setup.sh`

**Added GHDL check:**
```bash
# Check for GHDL (optional, for VHDL testing)
if ! command_exists ghdl; then
    echo "⚠️  GHDL not found - VHDL simulation tests will be skipped"
    echo "   Install with: sudo apt-get install ghdl-llvm"
    echo "   See: docs/GHDL_SETUP.md for full setup guide"
    echo ""
fi
```

**Behavior:**
- Non-blocking warning (doesn't exit)
- Clear install command provided
- Points to comprehensive docs
- Developers know immediately what's missing

---

### Step 4: Workflow Integration

**How It Works Now:**

1. **New Developer Setup:**
   ```bash
   ./setup.sh
   # Sees GHDL warning if not installed
   # Follows link to docs/GHDL_SETUP.md
   # Runs: sudo apt-get install ghdl-llvm
   # Re-runs ./setup.sh (warning gone)
   ```

2. **VHDL Development:**
   ```bash
   # Compile VHDL
   ghdl -a --std=08 my_design.vhd

   # Run CocoTB tests
   cd bpd/bpd-vhdl/tests
   pytest test_fi_interface.py -v
   ```

3. **CI/CD (GitHub Actions):**
   ```yaml
   - name: Install GHDL
     run: sudo apt-get install -y ghdl-llvm

   - name: Run VHDL tests
     run: pytest bpd/bpd-vhdl/tests/ -v
   ```

---

## Key Design Decisions

### Decision 1: Optional Dependency Group (Not Hard Requirement)

**Rationale:**
- Python developers may not need VHDL testing
- System package can't be enforced via pip/uv
- Better to document clearly than fail mysteriously

**Alternative Considered:** Hard requirement
- **Rejected:** Would block all `uv sync` commands
- Better to warn than block

### Decision 2: LLVM Backend (Recommended)

**Options:**
1. `ghdl-llvm` ← **Recommended**
2. `ghdl-mcode` (faster install, slower sim)
3. `ghdl-gcc` (maximum compatibility, slowest)

**Rationale:**
- LLVM backend: Good balance of speed/compatibility
- Most common in modern FPGA workflows
- Well-tested with CocoTB

### Decision 3: Documentation-First Approach

**Strategy:**
- Comprehensive `docs/GHDL_SETUP.md` as single source of truth
- `pyproject.toml` points to it
- `setup.sh` points to it
- README (future) will point to it

**Rationale:**
- Easier to maintain one detailed doc
- Developers need troubleshooting info
- CI/CD examples valuable for automation

---

## For Future Automation

**Potential Enhancements:**

1. **Docker Container:**
   ```dockerfile
   FROM ubuntu:22.04
   RUN apt-get install -y ghdl-llvm python3 uv
   # Pre-baked environment with GHDL
   ```

2. **Devcontainer (VS Code):**
   ```json
   {
     "image": "bpd-dev:latest",
     "features": {
       "ghcr.io/devcontainers/features/ghdl:1": {}
     }
   }
   ```

3. **Automated Detection:**
   ```python
   # In test conftest.py
   import shutil
   import pytest

   def pytest_configure(config):
       if not shutil.which("ghdl"):
           pytest.skip("GHDL not found - skipping VHDL tests")
   ```

---

## Verification Checklist

After following these steps, verify:

- [ ] `ghdl --version` shows LLVM backend
- [ ] `./setup.sh` runs without GHDL warning
- [ ] `uv sync --extra vhdl-dev` succeeds
- [ ] CocoTB can import: `python -c "import cocotb; print(cocotb.__version__)"`
- [ ] Can compile test VHDL: `ghdl -a --std=08 test.vhd`

**Test VHDL compilation:**
```bash
echo "entity test is end test;" > test.vhd
ghdl -a --std=08 test.vhd && echo "✅ GHDL works!"
rm test.vhd test.o
```

---

## Documentation Files Created

**Commit:** `8700f5a` - "Add GHDL installation documentation and setup checks"

**Files:**
1. `docs/GHDL_SETUP.md` (254 lines)
   - Complete installation guide
   - Multiple backend options
   - Troubleshooting section
   - CI/CD integration examples

2. `pyproject.toml` (modified)
   - Added `[project.optional-dependencies.vhdl-dev]`
   - Clear comment about system requirement

3. `setup.sh` (modified)
   - Added GHDL detection
   - Helpful install message

**Status:** ✅ RESOLVED - Ready for P2 VHDL development

**Next:** Can proceed with FSM implementation using GHDL for compilation checks.

---

**Next Kink ID:** #6
**Status:** P2 in progress - GHDL blocker resolved, ready for FSM implementation

