# GHDL Setup Guide for BPD-002

**Purpose:** Install GHDL for VHDL simulation and CocoTB testing

**Status:** System-level dependency (not installable via pip/uv)

---

## Quick Install (Ubuntu/Debian)

```bash
# Install GHDL with LLVM backend (recommended)
sudo apt-get update
sudo apt-get install -y ghdl-llvm

# Verify installation
ghdl --version
```

**Expected output:**
```
GHDL 2.0.0 (tarball) [Dunoon edition]
 Compiled with GNAT Version: 11.4.0
 llvm code generator
```

---

## What GHDL Provides

**GHDL** is a VHDL compiler/simulator that enables:
- VHDL syntax checking and compilation
- Waveform generation (VCD/FST files)
- CocoTB test execution (via `cocotb-ghdl` interface)
- Hardware simulation before deploying to Moku

---

## Installation Options

### Option 1: LLVM Backend (Recommended)
```bash
sudo apt-get install ghdl-llvm
```
**Pros:** Fast compilation, good performance
**Cons:** Slightly larger install

### Option 2: mcode Backend (Lightweight)
```bash
sudo apt-get install ghdl-mcode
```
**Pros:** Faster to install, smaller footprint
**Cons:** Slower simulation

### Option 3: GCC Backend
```bash
sudo apt-get install ghdl-gcc
```
**Pros:** Maximum compatibility
**Cons:** Slowest option

---

## Integration with BPD-002 Workflow

### 1. Add to setup.sh (Automatic Check)

```bash
# In setup.sh, add after uv check:
if ! command_exists ghdl; then
    echo "⚠️  GHDL not found - VHDL tests will be skipped"
    echo "   Install with: sudo apt-get install ghdl-llvm"
    echo "   See: docs/GHDL_SETUP.md"
fi
```

### 2. Install VHDL Dev Dependencies

```bash
# Install base dependencies
uv sync

# Install VHDL simulation extras
uv sync --extra vhdl

# NOTE: Still requires system GHDL installation
```

### 3. Verify CocoTB + GHDL Integration

```bash
# Test GHDL installation
ghdl --version

# Run VHDL tests (requires GHDL)
cd bpd/bpd-vhdl
pytest tests/

# Or run specific test
pytest tests/test_fi_interface.py -v
```

---

## CocoTB Configuration

CocoTB automatically detects GHDL via environment:

```bash
# Set simulator (optional - auto-detected)
export SIM=ghdl

# Run CocoTB tests
make  # or pytest
```

**Test output filtering:**
- P1 tests: <20 lines (GHDL warnings filtered)
- See `libs/forge-vhdl/CLAUDE.md` for progressive testing levels

---

## Troubleshooting

### GHDL not found after installation

```bash
# Check if installed
which ghdl
dpkg -l | grep ghdl

# If multiple backends installed, select one:
sudo update-alternatives --config ghdl
```

### CocoTB can't find GHDL

```bash
# Ensure ghdl is in PATH
export PATH="/usr/bin:$PATH"

# Verify CocoTB sees it
python -c "import cocotb; print(cocotb.__version__)"
```

### Compilation errors

```bash
# Check VHDL standard version
ghdl --version

# BPD uses VHDL-2008 (default for forge-vhdl)
ghdl -a --std=08 my_file.vhd
```

---

## Why Not pip-installable?

GHDL is a **compiled binary** (C++/Ada), not a Python package:
- Requires system libraries (LLVM, GCC, etc.)
- Platform-specific builds (x86, ARM, etc.)
- Too large for PyPI distribution

**Alternative:** Docker container with GHDL pre-installed (future work)

---

## Docker Option (Future)

```dockerfile
FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y ghdl-llvm python3 python3-pip && \
    pip3 install cocotb pytest

# Copy BPD project...
```

**Usage:**
```bash
docker run -v $(pwd):/workspace bpd-dev pytest
```

---

## CI/CD Integration (GitHub Actions)

```yaml
# .github/workflows/test-vhdl.yml
name: VHDL Tests

on: [push, pull_request]

jobs:
  test-vhdl:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          submodules: recursive

      - name: Install GHDL
        run: |
          sudo apt-get update
          sudo apt-get install -y ghdl-llvm

      - name: Install Python dependencies
        run: |
          pip install uv
          uv sync --extra vhdl

      - name: Run VHDL tests
        run: |
          cd bpd/bpd-vhdl
          pytest tests/ -v
```

---

## References

- **GHDL Homepage:** https://ghdl.github.io/ghdl/
- **CocoTB Docs:** https://docs.cocotb.org/
- **forge-vhdl Testing:** `libs/forge-vhdl/CLAUDE.md`
- **BPD VHDL Tests:** `bpd/bpd-vhdl/tests/`

---

**Created:** 2025-11-05
**Author:** Claude Code (during P2 phase)
**Status:** Ready for use
