# BPD-002 Customization Summary

**Date:** 2025-11-04
**Monorepo:** BPD-002 (Basic Probe Driver)
**Goal:** Generic FI probe driver for Moku platform

---

## What Was Customized

This monorepo template was customized for **BPD (Basic Probe Driver)** development - a generic probe driver framework for Moku platform supporting multiple vendor probes.

### Customization Overview

**From:** Generic Moku + Probe template
**To:** BPD-specific development environment with DS1120A reference implementation

---

## Added Components

### 1. BPD Core Framework (`bpd/bpd-core/`)

**Purpose:** Generic probe driver abstractions

**Key Files:**
- `interface.py` - `FIProbeInterface` protocol (vendor-agnostic)
- `registry.py` - Dynamic driver discovery
- `validation.py` - Moku-probe safety validation

**Design:** Protocol-based interface inspired by DS1120A but generic enough for any FI probe (EMFI, laser, voltage glitching, etc.)

### 2. BPD Drivers (`bpd/bpd-drivers/`)

**Purpose:** Probe-specific driver implementations

**Current Drivers:**
- `ds1120a.py` - Riscure DS1120A EMFI probe (reference implementation)

**Uses:** riscure-models for electrical specifications

**Future:** Add laser_fi.py, rf_analyzer.py, etc.

### 3. BPD VHDL (`bpd/bpd-vhdl/`)

**Purpose:** Vendor-agnostic FPGA interface for probe control

**Key Files:**
- `fi_probe_interface.vhd` - Standard FI probe control interface
- `tests/test_fi_interface.py` - CocoTB verification tests

**Design:** Inspired by DS1120A (de facto standard) but generic:
- Configurable pulse width (generic PULSE_WIDTH_BITS)
- Configurable voltage control (generic VOLTAGE_BITS)
- State machine: IDLE → ARMED → PULSE_ACTIVE → COOLDOWN
- Status signals: ready, busy, fault

---

## What Was Kept (Unchanged)

### Upstream Submodules (libs/)

✅ **Kept as read-only references:**

- `libs/moku-models/` - **REQUIRED** - Moku platform specs (foundation)
- `libs/riscure-models/` - **KEPT** - DS1120A specs (first probe, reference example)
- `libs/forge-vhdl/` - **KEPT** - General VHDL utilities
- `tools/forge-codegen/` - **KEPT** - YAML → VHDL code generator

**Rationale:** These are authoritative upstream references. BPD code uses them but doesn't modify them during iteration.

---

## Workspace Configuration

### Updated `pyproject.toml`

**Added workspace members:**
```toml
[tool.uv.workspace]
members = [
    # Upstream submodules
    "libs/forge-vhdl",
    "libs/moku-models",
    "libs/riscure-models",
    "tools/forge-codegen",
    # BPD development workspace members (NEW!)
    "bpd/bpd-core",
    "bpd/bpd-drivers",
    "bpd/bpd-vhdl",
]
```

**Added test paths:**
```toml
testpaths = [
    # ... existing upstream tests ...
    "bpd/bpd-core/tests",
    "bpd/bpd-drivers/tests",
    "bpd/bpd-vhdl/tests",
]
```

---

## Architecture Decisions

### 1. Terminology: "Drivers" not "Adapters"

**Problem:** "Adapter" confusing in hardware context (cables, impedance matchers)

**Solution:** Use "drivers" - clear in both software and hardware contexts
- `bpd-drivers/` = Probe-specific software drivers
- `ds1120a.py` = DS1120A driver (software controlling DS1120A hardware)

### 2. Python Interface: Protocol-Based

**Choice:** `FIProbeInterface` as Protocol (not ABC)

**Rationale:**
- Duck typing flexibility
- No forced inheritance
- Easy to implement for diverse probes
- Alternative `BaseFIProbeDriver` ABC available if needed

### 3. VHDL Interface: DS1120A-Inspired Generic

**Design:** Modeled after DS1120A (de facto standard) but:
- Configurable generics (not DS1120A-specific)
- Works for EMFI, laser FI, voltage glitching
- Simple control: arm, trigger, pulse_width, voltage
- Standard state machine with safety features

**Rationale:** Many vendors copy DS1120A interface → good baseline for generic design

### 4. Rapid Iteration Strategy

**Approach:** Work in monorepo `bpd/` first, upstream later

**NOT:** Fork submodules immediately and modify them

**Rationale:**
- Faster iteration (no submodule commit/push cycles)
- Easier to refactor and experiment
- Clear separation between "stable upstream" and "BPD experimental"
- Upstream extraction when patterns stabilize

---

## File Structure Overview

```
BPD-002/
├── libs/                          # Upstream (read-only during iteration)
│   ├── moku-models/               # Platform specs
│   ├── riscure-models/            # DS1120A specs
│   ├── forge-vhdl/                # VHDL utilities
│   └── forge-codegen/             # Code generator
│
├── tools/
│   └── forge-codegen/             # YAML → VHDL
│
├── bpd/                           # ⭐ BPD DEVELOPMENT AREA ⭐
│   ├── bpd-core/                  # Generic framework
│   │   ├── pyproject.toml
│   │   ├── README.md
│   │   └── src/bpd_core/
│   │       ├── __init__.py
│   │       ├── interface.py       # FIProbeInterface protocol
│   │       ├── registry.py        # Driver discovery
│   │       └── validation.py      # Safety validation
│   │
│   ├── bpd-drivers/               # Probe-specific drivers
│   │   ├── pyproject.toml
│   │   ├── README.md
│   │   └── src/bpd_drivers/
│   │       ├── __init__.py
│   │       └── ds1120a.py         # DS1120A driver
│   │
│   └── bpd-vhdl/                  # Vendor-agnostic VHDL
│       ├── pyproject.toml
│       ├── README.md
│       ├── src/
│       │   └── fi_probe_interface.vhd
│       └── tests/
│           └── test_fi_interface.py
│
├── bpd/examples/
│   └── quickstart.py              # Demo usage
│
├── BPD-README.md                  # ⭐ BPD-specific guide ⭐
├── CUSTOMIZATION-SUMMARY.md       # This file
├── CLAUDE.md                      # Original template guide
└── pyproject.toml                 # Updated workspace config
```

---

## Usage Examples

### Python: Using DS1120A Driver

```python
from bpd_drivers import DS1120ADriver
from moku_models import MOKU_GO_PLATFORM
from bpd_core import validate_probe_moku_compatibility

# Create and initialize
driver = DS1120ADriver()
driver.initialize()

# Validate Moku compatibility
validate_probe_moku_compatibility(driver, MOKU_GO_PLATFORM)

# Configure
driver.set_voltage(3.3)
driver.set_pulse_width(100)

# Use
driver.arm()
driver.trigger()
```

### VHDL: Integrating BPD Interface

```vhdl
-- In Moku instrument top-level
probe_ctrl : entity work.fi_probe_interface
    generic map (
        PULSE_WIDTH_BITS => 16,
        VOLTAGE_BITS => 16
    )
    port map (
        clk => clk_125mhz,
        rst_n => rst_n,
        trigger_in => trigger_reg,
        arm => arm_reg,
        pulse_width => pulse_width_reg,
        voltage_level => voltage_reg,
        probe_trigger => probe_trig_pin,
        -- ... other signals
    );
```

---

## Testing

### Quick Test

```bash
# Run quickstart example
python bpd/examples/quickstart.py
```

### Full Test Suite

```bash
# All tests
pytest

# BPD only
pytest bpd/

# VHDL tests
pytest bpd/bpd-vhdl/tests/
```

---

## Next Steps

### Immediate (v0.1.x)

1. **Add real DS1120A hardware integration** (currently simulated)
2. **Create example Moku instrument** using BPD
3. **Add more CocoTB tests** for VHDL edge cases

### Short-term (v0.2.x)

1. **Add second probe driver** (laser FI, RF analyzer, etc.)
2. **Create probe models submodule** for non-Riscure probes
3. **Multi-probe support** (use multiple probes simultaneously)

### Long-term (v1.0+)

1. **Extract bpd-core as standalone library** (upstream to new submodule)
2. **Upstream VHDL components to forge-vhdl** (if generally useful)
3. **Community drivers** (encourage others to add probe support)

---

## Upstreaming Strategy

**When BPD matures:**

**To `moku-models`:**
- Extended platform integration patterns

**To `forge-vhdl`:**
- Generic VHDL components from bpd-vhdl (if reusable beyond probes)

**To `riscure-models`:**
- Enhanced DS1120A driver integration

**New submodule `probe-driver-framework`:**
- Extract bpd-core as standalone library
- Make it useful for non-Moku platforms

**New probe model submodules:**
- `laser-models/` - Laser probe specs
- `rf-analyzer-models/` - RF analyzer specs
- etc.

---

## Key Takeaways

### What Makes This Customization Special

1. **Multi-vendor from day 1** - Designed for multiple probe types, not just DS1120A
2. **Clear separation** - Upstream (libs/) vs development (bpd/)
3. **Generic VHDL** - Works across probe vendors (DS1120A-inspired standard)
4. **Safety first** - Automatic voltage validation between Moku and probes
5. **Fast iteration** - Work in monorepo, upstream when stable

### Terminology Clarification

- **"Adapter"** ❌ (confused with hardware cables)
- **"Driver"** ✅ (clear: software controlling hardware)

### Development Philosophy

- **Iterate fast in `bpd/`**
- **Keep `libs/` upstream references clean**
- **Upstream when patterns stabilize**
- **Generic interface, specific implementations**

---

## Resources

**Main Documentation:**
- `BPD-README.md` - Complete BPD guide
- `bpd/bpd-core/README.md` - Framework details
- `bpd/bpd-drivers/README.md` - Driver development
- `bpd/bpd-vhdl/README.md` - VHDL interface

**Examples:**
- `bpd/examples/quickstart.py` - Quick start demo

**Original Template:**
- `CLAUDE.md` - Monorepo architecture guide

---

**Customization Completed:** 2025-11-04
**Framework Status:** ✅ Functional (v0.1.0)
**First Milestone:** ✅ DS1120A driver implemented and tested
