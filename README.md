# BPD-002: Basic Probe Driver

Multi-vendor fault injection probe integration framework for Moku platform development.

## Development Workflow

This project uses **session-based branching** for organized development:

1. Start from `main` branch
2. Read `bpd/bpd-sessions/NEXT-SESSION.md` for instructions
3. Create dated branch: `session/YYYY-MM-DD-description`
4. Work, commit, test
5. Merge to `main` and delete session branch

This keeps the repository clean while maintaining clear session history and goals. See [bpd/bpd-sessions/NEXT-SESSION.md](bpd/bpd-sessions/NEXT-SESSION.md) for the complete workflow template.

## What is BPD-002?

**BPD-002** is a complete probe driver framework for integrating fault injection probes (EMFI, laser FI, RF, voltage glitching) with Moku FPGA platforms (Go/Lab/Pro/Delta). Uses composable git submodules for: type system → code generation → VHDL implementation → hardware deployment.

**Current Status:** v0.1.0 - DS1120A EMFI reference implementation complete

**Key Innovation:** Vendor-agnostic Python + VHDL architecture enables writing probe drivers once and using them across multiple probe types.

**Architecture:** v2.0.0 - Clean separation between tools and foundational libraries (flat structure)

## Quick Start

After cloning this repository, simply run:

```bash
./setup.sh
```

This will initialize git submodules and install all dependencies.

For detailed setup:

```bash
# Clone with submodules
git clone --recurse-submodules https://github.com/sealablab/BPD-002.git
cd BPD-002

# Setup Python environment
uv sync

# Install BPD packages
cd bpd/bpd-core && uv pip install -e . && cd ../..
cd bpd/bpd-drivers && uv pip install -e . && cd ../..
cd bpd/bpd-vhdl && uv pip install -e . && cd ../..

# Run tests
pytest
```

## Project Structure

This is a workspace monorepo with:

### BPD Application (This Project)

| Component | Purpose | Quick Ref |
|-----------|---------|-----------|
| [bpd-core](bpd/bpd-core/) | Generic probe driver framework (Python) | [llms.txt](bpd/bpd-core/llms.txt) |
| [bpd-drivers](bpd/bpd-drivers/) | Probe-specific drivers (DS1120A + planned) | [llms.txt](bpd/bpd-drivers/llms.txt) |
| [bpd-vhdl](bpd/bpd-vhdl/) | Vendor-agnostic VHDL probe interface | [llms.txt](bpd/bpd-vhdl/llms.txt) |

### Core Platform (git submodules - upstream dependencies)

| Component | Purpose | Quick Ref |
|-----------|---------|-----------|
| [moku-models](libs/moku-models/) | **REQUIRED** - Moku platform specifications (Go/Lab/Pro/Delta) | [llms.txt](libs/moku-models/llms.txt) |
| [riscure-models](libs/riscure-models/) | DS1120A probe specs (reference) | [llms.txt](libs/riscure-models/llms.txt) |

### VHDL Development Tools (git submodules - upstream dependencies)

| Component | Purpose | Quick Ref |
|-----------|---------|-----------|
| [forge-codegen](tools/forge-codegen/) | YAML → VHDL code generator (23-type system) | [llms.txt](tools/forge-codegen/llms.txt) |
| [forge-vhdl](libs/forge-vhdl/) | Reusable VHDL components + voltage utilities | [llms.txt](libs/forge-vhdl/llms.txt) |

Each component follows a **three-tier documentation pattern**: `llms.txt` → `CLAUDE.md` → source code

## Four Authoritative Sources of Truth

This repository uses **Progressive Disclosure Architecture (PDA)** for token-efficient navigation. The four authoritative sources (in git submodules) are:

1. **libs/moku-models/llms.txt** - Moku platform specifications (Go/Lab/Pro/Delta)
   - Clock frequencies, voltage ranges, I/O configurations
   - Platform constants: `MOKU_GO_PLATFORM`, `MOKU_LAB_PLATFORM`, `MOKU_PRO_PLATFORM`, `MOKU_DELTA_PLATFORM`
   - Deployment configuration models (`MokuConfig`, `SlotConfig`, `MokuConnection`)

2. **libs/riscure-models/llms.txt** - DS1120A probe specifications
   - Electrical specifications for Riscure FI/SCA probes
   - Voltage-safe wiring validation patterns
   - Platform constant: `DS1120A_PLATFORM` (450V, 64A, fixed 50ns pulse)

3. **libs/forge-vhdl/llms.txt** - VHDL utilities and components
   - Reusable VHDL packages (voltage domains, LUTs, clock dividers)
   - CocoTB progressive testing infrastructure
   - Three voltage domains: 3.3V, 5V, ±5V

4. **tools/forge-codegen/llms.txt** - YAML → VHDL code generator
   - 23-type system with automatic register packing
   - Type-safe register serialization (50-75% register space savings)
   - Entry point: `python -m forge_codegen.generator.codegen spec.yaml`

**Never guess specifications** - always read these authoritative sources.

## Basic Usage

### Using the DS1120A Driver

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
driver.set_voltage(3.3)  # volts
driver.set_pulse_width(100)  # nanoseconds
driver.arm()
driver.trigger()

print(driver.get_status())
```

### Platform Specifications

```python
from moku_models import MOKU_GO_PLATFORM, MOKU_DELTA_PLATFORM

# Query platform specs
platform = MOKU_GO_PLATFORM
print(f"Clock: {platform.clock_mhz} MHz")  # 125 MHz
print(f"Period: {platform.clock_period_ns} ns")  # 8 ns

# Get specific port
in1 = platform.get_analog_input_by_id('IN1')
print(f"IN1: {in1.resolution_bits}-bit @ {in1.sample_rate_msa} MSa/s")
```

### Probe Specifications

```python
from riscure_models import DS1120A_PLATFORM

probe = DS1120A_PLATFORM
trigger = probe.get_port_by_id('digital_glitch')
print(f"Trigger: {trigger.get_voltage_range_str()}")  # "0.0V to 3.3V"

# Validate voltage compatibility
safe = trigger.is_voltage_compatible(3.3)  # True
```

## Common Workflows

### Create New Probe Driver

**Task:** "Add laser FI probe support"
- **→ Read:** [bpd/bpd-drivers/llms.txt](bpd/bpd-drivers/llms.txt)
- **→ Deep dive:** [bpd/bpd-drivers/CLAUDE.md](bpd/bpd-drivers/CLAUDE.md)

### Validate Probe with Moku

**Task:** "Check if probe voltage compatible with Moku Go"
- **→ Read:** [bpd/bpd-core/llms.txt](bpd/bpd-core/llms.txt)
- **→ Function:** `validate_probe_moku_compatibility()`

### Integrate VHDL Interface

**Task:** "Add FI probe control to Moku instrument"
- **→ Read:** [bpd/bpd-vhdl/llms.txt](bpd/bpd-vhdl/llms.txt)
- **→ Component:** `fi_probe_interface.vhd`

### Type System Lookup

**Task:** "What voltage types are available?"
- **→ Read:** [tools/forge-codegen/llms.txt](tools/forge-codegen/llms.txt) (section: "Basic Usage" → Type System)

### Platform Specs Lookup

**Task:** "What's Moku:Go clock frequency?"
- **→ Read:** [libs/moku-models/llms.txt](libs/moku-models/llms.txt)

## Tiered Documentation System

This repository uses a **three-tier documentation pattern** optimized for efficient context loading:

### Tier 1: Quick Reference (Always load first)
- **Files:** All `llms.txt` files (~150-200 lines each)
- **Purpose:** Essential facts, API surface, common tasks
- **Token cost:** ~500-1000 tokens each

**BPD Components:**
- `bpd/bpd-core/llms.txt` - Generic probe framework
- `bpd/bpd-drivers/llms.txt` - Probe-specific drivers
- `bpd/bpd-vhdl/llms.txt` - VHDL probe interface

**Upstream Libraries:**
- `tools/forge-codegen/llms.txt` - YAML → VHDL generation
- `libs/forge-vhdl/llms.txt` - VHDL utilities
- `libs/moku-models/llms.txt` - Moku platform specs
- `libs/riscure-models/llms.txt` - DS1120A probe specs

### Tier 2: Deep Context (Load when designing/integrating)
- **Files:** `CLAUDE.md` files (~3-5k tokens each)
- **Purpose:** Design rationale, integration patterns, development workflows
- **When:** Designing new features, understanding architecture

### Tier 3: Implementation (Load when modifying code)
- **Files:** Source code, tests, specialized docs
- **Purpose:** Detailed implementation logic
- **When:** Actually writing/modifying code

**For AI Assistants:** See [.claude/shared/CONTEXT_MANAGEMENT.md](.claude/shared/CONTEXT_MANAGEMENT.md) for complete token optimization strategy. Load minimally (llms.txt first), expand as needed (CLAUDE.md for design, source for implementation). This keeps 95% of your token budget available for actual work.

**For Cursor users:** The `.cursorrules` file provides automatic navigation instructions. Cursor will automatically follow the three-tier documentation pattern. See [CURSOR.md](CURSOR.md) for Cursor-specific documentation.

## Platform Comparison

| Platform | Slots | I/O | Clock | DIO | Use Case |
|----------|-------|-----|-------|-----|----------|
| Go | 2 | 2×2 | 125 MHz | 16 pins | Education, portable |
| Lab | 2 | 2×2 | 500 MHz | None | Research, low noise |
| Pro | 4 | 4×4 | 1.25 GHz | None | High-performance |
| Delta | 3 | 8×8 | 5 GHz | 32 pins | Ultra-performance |

## Probe Comparison

| Model | Type | Pulse Width | Max Voltage | Max Current | Status |
|-------|------|-------------|-------------|-------------|--------|
| DS1120A | Unidirectional | 50ns (fixed) | 450V | 64A | ✅ Implemented |
| DS1121A | Bidirectional | 4-200ns (adjustable) | 100V | TBD | 🚧 Planned |

## Development

```bash
./setup.sh              # Initialize and install
source .venv/bin/activate
pytest                  # Run tests
```

## Requirements

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager
- Git

## Git Submodule Workflow

```bash
# Initialize all submodules
git submodule update --init --recursive

# Update specific submodule
cd libs/moku-models
git pull origin main
cd ../..
git add libs/moku-models
git commit -m "Update moku-models submodule"

# Push both submodule and parent
git push
```

## Key Design Principles

1. **Clean Separation (v2.0)** - tools/ vs libs/ (no nested submodules)
2. **Tiered docs** - llms.txt (quick ref) → CLAUDE.md (deep dive) → source
3. **Agent delegation** - Monorepo coordinates, submodules execute
4. **Single source of truth** - Each submodule is authoritative for its domain
5. **Context efficiency** - Load minimally, expand as needed
6. **Type safety throughout** - Pydantic validation, voltage domain safety

## Documentation

### Architecture Overview
- **Architecture overview:** [.claude/shared/ARCHITECTURE_OVERVIEW.md](.claude/shared/ARCHITECTURE_OVERVIEW.md) (v2.0)
- **Context management:** [.claude/shared/CONTEXT_MANAGEMENT.md](.claude/shared/CONTEXT_MANAGEMENT.md)
- **AI navigation (general):** [HUMAN_AI_JUMPSTART.md](HUMAN_AI_JUMPSTART.md)
- **Cursor-specific:** [CURSOR.md](CURSOR.md) - Cursor adaptation of PDA pattern

### Component Documentation
- **BPD Core:** [bpd/bpd-core/llms.txt](bpd/bpd-core/llms.txt) | [CLAUDE.md](bpd/bpd-core/CLAUDE.md)
- **BPD Drivers:** [bpd/bpd-drivers/llms.txt](bpd/bpd-drivers/llms.txt) | [CLAUDE.md](bpd/bpd-drivers/CLAUDE.md)
- **BPD VHDL:** [bpd/bpd-vhdl/llms.txt](bpd/bpd-vhdl/llms.txt) | [CLAUDE.md](bpd/bpd-vhdl/CLAUDE.md)

### Submodule Context
- **forge-codegen:** [llms.txt](tools/forge-codegen/llms.txt) | [CLAUDE.md](tools/forge-codegen/CLAUDE.md)
- **forge-vhdl:** [llms.txt](libs/forge-vhdl/llms.txt) | [CLAUDE.md](libs/forge-vhdl/CLAUDE.md)
- **moku-models:** [llms.txt](libs/moku-models/llms.txt) | [CLAUDE.md](libs/moku-models/CLAUDE.md)
- **riscure-models:** [llms.txt](libs/riscure-models/llms.txt) | [CLAUDE.md](libs/riscure-models/CLAUDE.md)

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

### 📋 Planned

- [ ] Multi-probe support (simultaneous use of different probes)
- [ ] Probe switching/multiplexing
- [ ] Advanced triggering patterns
- [ ] Pulse train generation
- [ ] Voltage sweep automation

## Contributing

BPD is under active development. Contributions welcome!

**Areas needing help:**
- Additional probe drivers (laser FI, RF, voltage glitching)
- VHDL test coverage
- Documentation improvements
- Example Moku instruments

---

**Version:** v0.1.0  
**Architecture:** v2.0.0 (Clean separation: tools + flat libs)  
**License:** MIT  
**Main Branch:** main
