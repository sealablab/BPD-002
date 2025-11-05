#!/bin/bash
# Pre-sync hook for uv: Initialize git submodules before workspace sync
# This ensures all workspace members (which are git submodules) exist before uv tries to resolve them

set -e

echo "🔄 Initializing git submodules..."

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "⚠️  Not in a git repository, skipping submodule initialization"
    exit 0
fi

# Check if .gitmodules exists
if [ ! -f .gitmodules ]; then
    echo "⚠️  No .gitmodules found, skipping submodule initialization"
    exit 0
fi

# Initialize and update submodules recursively
if git submodule update --init --recursive; then
    echo "✅ Git submodules initialized successfully"
else
    echo "❌ Failed to initialize git submodules"
    exit 1
fi
