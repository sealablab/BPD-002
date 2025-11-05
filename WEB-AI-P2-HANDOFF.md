# Web AI P2 Handoff: VHDL FSM Implementation

**Date:** 2025-11-05
**Session:** P2 (VHDL FSM Implementation)
**Branch:** `main` (ready for P2 work)

---

## Quick Start

```bash
# 1. Checkout main branch
git checkout main

# 2. Run sandbox reconnaissance (helpful for debugging)
bash tools/sandbox-recon.sh > sandbox-info.txt
cat sandbox-info.txt  # Review what environment you're in

# 3. Run setup with GHDL auto-install
./setup.sh --install-ghdl

# 4. Verify GHDL installed
ghdl --version
# Should show: GHDL 2.0.0+ with llvm code generator

# 5. If GHDL install failed, attach sandbox-info.txt to your findings
# Document as kink in DRY-RUN-FINDINGS.md

# 6. Start P2 implementation
# Follow: bpd/agents/vhdl-fsm-implementation/agent.md
```

---

## What's Already Done

### ✅ P1 Complete - Python Register Alignment
- **File:** `bpd/bpd-core/src/bpd_core/registers.py` (364 lines)
  - All 13 YAML register fields implemented
  - Property accessors with validation
  - Type hints throughout

- **File:** `bpd/bpd-core/src/bpd_core/validation.py` (153 lines)
  - Unit conversion helpers (mV→V, ns→cycles, etc.)
  - Validation utilities

- **File:** `bpd/bpd-examples/basic_probe_driver_example.py` (158 lines)
  - Comprehensive usage example
  - Demonstrates all 13 register fields

### ✅ Kinks Documented (5 total)
See `bpd/bpd-sessions/DRY-RUN-FINDINGS.md` for details:
1. Kink #1: Stale FSM (archived to `fi_probe_interface.vhd.old_pre_yaml`)
2. Kink #2: CustomInstrument Wrapper (SimpleCustomInstrument pattern)
3. Kink #3: Python Layer Gap (resolved in P1)
4. Kink #4: Git Sandbox Isolation (web/CLI handoff pattern discovered)
5. Kink #5: GHDL Installation (docs + auto-install added)

### ✅ Infrastructure Ready
- GHDL setup documentation: `docs/GHDL_SETUP.md`
- Auto-install flag: `./setup.sh --install-ghdl`
- All submodules initialized
- Python dependencies installed

---

## Your Mission: P2 - VHDL FSM Implementation

### Agent Spec
**Read this first:** `bpd/agents/vhdl-fsm-implementation/agent.md`

This contains your complete task specification:
- FSM states to implement
- Register interface requirements
- Timing counter specifications
- GHDL compilation commands
- Commit message templates

### Key Files to Create/Modify

**Main FSM file:**
```
bpd/bpd-vhdl/src/basic_probe_driver_custom_inst_main.vhd
```

This must implement:
- 5 FSM states: IDLE, ARMED, FIRING, COOLDOWN, FAULT
- Interface to 13 register fields (from YAML spec)
- Timing counters (ns/μs/s conversion)
- Probe monitoring/comparator logic

**Use these references:**
- YAML spec: `bpd/bpd-specs/basic_probe_driver.yaml`
- Generated shim: `bpd/bpd-specs/generated/basic_probe_driver_custom_inst_shim.vhd`
- Python registers: `bpd/bpd-core/src/bpd_core/registers.py`
- Coding standards: `libs/forge-vhdl/CLAUDE.md`

---

## GHDL Installation

### The setup.sh Flag
```bash
./setup.sh --install-ghdl
```

This will:
1. Check if GHDL already installed
2. Detect package manager (apt-get/brew)
3. Auto-install ghdl-llvm
4. Verify installation

### If Auto-Install Fails

**First: Run reconnaissance script**
```bash
bash tools/sandbox-recon.sh > sandbox-info.txt
```

This will tell you:
- What OS/package manager is available
- Whether you have sudo access
- If GHDL packages are available
- What the recommended install command is

**Then: Try manual install**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y ghdl-llvm

# Verify
ghdl --version
```

**If still failing:**
1. Save `sandbox-info.txt`
2. Document as "Kink #6: GHDL Installation in Web Sandbox"
3. Include recon output in your findings
4. Continue with FSM design (can test compilation later)

**See:** `docs/GHDL_SETUP.md` for troubleshooting

---

## Expected Workflow

### 1. Setup (5 min)
```bash
git checkout main
./setup.sh --install-ghdl
ghdl --version  # Verify
```

### 2. Read Agent Spec (10 min)
```bash
cat bpd/agents/vhdl-fsm-implementation/agent.md
```

### 3. Implement FSM (60-90 min)
- Create `basic_probe_driver_custom_inst_main.vhd`
- Wire up all 13 registers
- Implement 5 FSM states
- Add timing counters

### 4. Test Compilation (10 min)
```bash
cd bpd/bpd-vhdl
ghdl -a --std=08 src/basic_probe_driver_custom_inst_main.vhd
```

### 5. Document Findings (15 min)
- Update `bpd/bpd-sessions/DRY-RUN-FINDINGS.md`
- Add any new kinks discovered
- Commit with template from agent spec

---

## Commit Message Template

From `bpd/agents/vhdl-fsm-implementation/agent.md`:

```
P2: Implement VHDL FSM for Basic Probe Driver

Implements 5-state FSM aligned with basic_probe_driver.yaml:
- States: IDLE, ARMED, FIRING, COOLDOWN, FAULT
- All 13 register fields wired
- Timing counters for ns/μs/s conversion
- Probe monitoring/comparator logic

GHDL compilation: [✓/✗]
forge-vhdl compliant: [✓/✗]

Next: P3 (CocoTB integration tests)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Success Criteria

### Minimum (P2 Complete)
- [ ] FSM file created with 5 states
- [ ] All 13 registers wired to FSM logic
- [ ] Timing counters implemented
- [ ] GHDL compiles without errors
- [ ] Committed with template message

### Stretch Goals
- [ ] Add fault detection logic
- [ ] Implement auto-rearm behavior
- [ ] Test with GHDL simulation (ghdl -r)
- [ ] Document design decisions in DRY-RUN-FINDINGS.md

---

## If You Get Stuck

### GHDL Not Installing?
1. Check `docs/GHDL_SETUP.md`
2. Document as new kink in DRY-RUN-FINDINGS.md
3. Continue with FSM design (can test compilation later)

### FSM Design Questions?
1. Reference Python `registers.py` for field definitions
2. Check YAML spec for operational flow
3. Look at `fi_probe_interface.vhd.old_pre_yaml` for inspiration (but don't copy - it's outdated)

### Compilation Errors?
1. Check forge-vhdl coding standards: `libs/forge-vhdl/CLAUDE.md`
2. Ensure VHDL-2008 syntax (no enums for states - use std_logic_vector)
3. Document specific errors as kink findings

---

## After P2 Completes

### Next Session: P3 (CocoTB Integration Tests)
**Agent spec:** `bpd/agents/cocotb-integration-test/agent.md`

Will test your FSM with:
- Python CocoTB testbenches
- Register read/write verification
- State transition testing
- Timing validation

---

## Notes

- **Rollback point:** Commit `4b0d6ca` (marked with 🔖 emoji)
- **Current branch:** `main` has P1 integrated
- **Session branch:** `session/2025-11-05-integration-testing` (can reference if needed)
- **Web session quirk:** Your branch will be `claude/integration-testing-web-ai-<session_id>`

---

**Good luck! You got this! 🚀**

Remember: Document kinks as you find them. The dry-run process is about discovering issues, not achieving perfection.

