# CLAUDE.md - BPD VHDL Components

## Project Overview

**bpd-vhdl** provides vendor-agnostic VHDL components for fault injection probe control on Moku FPGA platforms. The main component (`fi_probe_interface.vhd`) implements a standard FSM-based interface that works with EMFI, laser FI, voltage glitching, and RF injection probes.

**Purpose:** Bridge between Python driver layer (bpd-core/bpd-drivers) and physical probe hardware via Moku FPGA, providing:
- Standard control FSM (IDLE → ARMED → PULSE_ACTIVE → COOLDOWN)
- Configurable pulse timing and voltage control
- Safety interlocks (cooldown enforcement, fault detection)
- Status feedback to host software

**Part of:** BPD-002 (Basic Probe Driver) - Multi-vendor probe integration for Moku

**Design Philosophy:** Generic interface inspired by DS1120A (de facto standard), but vendor-agnostic for multi-probe support.

---

## Quick Start

### VHDL Integration

```vhdl
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

architecture rtl of my_moku_instrument is
    signal arm_signal : std_logic;
    signal trigger_signal : std_logic;
    signal pulse_width_reg : unsigned(15 downto 0);
    signal voltage_reg : unsigned(15 downto 0);

    signal probe_trigger_out : std_logic;
    signal probe_ready : std_logic;

begin
    probe_ctrl : entity work.fi_probe_interface
        generic map (
            PULSE_WIDTH_BITS => 16,
            VOLTAGE_BITS => 16,
            COOLDOWN_CYCLES => 125  -- 1μs @ 125MHz
        )
        port map (
            clk => clk_125mhz,
            rst_n => rst_n,
            trigger_in => trigger_signal,
            arm => arm_signal,
            pulse_width => pulse_width_reg,
            voltage_ctrl => voltage_reg,
            probe_trigger => probe_trigger_out,
            probe_pulse => open,
            probe_voltage => open,
            ready => probe_ready,
            busy => open,
            fault => open
        );

    -- Connect to Moku outputs
    OUT1 <= probe_trigger_out;
end architecture;
```

---

## Architecture

### FSM Design

**State Machine:** 4-state FSM for probe control

```
┌─────────┐
│  IDLE   │ ← Initial/safe state, ready=1
└────┬────┘
     │ arm=1
     ↓
┌─────────┐
│  ARMED  │ ← Waiting for trigger, armed=1
└────┬────┘
     │ trigger_in=1
     ↓
┌──────────────┐
│ PULSE_ACTIVE │ ← Generating pulse, busy=1
└──────┬───────┘
       │ pulse_width cycles elapsed
       ↓
┌──────────┐
│ COOLDOWN │ ← Safety delay, busy=1
└─────┬────┘
      │ cooldown cycles elapsed
      └──→ IDLE (if arm=0) or ARMED (if arm=1)
```

**State transitions:**
- `IDLE → ARMED`: Set `arm='1'`
- `ARMED → PULSE_ACTIVE`: Pulse `trigger_in='1'` (single cycle)
- `PULSE_ACTIVE → COOLDOWN`: Automatic after `pulse_width` cycles
- `COOLDOWN → IDLE/ARMED`: Automatic after `COOLDOWN_CYCLES`

**Safety features:**
- Cannot trigger unless armed
- Enforced cooldown prevents overheating
- Fault detection returns to IDLE

### Port Specifications

#### Generic Parameters

```vhdl
generic (
    PULSE_WIDTH_BITS : positive := 16;  -- Pulse duration resolution
    VOLTAGE_BITS     : positive := 16;  -- Voltage control resolution
    COOLDOWN_CYCLES  : positive := 125  -- Min cycles between pulses
);
```

**Typical values:**
- `PULSE_WIDTH_BITS=16`: 0-65535 ns resolution
- `VOLTAGE_BITS=16`: ±32767 for voltage control (signed)
- `COOLDOWN_CYCLES=125`: 1μs @ 125MHz clock

#### Input Ports

```vhdl
port (
    -- Clock and Reset
    clk    : in std_logic;               -- Moku clock (125MHz typical)
    rst_n  : in std_logic;               -- Active-low reset

    -- Control Inputs (from Moku registers)
    trigger_in   : in std_logic;         -- Trigger pulse (single cycle)
    arm          : in std_logic;         -- Arm signal (level)
    pulse_width  : in unsigned(PULSE_WIDTH_BITS-1 downto 0);  -- Pulse duration (ns)
    voltage_ctrl : in unsigned(VOLTAGE_BITS-1 downto 0);      -- Voltage control
```

**Control patterns:**
- `trigger_in`: Single-cycle pulse (edge-triggered)
- `arm`: Level signal (hold high to stay armed)
- `pulse_width`: Latched on trigger
- `voltage_ctrl`: Continuous (can change anytime)

#### Output Ports

```vhdl
    -- Probe Outputs (to physical probe hardware)
    probe_trigger  : out std_logic;         -- Digital trigger to probe
    probe_pulse    : out std_logic;         -- Pulse control signal
    probe_voltage  : out unsigned(VOLTAGE_BITS-1 downto 0);  -- Analog voltage control

    -- Status Outputs (to Moku registers)
    ready : out std_logic;                  -- Ready for arming (IDLE state)
    busy  : out std_logic;                  -- Pulse active or cooldown
    fault : out std_logic;                  -- Fault detected
);
```

**Output behavior:**
- `probe_trigger`: High during PULSE_ACTIVE state
- `probe_pulse`: Pulse control (probe-specific)
- `probe_voltage`: Passes through `voltage_ctrl`
- `ready`: '1' only in IDLE state
- `busy`: '1' during PULSE_ACTIVE or COOLDOWN
- `fault`: '1' if error detected

### Safety Mechanisms

**1. Cooldown Enforcement**

```vhdl
-- Enforced minimum delay between pulses
constant COOLDOWN_CYCLES : positive := 125;  -- 1μs @ 125MHz

-- FSM state: COOLDOWN
when COOLDOWN =>
    busy <= '1';
    if cooldown_counter >= COOLDOWN_CYCLES then
        if arm = '1' then
            state <= ARMED;  -- Re-arm if arm still high
        else
            state <= IDLE;   -- Return to idle
        end if;
    end if;
```

**Purpose:** Prevents:
- Probe overheating
- Excessive current draw
- Hardware damage from rapid pulses

**Cannot be bypassed:** Hard-coded in FSM

**2. Fault Detection**

```vhdl
-- Example fault conditions (probe-specific)
if (voltage_out_of_range or temperature_too_high) then
    fault <= '1';
    state <= IDLE;  -- Safe state
end if;
```

**Future enhancements:**
- Temperature monitoring
- Current limit detection
- Voltage range validation

**3. Arm-Before-Trigger**

```vhdl
-- Trigger only works in ARMED state
when ARMED =>
    if trigger_in = '1' then
        state <= PULSE_ACTIVE;  -- Transition to pulse
    end if;

-- In other states, trigger_in is ignored
```

**Purpose:** Prevents accidental triggers

---

## Integration Patterns

### Pattern 1: Moku Custom Instrument Integration

**Complete example:**

```vhdl
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity emfi_instrument is
    port (
        -- Moku system clock (125MHz for Moku Go)
        clk_125mhz : in std_logic;
        rst_n : in std_logic;

        -- Moku control registers (simplified)
        cr_arm          : in std_logic;
        cr_trigger      : in std_logic;
        cr_pulse_width  : in unsigned(15 downto 0);
        cr_voltage      : in unsigned(15 downto 0);

        -- Moku outputs (to probe)
        OUT1 : out std_logic;  -- Digital trigger
        OUT2 : out std_logic;  -- Pulse control

        -- Moku status registers
        sr_ready : out std_logic;
        sr_busy  : out std_logic;
        sr_fault : out std_logic
    );
end entity;

architecture rtl of emfi_instrument is
    signal probe_trigger : std_logic;
    signal probe_pulse : std_logic;
    signal probe_voltage : unsigned(15 downto 0);

begin
    -- Instantiate BPD VHDL interface
    probe_ctrl : entity work.fi_probe_interface
        generic map (
            PULSE_WIDTH_BITS => 16,
            VOLTAGE_BITS => 16,
            COOLDOWN_CYCLES => 125  -- 1μs cooldown
        )
        port map (
            clk => clk_125mhz,
            rst_n => rst_n,

            -- Control from Moku registers
            trigger_in => cr_trigger,
            arm => cr_arm,
            pulse_width => cr_pulse_width,
            voltage_ctrl => cr_voltage,

            -- Outputs to probe
            probe_trigger => probe_trigger,
            probe_pulse => probe_pulse,
            probe_voltage => probe_voltage,

            -- Status to Moku registers
            ready => sr_ready,
            busy => sr_busy,
            fault => sr_fault
        );

    -- Connect to Moku physical outputs
    OUT1 <= probe_trigger;
    OUT2 <= probe_pulse;

    -- Note: probe_voltage would go to DAC if analog control needed
end architecture;
```

### Pattern 2: Python Control Flow

**Host-side control (via Moku API):**

```python
from bpd_drivers import DS1120ADriver
from moku import MokuGo
from bpd_core import validate_probe_moku_compatibility, MOKU_GO_PLATFORM

# Initialize hardware
moku = MokuGo(ip="192.168.1.1")
driver = DS1120ADriver()

# Validate compatibility
validate_probe_moku_compatibility(driver, MOKU_GO_PLATFORM)

# Deploy bitstream with BPD VHDL
moku.deploy_instrument("emfi_instrument.tar")

# Configure probe (writes to Moku control registers)
pulse_width_ns = 100
voltage_digital = int((3.3 / 5.0) * 2**16)  # 3.3V scaled to 16-bit

moku.set_control_register(0, pulse_width_ns)  # CR0: pulse_width
moku.set_control_register(1, voltage_digital)  # CR1: voltage

# Arm probe (CR2: arm bit)
moku.set_control_register(2, 1)

# Wait for ready (SR0: ready flag)
while not moku.get_status_register(0):
    time.sleep(0.001)

# Trigger (CR3: trigger bit, single-cycle pulse)
moku.set_control_register(3, 1)
moku.set_control_register(3, 0)  # Clear trigger

# Wait for completion (SR1: busy flag)
while moku.get_status_register(1):
    time.sleep(0.001)

# Check fault (SR2: fault flag)
if moku.get_status_register(2):
    print("Probe fault detected!")

# Disarm
moku.set_control_register(2, 0)
```

### Pattern 3: Multi-Probe Support

**Same VHDL works for different probes:**

```vhdl
-- For DS1120A (EMFI)
probe_ds1120a : entity work.fi_probe_interface
    generic map (
        PULSE_WIDTH_BITS => 16,
        VOLTAGE_BITS => 16,
        COOLDOWN_CYCLES => 125  -- 1μs
    )
    -- ports...

-- For Laser FI (different timing)
probe_laser : entity work.fi_probe_interface
    generic map (
        PULSE_WIDTH_BITS => 16,
        VOLTAGE_BITS => 16,
        COOLDOWN_CYCLES => 10   -- 80ns (faster cooldown for laser)
    )
    -- ports...

-- For Voltage Glitching (sub-nanosecond pulses)
probe_vglitch : entity work.fi_probe_interface
    generic map (
        PULSE_WIDTH_BITS => 8,   -- Shorter pulses
        VOLTAGE_BITS => 16,
        COOLDOWN_CYCLES => 1250  -- 10μs (longer cooldown)
    )
    -- ports...
```

**Key: Adjust generics per probe type**

---

## Testing with CocoTB

### Basic FSM Test

```python
# tests/test_fi_interface.py

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

@cocotb.test()
async def test_arm_trigger_sequence(dut):
    """Test basic arm → trigger → pulse → cooldown → disarm."""

    # Setup clock (125MHz = 8ns period)
    clock = Clock(dut.clk, 8, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # Initially in IDLE
    assert dut.ready.value == 1
    assert dut.busy.value == 0

    # Configure pulse width (100ns = 100 cycles @ 1ns resolution)
    dut.pulse_width.value = 100
    dut.voltage_ctrl.value = 32767  # Mid-range voltage

    # Arm probe
    dut.arm.value = 1
    await RisingEdge(dut.clk)

    # Should transition to ARMED
    await Timer(10, units="ns")
    assert dut.ready.value == 0
    # assert dut.armed.value == 1  # If armed output exists

    # Trigger
    dut.trigger_in.value = 1
    await RisingEdge(dut.clk)
    dut.trigger_in.value = 0

    # Should transition to PULSE_ACTIVE
    await Timer(10, units="ns")
    assert dut.busy.value == 1
    assert dut.probe_trigger.value == 1

    # Wait for pulse duration (100ns)
    await Timer(100, units="ns")

    # Should transition to COOLDOWN
    assert dut.busy.value == 1  # Still busy
    assert dut.probe_trigger.value == 0  # Pulse ended

    # Wait for cooldown (125 cycles = 1μs @ 125MHz)
    await Timer(1, units="us")

    # Should return to ARMED (arm still high)
    assert dut.ready.value == 0
    assert dut.busy.value == 0

    # Disarm
    dut.arm.value = 0
    await RisingEdge(dut.clk)

    # Should return to IDLE
    await Timer(10, units="ns")
    assert dut.ready.value == 1
```

### Cooldown Enforcement Test

```python
@cocotb.test()
async def test_cooldown_enforcement(dut):
    """Test that cooldown prevents rapid triggers."""

    clock = Clock(dut.clk, 8, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1

    dut.pulse_width.value = 10
    dut.arm.value = 1
    await RisingEdge(dut.clk)

    # First trigger
    dut.trigger_in.value = 1
    await RisingEdge(dut.clk)
    dut.trigger_in.value = 0

    # Wait for pulse completion
    await Timer(20, units="ns")

    # Attempt second trigger during cooldown
    dut.trigger_in.value = 1
    await RisingEdge(dut.clk)
    dut.trigger_in.value = 0

    # Second trigger should be ignored (still in cooldown)
    await Timer(10, units="ns")
    assert dut.busy.value == 1  # Still cooling down

    # Wait for cooldown to complete
    await Timer(1, units="us")

    # Now ready for next trigger
    assert dut.busy.value == 0
```

---

## Common Tasks

### Adjust Pulse Timing

**Change pulse width at runtime:**

```vhdl
-- From Python
pulse_width_ns = 200  -- nanoseconds
moku.set_control_register(0, pulse_width_ns)

-- VHDL receives and uses immediately on next trigger
```

### Adjust Cooldown Period

**Change cooldown in VHDL:**

```vhdl
-- At design time (generic)
probe_ctrl : entity work.fi_probe_interface
    generic map (
        COOLDOWN_CYCLES => 250  -- 2μs @ 125MHz (double the default)
    )
```

**Cannot change at runtime** (safety feature)

### Debug FSM States

**Use fsm_observer from forge-vhdl:**

```vhdl
-- Map FSM states to voltages for oscilloscope debugging
use work.fsm_observer;

dbg_observer : entity work.fsm_observer
    generic map (
        NUM_STATES => 4,
        V_MIN => -5.0,
        V_MAX => 5.0
    )
    port map (
        state => current_state,  -- Internal FSM state
        voltage_out => debug_voltage
    );

-- Connect debug_voltage to Moku output
OUT2 <= debug_voltage;  -- View on oscilloscope
```

**State mapping:**
- IDLE = -5V
- ARMED = -1.67V
- PULSE_ACTIVE = +1.67V
- COOLDOWN = +5V

### Handle Faults

**Detect and recover from faults:**

```python
# Python control
status_fault = moku.get_status_register(2)  # SR2: fault flag

if status_fault:
    print("Probe fault detected")

    # Disarm to reset FSM
    moku.set_control_register(2, 0)  # Clear arm

    # Wait for IDLE
    while not moku.get_status_register(0):  # SR0: ready
        time.sleep(0.001)

    # Investigate fault (check hardware, reduce voltage, etc.)
    # Then re-arm when safe
```

---

## File Structure

```
bpd-vhdl/
├── src/
│   └── fi_probe_interface.vhd   # Main VHDL component
├── tests/
│   ├── test_fi_interface.py     # CocoTB tests
│   ├── conftest.py              # Test configuration
│   └── Makefile                 # CocoTB build
├── pyproject.toml
├── llms.txt                     # Tier 1 quick reference
├── CLAUDE.md                    # This file (Tier 2 deep dive)
└── README.md
```

---

## Dependencies

**VHDL Libraries:**
- `ieee.std_logic_1164` - Standard logic types
- `ieee.numeric_std` - Unsigned/signed arithmetic
- `work.forge_vhdl` (optional) - Utilities from forge-vhdl

**Testing:**
- CocoTB - Python-based VHDL testing
- GHDL - VHDL simulator
- pytest - Test runner

**Integration:**
- `bpd-core` / `bpd-drivers` - Python control layer
- Moku API - Hardware deployment

---

## Development Workflow

```bash
# Navigate to bpd-vhdl
cd bpd/bpd-vhdl

# Run CocoTB tests
cd tests/
pytest test_fi_interface.py

# View waveforms
gtkwave test_fi_interface.vcd

# Format VHDL (if using formatter)
vsg --fix src/fi_probe_interface.vhd
```

---

## Future Enhancements

**Planned:**
- [ ] Temperature monitoring input
- [ ] Current limit detection
- [ ] Advanced triggering patterns (burst mode, sweep)
- [ ] Probe health status (extended status word)
- [ ] Multi-probe coordination (mutex, scheduling)

**Potential:**
- [ ] Adaptive cooldown (temperature-based)
- [ ] Pulse train generation
- [ ] Frequency sweeping
- [ ] Real-time feedback (coil current monitoring)

---

**Last Updated:** 2025-11-04
**Maintainer:** BPD Development Team
**License:** MIT
**Part of:** BPD-002 (Basic Probe Driver)
