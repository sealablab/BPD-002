# BPD (Basic Probe Driver) - Development Guide

**Version:** 0.1.0
**Status:** Active Development
**Goal:** Generic probe driver framework for Moku platform with multi-vendor support

---

## What is BPD?

BPD is a generic fault injection probe driver framework for the Moku platform that provides:

- **Vendor-agnostic Python interface** - Write probe drivers once, work with multiple probe types
- **Vendor-agnostic VHDL interface** - Standard FPGA interface modeled after DS1120A (de facto standard)
- **Safety validation** - Automatic voltage compatibility checking between Moku and probes
- **Extensibility** - Easy to add new probe types

**Current Support:**
- ✅ Riscure DS1120A EMFI probe (reference implementation)
- 🚧 Additional probes (planned)

---

## Architecture Overview

```
BPD-002/
├── libs/                          # Upstream submodules (READ-ONLY)
│   ├── moku-models/               # Moku platform specs (Go/Lab/Pro/Delta)
│   ├── riscure-models/            # DS1120A electrical specs
│   ├── forge-vhdl/                # General VHDL utilities
│   └── forge-codegen/             # YAML → VHDL code generator
│
├── bpd/                           # BPD DEVELOPMENT (your work here!)
│   ├── bpd-core/                  # Generic probe framework (Python)
│   │   ├── interface.py           # FIProbeInterface protocol
│   │   ├── registry.py            # Driver discovery
│   │   └── validation.py          # Safety checks
│   │
│   ├── bpd-drivers/               # Probe-specific drivers (Python)
│   │   └── ds1120a.py             # DS1120A driver (reference)
│   │
│   ├── bpd-vhdl/                  # Vendor-agnostic VHDL
│   │   └── fi_probe_interface.vhd # Standard FI interface
│   │
│   └── examples/                  # Integration examples (TODO)
│       └── bpd-demo-instrument/   # Full Moku instrument using BPD
```

### Design Philosophy

**1. Generic Interface, Specific Implementations**
- `bpd-core` defines abstract `FIProbeInterface`
- `bpd-drivers` contains probe-specific implementations (DS1120A, laser, etc.)
- All drivers implement same interface → easy to swap probes

**2. Upstream Submodules = Read-Only References**
- Don't modify `libs/` submodules directly during iteration
- Use them as authoritative specifications
- When code stabilizes, extract and upstream changes

**3. VHDL Inspired by DS1120A**
- DS1120A interface is de facto standard (many vendors copy it)
- `bpd-vhdl/fi_probe_interface.vhd` is generic but DS1120A-like
- Works for EMFI, laser FI, voltage glitching, etc.

---

## Quick Start

### 1. Clone and Initialize

```bash
git clone --recurse-submodules https://github.com/YOUR-USERNAME/BPD-002.git
cd BPD-002
uv sync
```

### 2. Install BPD Packages

```bash
cd bpd/bpd-core && uv pip install -e . && cd ../..
cd bpd/bpd-drivers && uv pip install -e . && cd ../..
```

### 3. Test BPD Framework

```python
from bpd_drivers import DS1120ADriver
from moku_models import MOKU_GO_PLATFORM
from bpd_core import validate_probe_moku_compatibility

# Create driver for DS1120A
driver = DS1120ADriver()
driver.initialize()

# Validate compatibility with Moku Go
validate_probe_moku_compatibility(driver, MOKU_GO_PLATFORM)

# Configure and use
driver.set_voltage(3.3)
driver.set_pulse_width(100)
driver.arm()
driver.trigger()

print(driver.get_status())
```

---

## Development Workflow

### Adding a New Probe Driver

**Example: Adding laser FI probe support**

1. **Create driver module:**
```python
# bpd/bpd-drivers/src/bpd_drivers/laser_fi.py

from bpd_core import FIProbeInterface, ProbeCapabilities, register_driver

@register_driver("laser_fi")
class LaserFIDriver:
    """Driver for laser fault injection probe."""

    @property
    def capabilities(self) -> ProbeCapabilities:
        return ProbeCapabilities(
            min_voltage_v=0.0,
            max_voltage_v=5.0,
            min_pulse_width_ns=1,
            max_pulse_width_ns=1000,
            pulse_width_resolution_ns=1,
            supports_external_trigger=True,
            supports_internal_trigger=True,
        )

    def initialize(self) -> None:
        # Initialize laser hardware
        pass

    # ... implement other FIProbeInterface methods
```

2. **Add to exports:**
```python
# bpd/bpd-drivers/src/bpd_drivers/__init__.py
from bpd_drivers.laser_fi import LaserFIDriver

__all__ = ["DS1120ADriver", "LaserFIDriver"]
```

3. **Use it:**
```python
from bpd_drivers import LaserFIDriver
driver = LaserFIDriver()
# Same interface as DS1120A!
```

### Testing VHDL Interface

```bash
cd bpd/bpd-vhdl/tests/
pytest test_fi_interface.py
```

---

## Integration with Moku

### Python Layer: Safety Validation

```python
from bpd_core import validate_probe_moku_compatibility
from moku_models import MOKU_GO_PLATFORM, MOKU_LAB_PLATFORM

# Validate probe works with Moku Go
validate_probe_moku_compatibility(driver, MOKU_GO_PLATFORM, output_id="OUT1")

# Validate probe works with Moku Lab
validate_probe_moku_compatibility(driver, MOKU_LAB_PLATFORM, output_id="OUT2")
```

This checks:
- Probe input voltage ≤ Moku output voltage
- Signal compatibility (TTL vs analog)
- Safety constraints

### VHDL Layer: Standard Interface

```vhdl
-- In your Moku instrument top-level VHDL
library work;
use work.fi_probe_interface;

-- Instantiate BPD VHDL interface
probe_ctrl : entity work.fi_probe_interface
    generic map (
        PULSE_WIDTH_BITS => 16,  -- 0-65535 ns
        VOLTAGE_BITS => 16       -- ±32767 for voltage control
    )
    port map (
        clk => clk_125mhz,
        rst_n => rst_n,

        -- Control from Moku registers
        trigger_in => trigger_reg,
        arm => arm_reg,
        pulse_width => pulse_width_reg,
        voltage_level => voltage_reg,

        -- Output to probe hardware
        probe_trigger => probe_trig_pin,
        probe_pulse_ctrl => probe_pulse_pin,
        probe_voltage => probe_dac_value,

        -- Status
        ready => probe_ready,
        busy => probe_busy,
        fault => probe_fault
    );
```

---

## Upstreaming Strategy

**Goal:** Develop quickly here, upstream when stable

### What Goes Where (Eventually)

**To `moku-models` (if adding Moku features):**
- New Moku platform definitions
- Extended platform capabilities

**To `forge-vhdl` (if generally useful):**
- Reusable VHDL components from `bpd-vhdl/`
- Generic utilities (not probe-specific)

**To `riscure-models` (if DS1120A-specific):**
- Enhanced DS1120A specifications
- Driver integration patterns

**New submodule: `probe-driver-framework`:**
- Extract `bpd-core` as standalone library
- Make it useful for non-Moku platforms too

**New submodule: `laser-models` (when adding laser support):**
- Laser probe specifications (like riscure-models)
- Voltage safety specs

### Upstreaming Process

1. **Develop here** - Fast iteration in `bpd/`
2. **Stabilize** - Tests pass, patterns clear
3. **Extract** - Create standalone repo for component
4. **Add as submodule** - Replace local code with submodule reference
5. **Submit PR** - Contribute back to upstream repos

---

## FAQ

### Q: Why keep riscure-models if I'm using other probes?

**A:** It's an excellent reference implementation showing:
- How to structure probe specifications (Pydantic models)
- Voltage safety validation patterns
- 3-tier documentation (llms.txt → CLAUDE.md → source)

Keep it as a reference implementation even if you're not using Riscure hardware.

### Q: Can I modify upstream submodules (libs/)?

**A:** You *can*, but recommended workflow:
- **During iteration:** Don't modify, use as read-only references
- **When mature:** Fork submodule, make changes, submit PR upstream
- **If rejected:** Keep your fork and update `.gitmodules`

### Q: Why separate bpd-core and bpd-drivers?

**A:** Clean separation of concerns:
- `bpd-core` = generic framework (no probe-specific code)
- `bpd-drivers` = implementations for specific probes
- Easier to extract `bpd-core` as standalone library later

### Q: Does VHDL interface work for non-FI probes?

**A:** The `fi_probe_interface.vhd` is designed for FI probes (trigger, pulse, voltage).
For very different probes (oscilloscopes, logic analyzers), you may need different VHDL interfaces.
But many probes (EMFI, laser FI, voltage glitching) fit this model.

---

## Current Status

### ✅ Completed (v0.1.0)

- [x] BPD workspace structure (`bpd-core`, `bpd-drivers`, `bpd-vhdl`)
- [x] Generic `FIProbeInterface` protocol
- [x] DS1120A reference driver using riscure-models
- [x] Voltage safety validation
- [x] Vendor-agnostic VHDL interface
- [x] CocoTB tests for VHDL
- [x] Integration with Moku platform specs

### 🚧 In Progress

- [ ] Complete DS1120A hardware integration (currently simulated)
- [ ] Example Moku instrument using BPD
- [ ] Additional probe drivers (laser, RF, etc.)
- [ ] Extended VHDL test coverage
- [ ] Performance testing

### 📋 Planned

- [ ] Multi-probe support (simultaneous use of different probes)
- [ ] Probe switching/multiplexing
- [ ] Advanced triggering patterns
- [ ] Pulse train generation
- [ ] Voltage sweep automation
- [ ] Extract bpd-core as standalone library

---

## Resources

**Documentation:**
- `bpd/bpd-core/README.md` - Generic framework guide
- `bpd/bpd-drivers/README.md` - Driver development guide
- `bpd/bpd-vhdl/README.md` - VHDL interface guide
- Root `CLAUDE.md` - Monorepo architecture

**Submodule References:**
- `libs/moku-models/` - Moku platform specifications
- `libs/riscure-models/` - DS1120A probe specifications
- `libs/forge-vhdl/` - General VHDL utilities
- `tools/forge-codegen/` - YAML → VHDL generator

**Testing:**
```bash
pytest                              # Run all tests
pytest bpd/bpd-vhdl/tests/         # VHDL tests only
pytest bpd/bpd-core/tests/         # Python tests only
```

---

## Contributing

BPD is under active development. Contributions welcome!

**Areas needing help:**
- Additional probe drivers (laser FI, RF, voltage glitching)
- VHDL test coverage
- Documentation improvements
- Example Moku instruments

**Development setup:**
1. Clone with submodules
2. Install BPD packages in editable mode
3. Make changes
4. Run tests
5. Submit PR

---

**License:** MIT
**Maintainer:** BPD Development Team
**Last Updated:** 2025-11-04
