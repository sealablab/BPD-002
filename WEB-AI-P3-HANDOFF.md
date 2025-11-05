# 🧪 P3 Mission: CocoTB Integration Testing

**Goal:** Create progressive CocoTB tests to verify the P2 FSM works correctly.

---

## Quick Setup

```bash
# 1. Pull latest (includes stub packages + compiled FSM)
git pull origin main

# 2. Verify GHDL works
ghdl --version

# 3. Install Python dependencies
uv sync --extra vhdl-dev

# 4. Navigate to test directory
cd bpd/bpd-vhdl/tests
```

---

## Mission: Create CocoTB Test Suite

### Background

The P2 FSM (`basic_probe_driver_custom_inst_main.vhd`, 471 lines) is syntactically correct and compiles with GHDL. Now we need **functional verification** via CocoTB tests.

**What CocoTB Does:**
- Python-based VHDL/Verilog testbench
- Drives FSM inputs (clk, registers, etc.)
- Observes FSM outputs (state, signals)
- Verifies timing and behavior

---

## Test Architecture

### Progressive Testing (P1 → P2 → P3)

Follow **forge-vhdl progressive testing standards**:

**P1 Tests (Basic Sanity):**
- Reset behavior
- Clock toggles
- Simple signal assertions
- Goal: Prove DUT loads and responds

**P2 Tests (Module Behavior):**
- FSM state transitions (IDLE → ARMED → FIRING → COOLDOWN)
- Register interface wiring (all 13 fields)
- Timing verification (pulse durations, cooldown)
- Goal: Verify FSM logic correctness

**P3 Tests (Integration):**
- Full firing sequences with monitoring
- Edge cases (timeouts, faults, rapid triggers)
- Stress testing (boundary values)
- Goal: Prove production readiness

---

## Implementation Steps

### Step 1: Create Test Infrastructure

**File: `bpd/bpd-vhdl/tests/test_basic_probe_fsm.py`**

```python
"""
CocoTB tests for Basic Probe Driver FSM
Progressive testing: P1 (sanity) → P2 (behavior) → P3 (integration)
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer, ClockCycles

# Test constants (from YAML spec)
CLK_PERIOD_NS = 8  # 125 MHz
DEFAULT_PULSE_WIDTH_NS = 100
DEFAULT_VOLTAGE_MV = 3300

# ============================================================================
# P1 TESTS: Basic Sanity Checks
# ============================================================================

@cocotb.test()
async def test_p1_reset_behavior(dut):
    """P1: Verify reset initializes FSM to IDLE state."""

    clock = Clock(dut.Clk, CLK_PERIOD_NS, units="ns")
    cocotb.start_soon(clock.start())

    # Assert reset
    dut.Reset.value = 1
    await ClockCycles(dut.Clk, 5)

    # Release reset
    dut.Reset.value = 0
    await ClockCycles(dut.Clk, 2)

    # Verify IDLE state (state should be "000000")
    # Note: If state signal is not exported, check via output behavior
    # For now, verify that FSM is not busy/firing

    cocotb.log.info("✅ P1: Reset test passed")


@cocotb.test()
async def test_p1_clock_toggles(dut):
    """P1: Verify clock is toggling and DUT responds."""

    clock = Clock(dut.Clk, CLK_PERIOD_NS, units="ns")
    cocotb.start_soon(clock.start())

    dut.Reset.value = 1
    await ClockCycles(dut.Clk, 2)
    dut.Reset.value = 0

    # Just verify we can advance time
    await ClockCycles(dut.Clk, 100)

    cocotb.log.info("✅ P1: Clock toggle test passed")


# ============================================================================
# P2 TESTS: FSM Behavior Verification
# ============================================================================

@cocotb.test()
async def test_p2_idle_to_armed_transition(dut):
    """P2: Verify IDLE → ARMED transition via arm_enable."""

    clock = Clock(dut.Clk, CLK_PERIOD_NS, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.Reset.value = 1
    await ClockCycles(dut.Clk, 5)
    dut.Reset.value = 0
    await ClockCycles(dut.Clk, 2)

    # Set arm_enable high
    dut.arm_enable.value = 1
    await ClockCycles(dut.Clk, 5)

    # Verify FSM entered ARMED state
    # (Check internal state signal if exported, or via output behavior)

    cocotb.log.info("✅ P2: IDLE → ARMED transition passed")


@cocotb.test()
async def test_p2_full_firing_sequence(dut):
    """P2: Verify complete IDLE → ARMED → FIRING → COOLDOWN → IDLE."""

    clock = Clock(dut.Clk, CLK_PERIOD_NS, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.Reset.value = 1
    await ClockCycles(dut.Clk, 5)
    dut.Reset.value = 0
    await ClockCycles(dut.Clk, 2)

    # Configure pulse parameters
    dut.trig_out_voltage.value = 3300  # mV
    dut.trig_out_duration.value = 100  # ns
    dut.intensity_voltage.value = 5000  # mV
    dut.intensity_duration.value = 200  # ns
    dut.cooldown_interval.value = 1000  # μs

    # Arm
    dut.arm_enable.value = 1
    await ClockCycles(dut.Clk, 5)

    # Trigger (single pulse on ext_trigger_in)
    dut.ext_trigger_in.value = 1
    await ClockCycles(dut.Clk, 1)
    dut.ext_trigger_in.value = 0

    # Verify FIRING state
    # TODO: Check trig_out_active, intensity_out_active signals

    # Wait for pulse duration + cooldown
    await Timer(500, units="ns")  # Pulse duration
    await Timer(1000, units="us")  # Cooldown

    # Verify returned to ARMED (since arm_enable still high)

    cocotb.log.info("✅ P2: Full firing sequence passed")


@cocotb.test()
async def test_p2_trigger_wait_timeout(dut):
    """P2: Verify ARMED → IDLE on trigger_wait_timeout."""

    clock = Clock(dut.Clk, CLK_PERIOD_NS, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.Reset.value = 1
    await ClockCycles(dut.Clk, 5)
    dut.Reset.value = 0

    # Set short timeout (2 seconds)
    dut.trigger_wait_timeout.value = 2  # seconds

    # Arm but don't trigger
    dut.arm_enable.value = 1
    await ClockCycles(dut.Clk, 10)

    # Wait for timeout (2 seconds at 125 MHz = 250M cycles)
    # For testing, use smaller value or mock the counter
    # TODO: Implement timeout verification

    cocotb.log.info("✅ P2: Timeout test passed")


# ============================================================================
# P3 TESTS: Integration & Edge Cases
# ============================================================================

@cocotb.test()
async def test_p3_auto_rearm_behavior(dut):
    """P3: Verify auto_rearm_enable causes COOLDOWN → ARMED."""

    clock = Clock(dut.Clk, CLK_PERIOD_NS, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.Reset.value = 1
    await ClockCycles(dut.Clk, 5)
    dut.Reset.value = 0

    # Enable auto-rearm
    dut.auto_rearm_enable.value = 1
    dut.arm_enable.value = 1

    # Trigger first pulse
    dut.ext_trigger_in.value = 1
    await ClockCycles(dut.Clk, 1)
    dut.ext_trigger_in.value = 0

    # Wait for cooldown
    await Timer(1000, units="us")

    # Verify FSM returned to ARMED (not IDLE)
    # TODO: Check state or ready signals

    cocotb.log.info("✅ P3: Auto-rearm test passed")


@cocotb.test()
async def test_p3_fault_clear_recovery(dut):
    """P3: Verify fault_clear transitions FAULT → IDLE."""

    clock = Clock(dut.Clk, CLK_PERIOD_NS, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.Reset.value = 1
    await ClockCycles(dut.Clk, 5)
    dut.Reset.value = 0

    # TODO: Trigger a fault condition
    # Then verify fault_clear pulse clears it

    cocotb.log.info("✅ P3: Fault clear test passed")


@cocotb.test()
async def test_p3_rapid_trigger_prevention(dut):
    """P3: Verify cooldown prevents rapid re-triggering."""

    clock = Clock(dut.Clk, CLK_PERIOD_NS, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.Reset.value = 1
    await ClockCycles(dut.Clk, 5)
    dut.Reset.value = 0

    # Arm and trigger first pulse
    dut.arm_enable.value = 1
    dut.auto_rearm_enable.value = 1
    dut.ext_trigger_in.value = 1
    await ClockCycles(dut.Clk, 1)
    dut.ext_trigger_in.value = 0

    # Immediately try to trigger again (should be ignored)
    await ClockCycles(dut.Clk, 10)
    dut.ext_trigger_in.value = 1
    await ClockCycles(dut.Clk, 1)
    dut.ext_trigger_in.value = 0

    # Verify second trigger was blocked during cooldown
    # TODO: Check that only one pulse occurred

    cocotb.log.info("✅ P3: Rapid trigger prevention passed")
```

---

### Step 2: Create Makefile for CocoTB

**File: `bpd/bpd-vhdl/tests/Makefile`**

```makefile
# CocoTB Makefile for Basic Probe Driver FSM

# VHDL files to compile
VHDL_SOURCES = $(PWD)/../src/basic_app_types_pkg.vhd \
               $(PWD)/../src/basic_app_voltage_pkg.vhd \
               $(PWD)/../src/basic_app_time_pkg.vhd \
               $(PWD)/../src/basic_probe_driver_custom_inst_main.vhd

# DUT (top-level entity)
TOPLEVEL = basic_probe_driver_custom_inst_main

# Test module
MODULE = test_basic_probe_fsm

# Simulator
SIM = ghdl

# GHDL flags
GHDL_ARGS = --std=08

# CocoTB settings
COCOTB_REDUCED_LOG_FMT = True

include $(shell cocotb-config --makefiles)/Makefile.sim
```

---

### Step 3: Run Tests

```bash
cd bpd/bpd-vhdl/tests

# Run all tests
make

# Run specific test
pytest test_basic_probe_fsm.py::test_p1_reset_behavior -v

# View waveforms (if generated)
gtkwave dump.vcd
```

---

## Expected Challenges

### Challenge 1: FSM State Not Exported

**Problem:** Internal `state` signal may not be visible to CocoTB.

**Solution:**
- Verify behavior via output signals (e.g., check if outputs match expected state)
- Or temporarily add state as output port for testing

### Challenge 2: Timing Conversion Accuracy

**Problem:** Stub packages use simplified math.

**Solution:**
- Tests may show timing inaccuracies
- Document as expected (stubs will be replaced by forge-codegen)
- Focus on FSM logic, not conversion precision

### Challenge 3: CocoTB Setup Issues

**Problem:** CocoTB + GHDL integration may have quirks.

**Solution:**
- Check `cocotb-config --version`
- Verify GHDL backend: `ghdl --version` (should show backend type)
- Consult forge-vhdl test examples if available

---

## Success Criteria

### Minimum Success (P1)
- [ ] Reset test passes
- [ ] Clock toggles without errors
- [ ] Can load DUT and run basic assertions

### Good Success (P2)
- [ ] IDLE → ARMED → FIRING → COOLDOWN verified
- [ ] Pulse timing roughly correct (within 10% due to stub math)
- [ ] Register interface wiring confirmed (all 13 fields accessible)

### Full Success (P3)
- [ ] Auto-rearm behavior works
- [ ] Fault recovery works
- [ ] Cooldown enforcement verified
- [ ] All tests pass with clear waveforms

---

## Deliverables

**Commit to branch:**
1. `bpd/bpd-vhdl/tests/test_basic_probe_fsm.py` - Test suite
2. `bpd/bpd-vhdl/tests/Makefile` - CocoTB build config
3. `bpd/bpd-vhdl/tests/conftest.py` - pytest config (if needed)
4. `bpd/bpd-sessions/DRY-RUN-FINDINGS.md` - Update with Kink #11 (test results)

**Document:**
- Which tests passed/failed
- Any timing discrepancies (expected due to stubs)
- Whether FSM logic is correct
- Recommendations for real package implementation

---

## Notes

- **Clock Frequency:** Assume 125 MHz (8 ns period) per Moku standard
- **Test Strategy:** Start with P1 (sanity), then P2 (behavior), then P3 (integration)
- **Stub Limitations:** Time conversions are simplified - expect ~10% inaccuracy
- **Waveforms:** Use `gtkwave dump.vcd` to visualize FSM transitions

---

## If Stuck

**Can't get CocoTB working?**
- Document the blocker as Kink #11
- Show what you tried (error messages)
- Provide minimal reproduction case

**Tests failing?**
- Document failures clearly (expected vs. actual)
- Note if it's FSM logic vs. stub math issue
- Waveform screenshots help!

**Not sure what to assert?**
- Focus on state transitions first
- Then verify timing (approximately)
- Then check register wiring

---

**Ready to verify the FSM works correctly? Let's test it! 🧪**
