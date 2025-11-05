# BPD-002 - Basic Probe Driver

**Multi-Vendor Fault Injection Probe Integration for Moku Platform**

---

## What Is BPD-002?

**BPD-002** is a complete probe driver framework for integrating fault injection probes (EMFI, laser FI, RF, voltage glitching) with Moku FPGA platforms (Go/Lab/Pro/Delta).

**Key Innovation:** Vendor-agnostic Python + VHDL architecture enables writing probe drivers once and using them across multiple probe types without code changes.

**Current Status:** v0.1.0 - DS1120A EMFI reference implementation complete

**Reference Implementation:** Moku + Riscure DS1120A EMFI probe

---

## Project Structure

```
BPD-002/
├── bpd/                           # BPD Application (your work)
│   ├── bpd-core/                  # Generic probe framework (Python)
│   ├── bpd-drivers/               # Probe-specific drivers (Python)
│   ├── bpd-vhdl/                  # Vendor-agnostic VHDL interface
│   └── examples/                  # Integration examples
│
├── libs/                          # Upstream dependencies (git submodules)
│   ├── moku-models/               # Moku platform specifications
│   ├── riscure-models/            # DS1120A probe specs (reference)
│   └── forge-vhdl/                # VHDL utilities
│
├── tools/                         # Development tools (git submodules)
│   └── forge-codegen/             # YAML → VHDL generator
│
├── llms.txt                       # Quick navigation (Tier 1)
├── CLAUDE.md                      # This file (Tier 2)
├── BPD-README.md                  # User-facing README
└── .claude/                       # AI agent system
    ├── shared/
    │   └── CONTEXT_MANAGEMENT.md  # AI context loading strategy
    └── agents/                    # Project-level agents
```

---

## Quick Start

### Installation

```bash
# Clone with submodules
git clone --recurse-submodules https://github.com/sealablab/BPD-002.git
cd BPD-002

# Install dependencies
uv sync

# Install BPD packages
cd bpd/bpd-core && uv pip install -e . && cd ../..
cd bpd/bpd-drivers && uv pip install -e . && cd ../..
cd bpd/bpd-vhdl && uv pip install -e . && cd ../..
```

### Basic Usage (DS1120A)

```python
from bpd_drivers import DS1120ADriver
from bpd_core import validate_probe_moku_compatibility
from moku_models import MOKU_GO_PLATFORM

# Initialize driver
driver = DS1120ADriver()
driver.initialize()

# Validate voltage safety
validate_probe_moku_compatibility(driver, MOKU_GO_PLATFORM)

# Configure and use
driver.set_voltage(3.3)
driver.set_pulse_width(50)  # Fixed for DS1120A
driver.arm()
driver.trigger()
driver.disarm()
```

---

## Architecture Overview

### Three-Layer Design

**1. Python Framework (bpd-core)**
- Generic `FIProbeInterface` protocol
- Driver registry and discovery
- Voltage safety validation
- **[Details: bpd/bpd-core/CLAUDE.md](bpd/bpd-core/CLAUDE.md)**

**2. Python Drivers (bpd-drivers)**
- Probe-specific implementations
- DS1120A (EMFI) reference implementation
- Future: Laser FI, RF injection, voltage glitching
- **[Details: bpd/bpd-drivers/CLAUDE.md](bpd/bpd-drivers/CLAUDE.md)**

**3. VHDL Interface (bpd-vhdl)**
- Vendor-agnostic FPGA control
- FSM: IDLE → ARMED → PULSE_ACTIVE → COOLDOWN
- Safety interlocks (cooldown, fault detection)
- **[Details: bpd/bpd-vhdl/CLAUDE.md](bpd/bpd-vhdl/CLAUDE.md)**

### Data Flow

```
[Python Driver] ← validate → [moku-models] (platform specs)
                ← validate → [riscure-models] (probe specs)
       ↓
[Moku API] → Control Registers
       ↓
[VHDL FSM] → probe_trigger, probe_voltage
       ↓
[Physical Probe] → Target DUT
```

---

## Core Concepts

### 1. Generic Probe Interface

All probe drivers implement same protocol:

```python
class FIProbeInterface(Protocol):
    @property
    def capabilities(self) -> ProbeCapabilities: ...
    def initialize(self) -> None: ...
    def set_voltage(self, voltage_v: float) -> None: ...
    def set_pulse_width(self, width_ns: int) -> None: ...
    def arm(self) -> None: ...
    def trigger(self) -> None: ...
    def disarm(self) -> None: ...
    def get_status(self) -> ProbeStatus: ...
    def shutdown(self) -> None: ...
```

**Benefit:** Same code works for DS1120A, laser FI, RF probes, etc.

### 2. Voltage Safety Validation

Before physical wiring:

```python
from bpd_core import validate_probe_moku_compatibility, ProbeValidationError

try:
    validate_probe_moku_compatibility(driver, MOKU_GO_PLATFORM, output_id="OUT1")
    print("✓ Safe to connect Moku OUT1 → Probe")
except ProbeValidationError as e:
    print(f"✗ Unsafe: {e}")
```

**Checks:**
- Probe max voltage ≤ Moku output voltage
- Signal type compatibility (TTL vs analog)
- Prevents hardware damage

### 3. Driver Discovery

Drivers auto-register with decorator:

```python
@register_driver("laser_fi")
class LaserFIDriver:
    # Implementation
    pass

# Later, load by name
from bpd_core import get_driver
DriverClass = get_driver("laser_fi")
driver = DriverClass()
```

**Benefit:** Config-driven probe selection (no code changes)

### 4. VHDL State Machine

Generic FSM for all probe types:

```
IDLE → (arm) → ARMED → (trigger) → PULSE_ACTIVE → COOLDOWN → IDLE/ARMED
```

**Safety features:**
- Enforced cooldown (prevents overheating)
- Arm-before-trigger (prevents accidents)
- Fault detection (returns to safe state)

---

## Development Workflows

### Adding a New Probe Type

**Example: Laser FI probe**

1. **Create driver** in `bpd/bpd-drivers/src/bpd_drivers/laser_fi.py`
2. **Implement `FIProbeInterface`** protocol
3. **Add `@register_driver("laser_fi")`** decorator
4. **Export** in `bpd/bpd-drivers/src/bpd_drivers/__init__.py`
5. **Write tests** in `bpd/bpd-drivers/tests/test_laser_fi.py`
6. **Use same VHDL** (adjust generics for timing)

**[Complete Guide: bpd/bpd-drivers/CLAUDE.md](bpd/bpd-drivers/CLAUDE.md)**

### Validating Compatibility

**Check probe works with Moku platform:**

```python
from bpd_core import validate_probe_moku_compatibility
from moku_models import MOKU_GO_PLATFORM, MOKU_LAB_PLATFORM

platforms = [MOKU_GO_PLATFORM, MOKU_LAB_PLATFORM]

for platform in platforms:
    try:
        validate_probe_moku_compatibility(driver, platform)
        print(f"✓ Compatible with {platform.name}")
    except Exception as e:
        print(f"✗ Incompatible: {e}")
```

### Integrating VHDL Interface

**Add to Moku custom instrument:**

```vhdl
probe_ctrl : entity work.fi_probe_interface
    generic map (
        PULSE_WIDTH_BITS => 16,
        VOLTAGE_BITS => 16,
        COOLDOWN_CYCLES => 125  -- 1μs @ 125MHz
    )
    port map (
        clk => clk_125mhz,
        rst_n => rst_n,
        trigger_in => trigger_reg,
        arm => arm_reg,
        probe_trigger => OUT1,
        ready => status_ready,
        busy => status_busy
    );
```

**[Complete Guide: bpd/bpd-vhdl/CLAUDE.md](bpd/bpd-vhdl/CLAUDE.md)**

---

## Common Tasks

### Query Probe Capabilities

```python
driver = DS1120ADriver()
caps = driver.capabilities

print(f"Voltage: {caps.min_voltage_v}V - {caps.max_voltage_v}V")
print(f"Pulse width: {caps.min_pulse_width_ns}ns - {caps.max_pulse_width_ns}ns")
```

### Switch Between Probes

```python
# Config-driven probe selection
probe_name = config["probe_type"]  # "ds1120a", "laser_fi", etc.
DriverClass = get_driver(probe_name)
driver = DriverClass()

# Same code for any probe!
driver.initialize()
driver.arm()
driver.trigger()
```

### Test Without Hardware

```python
# Drivers automatically fall back to simulation
driver = DS1120ADriver()
driver.initialize()  # Works without hardware connected

driver.trigger()  # Prints "[SIM] DS1120A pulse: 3.3V, 50ns"
```

### Debug VHDL FSM

```vhdl
-- Use fsm_observer from forge-vhdl
dbg : entity work.fsm_observer
    generic map (NUM_STATES => 4, V_MIN => -5.0, V_MAX => 5.0)
    port map (state => current_state, voltage_out => debug_out);

-- Connect to Moku output
OUT2 <= debug_out;  -- View states on oscilloscope
```

---

## Integration with Upstream Libraries

### moku-models

**Purpose:** Moku platform specifications

**Usage:**
```python
from moku_models import MOKU_GO_PLATFORM

platform = MOKU_GO_PLATFORM
print(f"Clock: {platform.clock_mhz} MHz")
print(f"Outputs: {len(platform.analog_outputs)}")

# Get specific output
out1 = platform.get_analog_output_by_id('OUT1')
print(f"OUT1 voltage range: {out1.voltage_range_vpp}Vpp")
```

**Integration:** Voltage validation, platform selection

**[Details: libs/moku-models/CLAUDE.md](libs/moku-models/CLAUDE.md)**

### riscure-models

**Purpose:** DS1120A probe specifications

**Usage:**
```python
from riscure_models import DS1120A_PLATFORM

probe = DS1120A_PLATFORM
port = probe.get_port_by_id('digital_glitch')
print(f"Trigger input: {port.get_voltage_range_str()}")
```

**Integration:** DS1120A driver uses these specs

**[Details: libs/riscure-models/CLAUDE.md](libs/riscure-models/CLAUDE.md)**

### forge-vhdl

**Purpose:** Reusable VHDL components

**Usage:**
```vhdl
-- Clock divider
use work.forge_util_clk_divider;

-- Voltage packages
use work.forge_voltage_5v_bipolar_pkg.all;
signal voltage_digital : signed(15 downto 0);
voltage_digital <= to_digital(2.5);  -- Convert 2.5V to digital
```

**Integration:** VHDL utilities for custom instruments

**[Details: libs/forge-vhdl/CLAUDE.md](libs/forge-vhdl/CLAUDE.md)**

### forge-codegen

**Purpose:** YAML → VHDL code generator

**Usage:**
```bash
python -m forge_codegen.generator.codegen probe_spec.yaml --output-dir generated/
```

**Integration:** Generate Moku instrument boilerplate

**[Details: tools/forge-codegen/CLAUDE.md](tools/forge-codegen/CLAUDE.md)**

---

## Testing

### Unit Tests (Python)

```bash
# BPD Core tests
cd bpd/bpd-core
pytest tests/

# BPD Drivers tests
cd bpd/bpd-drivers
pytest tests/

# Skip hardware tests
pytest tests/ -m "not hardware"
```

### CocoTB Tests (VHDL)

```bash
# BPD VHDL tests
cd bpd/bpd-vhdl/tests
pytest test_fi_interface.py
```

### Integration Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=bpd_core --cov=bpd_drivers
```

---

## Documentation Navigation

### 3-Tier Documentation System

**Tier 1: llms.txt** (~500-1000 tokens)
- Quick reference, basic usage
- Load first for any query
- **[Root llms.txt](llms.txt)** - Component catalog

**Tier 2: CLAUDE.md** (~3-5k tokens)
- Architecture, design rationale
- Integration patterns
- **This file** - BPD-002 overview
- **[bpd-core/CLAUDE.md](bpd/bpd-core/CLAUDE.md)** - Framework design
- **[bpd-drivers/CLAUDE.md](bpd/bpd-drivers/CLAUDE.md)** - Driver development
- **[bpd-vhdl/CLAUDE.md](bpd/bpd-vhdl/CLAUDE.md)** - VHDL architecture

**Tier 3: Source + Docs** (load as needed)
- Implementation details
- API references
- Troubleshooting guides

**AI Navigation Strategy:**
1. Start with `llms.txt` (minimal tokens)
2. Load `CLAUDE.md` for design questions
3. Read source code only when implementing

---

## Roadmap

### v0.1.0 (Current) ✅
- [x] BPD Core framework
- [x] DS1120A driver (reference)
- [x] Generic VHDL interface
- [x] Voltage safety validation
- [x] CocoTB tests
- [x] 3-tier documentation

### v0.2.0 (Planned)
- [ ] Laser FI probe driver
- [ ] Example Moku instrument using BPD
- [ ] Hardware testing with real DS1120A
- [ ] Extended VHDL test coverage

### v0.3.0 (Future)
- [ ] RF injection probe driver
- [ ] Voltage glitching probe driver
- [ ] Multi-probe coordination
- [ ] Advanced triggering patterns
- [ ] Real-time feedback integration

---

## Contributing

**Development setup:**
```bash
git clone --recurse-submodules https://github.com/sealablab/BPD-002.git
cd BPD-002
uv sync
cd bpd/bpd-core && uv pip install -e . && cd ../..
cd bpd/bpd-drivers && uv pip install -e . && cd ../..
```

**Adding new probe types:**
See [bpd/bpd-drivers/CLAUDE.md](bpd/bpd-drivers/CLAUDE.md)

**Testing:**
```bash
pytest                          # All tests
pytest -m "not hardware"       # Skip hardware tests
pytest --cov                   # With coverage
```

---

## Resources

### Documentation
- **This file** - BPD-002 architecture overview
- **[llms.txt](llms.txt)** - Quick navigation guide
- **[BPD-README.md](BPD-README.md)** - User-facing README
- **[examples/](bpd/examples/)** - Integration examples

### Component Guides
- **[bpd-core/CLAUDE.md](bpd/bpd-core/CLAUDE.md)** - Framework design
- **[bpd-drivers/CLAUDE.md](bpd/bpd-drivers/CLAUDE.md)** - Driver development
- **[bpd-vhdl/CLAUDE.md](bpd/bpd-vhdl/CLAUDE.md)** - VHDL architecture

### Community
- **Issues:** https://github.com/sealablab/BPD-002/issues
- **Discussions:** https://github.com/sealablab/BPD-002/discussions

---

**Version:** 0.1.0
**Last Updated:** 2025-11-04
**License:** MIT
**Maintainer:** BPD Development Team
