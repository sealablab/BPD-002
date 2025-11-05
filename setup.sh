#!/bin/bash
# Intelligent setup script for BPD-002 monorepo
# Handles git submodules initialization before running uv sync

set -e

echo "🚀 BPD-002 Setup - Initializing workspace..."
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for required tools
if ! command_exists git; then
    echo "❌ Error: git is not installed"
    exit 1
fi

if ! command_exists uv; then
    echo "❌ Error: uv is not installed"
    echo "   Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Step 1: Initialize git submodules
echo "📦 Step 1: Initializing git submodules..."
if [ -f .gitmodules ]; then
    if git submodule update --init --recursive; then
        echo "✅ Git submodules initialized successfully"
        echo ""
    else
        echo "❌ Failed to initialize git submodules"
        exit 1
    fi
else
    echo "⚠️  No .gitmodules found - skipping submodule initialization"
    echo ""
fi

# Step 2: Run uv sync
echo "🔧 Step 2: Running uv sync to install dependencies..."
if uv sync "$@"; then
    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "You can now:"
    echo "  • Activate the virtual environment: source .venv/bin/activate"
    echo "  • Run tests: pytest"
    echo "  • Start developing!"
else
    echo ""
    echo "❌ uv sync failed"
    exit 1
fi
