# BPD-002 - Basic Probe Driver
<!-- NOTE: This comment was handplaced by Johnny so you know a human has looked at this, not just machines 🐬🧜 -->
**Multi-Vendor Fault Injection Probe Integration for Moku Platform**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/sealablab/BPD-002/releases/tag/v0.1.0)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

---

## 🎯 What is BPD-002?

**BPD-002** is a comprehensive probe driver framework for integrating fault injection probes with Moku FPGA platforms. It provides a **vendor-agnostic architecture** that enables you to write probe drivers once and use them across multiple probe types (EMFI, laser FI, RF injection, voltage glitching).

### Key Features

- 🔌 **Generic Probe Interface** - Protocol-based Python framework works with any FI probe
- 🔒 **Voltage Safety Validation** - Automatic compatibility checking before physical wiring
- 🎛️ **VHDL State Machine** - Vendor-agnostic FPGA interface with safety interlocks
- 📦 **Driver Discovery** - Auto-registration system for easy probe switching
- 🧪 **Simulation Mode** - Test drivers without physical hardware
- 📚 **AI-Navigable Docs** - 3-tier documentation optimized for AI assistants

### Current Status

- ✅ **v0.1.0 Released** - DS1120A EMFI reference implementation complete
- ✅ Complete 3-tier documentation system
- ✅ Python framework (bpd-core) production-ready
- ✅ VHDL interface with CocoTB tests
- 🚧 Additional probe drivers planned (laser FI, RF, voltage glitch)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- [uv](https://github.com/astral-sh/uv) package manager
- Git with submodule support
- Moku platform (Go/Lab/Pro/Delta) for hardware deployment

### Installation

```bash
# Clone repository with submodules
git clone --recurse-submodules https://github.com/sealablab/BPD-002.git
cd BPD-002

# Install dependencies
uv sync

# Install BPD packages
cd bpd/bpd-core && uv pip install -e . && cd ../..
cd bpd/bpd-drivers && uv pip install -e . && cd ../..
cd bpd/bpd-vhdl && uv pip install -e . && cd ../..
```

### Verify Installation

```python
# Test imports
from bpd_drivers import DS1120ADriver
from bpd_core import validate_probe_moku_compatibility
from moku_models import MOKU_GO_PLATFORM

print("✅ BPD-002 ready!")
```

---

## 📖 Usage Example

### DS1120A EMFI Probe

```python
from bpd_drivers import DS1120ADriver
from bpd_core import validate_probe_moku_compatibility
from moku_models import MOKU_GO_PLATFORM

# Initialize driver
driver = DS1120ADriver()
driver.initialize()

# Validate voltage safety with Moku Go
validate_probe_moku_compatibility(driver, MOKU_GO_PLATFORM)
print("✅ Safe to connect Moku OUT1 → DS1120A digital_glitch")

# Configure probe
driver.set_voltage(3.3)  # TTL trigger threshold
driver.set_pulse_width(50)  # Fixed at 50ns for DS1120A

# Execute fault injection
driver.arm()
print(f"Status: {driver.get_status()}")
driver.trigger()
driver.disarm()

# Shutdown cleanly
driver.shutdown()
```

### Output

```
[SIM] DS1120A in simulation mode
✅ Safe to connect Moku OUT1 → DS1120A digital_glitch
Status: ProbeStatus(ready=False, busy=False, armed=True, fault=False)
[SIM] DS1120A pulse: 3.3V, 50ns
```

---

## 🏗️ Architecture

BPD-002 uses a **three-layer architecture** for maximum flexibility:

### 1. Python Framework (`bpd-core`)

Generic probe driver framework with protocol-based interface:

- `FIProbeInterface` - Protocol all drivers implement
- `ProbeCapabilities` - Hardware specification dataclass
- `ProbeRegistry` - Auto-discovery system
- `validate_probe_moku_compatibility()` - Safety validation

**[Documentation →](bpd/bpd-core/)**

### 2. Python Drivers (`bpd-drivers`)

Probe-specific implementations:

- **DS1120A** - Riscure EMFI probe (reference implementation) ✅
- **Laser FI** - Optical fault injection (planned) 🚧
- **RF Injection** - Radio frequency FI (planned) 🚧
- **Voltage Glitch** - Power supply glitching (planned) 🚧

**[Documentation →](bpd/bpd-drivers/)**

### 3. VHDL Interface (`bpd-vhdl`)

Vendor-agnostic FPGA control with FSM:

```
IDLE → ARMED → PULSE_ACTIVE → COOLDOWN → IDLE/ARMED
```

Features:
- Configurable pulse timing and voltage control
- Safety interlocks (cooldown enforcement, fault detection)
- Works with EMFI, laser, RF, voltage glitch probes

**[Documentation →](bpd/bpd-vhdl/)**

### Data Flow

```
┌──────────────┐
│ Python Driver│ ← validate → moku-models (platform specs)
└──────┬───────┘ ← validate → riscure-models (probe specs)
       │
       ↓
┌──────────────┐
│  Moku API    │ → Control Registers
└──────┬───────┘
       │
       ↓
┌──────────────┐
│  VHDL FSM    │ → probe_trigger, probe_voltage
└──────┬───────┘
       │
       ↓
┌──────────────┐
│Physical Probe│ → Target DUT
└──────────────┘
```

---

## 📦 Project Structure

```
BPD-002/
├── bpd/                      # BPD Application
│   ├── bpd-core/             # Generic probe framework (Python)
│   │   ├── src/bpd_core/
│   │   ├── tests/
│   │   ├── llms.txt          # Quick reference
│   │   └── CLAUDE.md         # Architecture guide
│   │
│   ├── bpd-drivers/          # Probe-specific drivers (Python)
│   │   ├── src/bpd_drivers/
│   │   │   └── ds1120a.py    # DS1120A driver
│   │   ├── tests/
│   │   ├── llms.txt
│   │   └── CLAUDE.md
│   │
│   ├── bpd-vhdl/             # VHDL probe interface
│   │   ├── src/
│   │   │   └── fi_probe_interface.vhd
│   │   ├── tests/
│   │   ├── llms.txt
│   │   └── CLAUDE.md
│   │
│   └── examples/             # Integration examples
│       └── quickstart.py     # DS1120A basic usage
│
├── libs/                     # Upstream Dependencies (git submodules)
│   ├── moku-models/          # Moku platform specifications
│   ├── riscure-models/       # DS1120A probe specs
│   ├── forge-vhdl/           # VHDL utilities
│   └── forge-codegen/        # YAML → VHDL generator
│
├── llms.txt                  # Root navigation
├── CLAUDE.md                 # Project overview
├── BPD-README.md             # Development guide
└── README.md                 # This file
```

---

## 🔧 Development

### Adding a New Probe Type

**Example: Laser FI probe**

1. **Create driver** implementing `FIProbeInterface`:

```python
# bpd/bpd-drivers/src/bpd_drivers/laser_fi.py

from bpd_core import FIProbeInterface, ProbeCapabilities, register_driver

@register_driver("laser_fi")
class LaserFIDriver:
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

2. **Export in `__init__.py`**:

```python
from bpd_drivers.laser_fi import LaserFIDriver

__all__ = ["DS1120ADriver", "LaserFIDriver"]
```

3. **Use same VHDL interface** (adjust generics for timing):

```vhdl
probe_ctrl : entity work.fi_probe_interface
    generic map (
        PULSE_WIDTH_BITS => 16,
        VOLTAGE_BITS => 16,
        COOLDOWN_CYCLES => 10  -- Faster cooldown for laser
    )
    port map (
        -- Same interface as DS1120A!
    );
```

**[Complete Guide → bpd/bpd-drivers/CLAUDE.md](bpd/bpd-drivers/CLAUDE.md)**

### Running Tests

```bash
# Python tests
pytest bpd/bpd-core/tests/
pytest bpd/bpd-drivers/tests/

# VHDL tests (CocoTB)
cd bpd/bpd-vhdl/tests
pytest test_fi_interface.py

# All tests
pytest

# Skip hardware tests (no physical probe required)
pytest -m "not hardware"
```

### Building Documentation

Documentation uses a **3-tier system** optimized for AI navigation:

- **Tier 1 (llms.txt):** Quick reference (~500-1000 tokens)
- **Tier 2 (CLAUDE.md):** Architecture guide (~3-5k tokens)
- **Tier 3 (Source):** Implementation details

Each component has its own llms.txt and CLAUDE.md for progressive disclosure.

---

## 🧪 Hardware Integration

### VHDL Integration Example

```vhdl
architecture rtl of emfi_instrument is
    signal arm_reg : std_logic;
    signal trigger_reg : std_logic;
    signal pulse_width_reg : unsigned(15 downto 0);
    signal voltage_reg : unsigned(15 downto 0);
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
            trigger_in => trigger_reg,
            arm => arm_reg,
            pulse_width => pulse_width_reg,
            voltage_ctrl => voltage_reg,
            probe_trigger => OUT1,  -- To probe hardware
            ready => status_ready,
            busy => status_busy,
            fault => status_fault
        );
end architecture;
```

### Python Control Flow

```python
from moku import MokuGo

# Deploy bitstream with BPD VHDL
moku = MokuGo(ip="192.168.1.1")
moku.deploy_instrument("emfi_instrument.tar")

# Configure via registers
moku.set_control_register(0, pulse_width_ns)
moku.set_control_register(1, voltage_digital)

# Arm
moku.set_control_register(2, 1)

# Trigger
moku.set_control_register(3, 1)
moku.set_control_register(3, 0)

# Check status
ready = moku.get_status_register(0)
busy = moku.get_status_register(1)
fault = moku.get_status_register(2)
```

---

## 📚 Documentation

### Quick Navigation

| Component | Purpose | Quick Ref | Full Guide |
|-----------|---------|-----------|------------|
| **bpd-core** | Generic framework | [llms.txt](bpd/bpd-core/llms.txt) | [CLAUDE.md](bpd/bpd-core/CLAUDE.md) |
| **bpd-drivers** | Probe drivers | [llms.txt](bpd/bpd-drivers/llms.txt) | [CLAUDE.md](bpd/bpd-drivers/CLAUDE.md) |
| **bpd-vhdl** | VHDL interface | [llms.txt](bpd/bpd-vhdl/llms.txt) | [CLAUDE.md](bpd/bpd-vhdl/CLAUDE.md) |
| **Root** | Project overview | [llms.txt](llms.txt) | [CLAUDE.md](CLAUDE.md) |

### User Guides

- **[BPD-README.md](BPD-README.md)** - Complete development guide
- **[examples/quickstart.py](bpd/examples/quickstart.py)** - Working example

### For AI Assistants

This project uses a **3-tier documentation pattern** optimized for context-efficient AI navigation:

1. Load `llms.txt` first (quick facts, ~1k tokens)
2. Load `CLAUDE.md` for design questions (~5k tokens)
3. Read source code only when implementing

Start with **[llms.txt](llms.txt)** for component catalog.

---

## 🗺️ Roadmap

### v0.1.0 (Current) ✅

- [x] BPD Core framework
- [x] DS1120A EMFI driver (reference)
- [x] Generic VHDL interface with FSM
- [x] Voltage safety validation
- [x] CocoTB test suite
- [x] Complete 3-tier documentation

### v0.2.0 (Next)

- [ ] Laser FI probe driver
- [ ] Example Moku instrument using BPD
- [ ] Hardware testing with physical DS1120A
- [ ] Extended VHDL test coverage
- [ ] Performance benchmarking

### v0.3.0 (Future)

- [ ] RF injection probe driver
- [ ] Voltage glitching probe driver
- [ ] Multi-probe coordination
- [ ] Advanced triggering patterns (burst, sweep)
- [ ] Real-time feedback integration

---

## 🤝 Contributing

Contributions welcome! BPD-002 is under active development.

### Areas Needing Help

- 🔧 Additional probe drivers (laser FI, RF, voltage glitch)
- 📝 Documentation improvements
- 🧪 VHDL test coverage expansion
- 🎯 Example Moku instruments

### Development Setup

```bash
# Fork and clone
git clone --recurse-submodules https://github.com/YOUR-USERNAME/BPD-002.git
cd BPD-002

# Install in editable mode
uv sync
cd bpd/bpd-core && uv pip install -e . && cd ../..
cd bpd/bpd-drivers && uv pip install -e . && cd ../..

# Make changes
# ...

# Run tests
pytest

# Submit PR
```

### Coding Standards

- Follow existing code style (black + ruff)
- Write tests for new features
- Update documentation (llms.txt + CLAUDE.md)
- Use type hints

---

## 📜 License

MIT License - see [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

- DS1120A specifications from [riscure-models](https://github.com/sealablab/riscure-models)
- Moku platform support via [moku-models](https://github.com/sealablab/moku-models)
- VHDL utilities from [forge-vhdl](https://github.com/sealablab/moku-instrument-forge-vhdl)
- Code generation via [forge-codegen](https://github.com/sealablab/moku-instrument-forge-codegen)

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/sealablab/BPD-002/issues)
- **Discussions:** [GitHub Discussions](https://github.com/sealablab/BPD-002/discussions)
- **Documentation:** Start with [llms.txt](llms.txt) or [CLAUDE.md](CLAUDE.md)

---

## 🔗 Related Projects

- [moku-models](https://github.com/sealablab/moku-models) - Moku platform specifications
- [riscure-models](https://github.com/sealablab/riscure-models) - Riscure probe specifications
- [forge-vhdl](https://github.com/sealablab/moku-instrument-forge-vhdl) - VHDL component library
- [forge-codegen](https://github.com/sealablab/moku-instrument-forge-codegen) - YAML → VHDL generator

---

**Built for researchers, by researchers** 🔬 | **MIT License** | **v0.1.0**
