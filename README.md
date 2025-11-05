# BPD-002: Basic Probe Driver

Multi-vendor probe integration framework for Moku platform fault injection development.

## Quick Start

After cloning this repository, simply run:

```bash
./setup.sh
```

This intelligent setup script will:
1. Automatically initialize all git submodules (forge-vhdl, moku-models, riscure-models, forge-codegen)
2. Run `uv sync` to install all workspace dependencies
3. Set up your development environment

### What if I already ran `git submodule update --init --recursive`?

That's fine! You can still run `./setup.sh` - it will detect that submodules are already initialized and proceed directly to `uv sync`.

Alternatively, if submodules are already initialized, you can run `uv sync` directly.

## Manual Setup (Alternative)

If you prefer manual setup:

```bash
# 1. Initialize submodules
git submodule update --init --recursive

# 2. Install dependencies
uv sync

# 3. Activate virtual environment
source .venv/bin/activate
```

## Project Structure

This is a workspace monorepo containing:

### Upstream Dependencies (Git Submodules)
- `libs/forge-vhdl` - VHDL testing framework
- `libs/moku-models` - Moku platform specifications
- `libs/riscure-models` - Riscure equipment specifications
- `tools/forge-codegen` - Code generation tools

### BPD Development Packages
- `bpd/bpd-core` - Generic fault injection probe driver framework
- `bpd/bpd-drivers` - Probe-specific implementations (DS1120A, etc.)
- `bpd/bpd-vhdl` - VHDL components for probe integration

## Development

```bash
# Activate virtual environment
source .venv/bin/activate

# Run tests
pytest

# Run tests for specific package
pytest bpd/bpd-core/tests

# Format code
black .
ruff check .
```

## Requirements

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager
- Git

### Installing uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Documentation

See `CLAUDE.md` files in each package directory for detailed architecture and design documentation.

## License

MIT
