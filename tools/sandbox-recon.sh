#!/bin/bash
# Sandbox Reconnaissance Script
# Performs lightweight system enumeration to understand the environment
# Useful for debugging installation issues and understanding sandbox constraints

set +e  # Don't exit on errors - we want to collect all info

echo "=================================="
echo "🔍 Sandbox Environment Reconnaissance"
echo "=================================="
echo ""

# =============================================================================
# 1. BASIC SYSTEM INFO
# =============================================================================
echo "📋 1. BASIC SYSTEM INFO"
echo "-----------------------------------"
echo "Hostname: $(hostname 2>/dev/null || echo 'N/A')"
echo "Username: $(whoami 2>/dev/null || echo 'N/A')"
echo "User ID: $(id -u 2>/dev/null || echo 'N/A')"
echo "Home Dir: $HOME"
echo "Working Dir: $(pwd)"
echo ""

# =============================================================================
# 2. OPERATING SYSTEM
# =============================================================================
echo "🐧 2. OPERATING SYSTEM"
echo "-----------------------------------"
echo "Kernel: $(uname -s 2>/dev/null || echo 'N/A')"
echo "Kernel Version: $(uname -r 2>/dev/null || echo 'N/A')"
echo "Machine: $(uname -m 2>/dev/null || echo 'N/A')"
echo "OS: $(uname -o 2>/dev/null || echo 'N/A')"
echo ""

if [ -f /etc/os-release ]; then
    echo "OS Release Info:"
    cat /etc/os-release
    echo ""
elif [ -f /etc/lsb-release ]; then
    echo "LSB Release Info:"
    cat /etc/lsb-release
    echo ""
fi

# =============================================================================
# 3. PACKAGE MANAGERS
# =============================================================================
echo "📦 3. PACKAGE MANAGERS"
echo "-----------------------------------"
command -v apt-get >/dev/null 2>&1 && echo "✓ apt-get: $(which apt-get)" || echo "✗ apt-get: not found"
command -v apt >/dev/null 2>&1 && echo "✓ apt: $(which apt)" || echo "✗ apt: not found"
command -v yum >/dev/null 2>&1 && echo "✓ yum: $(which yum)" || echo "✗ yum: not found"
command -v dnf >/dev/null 2>&1 && echo "✓ dnf: $(which dnf)" || echo "✗ dnf: not found"
command -v brew >/dev/null 2>&1 && echo "✓ brew: $(which brew)" || echo "✗ brew: not found"
command -v apk >/dev/null 2>&1 && echo "✓ apk: $(which apk)" || echo "✗ apk: not found"
command -v snap >/dev/null 2>&1 && echo "✓ snap: $(which snap)" || echo "✗ snap: not found"
echo ""

# =============================================================================
# 4. SUDO / PERMISSIONS
# =============================================================================
echo "🔐 4. SUDO / PERMISSIONS"
echo "-----------------------------------"
if command -v sudo >/dev/null 2>&1; then
    echo "✓ sudo available: $(which sudo)"
    echo -n "  sudo version: "
    sudo --version 2>/dev/null | head -1 || echo "N/A"

    echo -n "  sudo access test: "
    timeout 2 sudo -n true 2>/dev/null && echo "✓ PASSWORDLESS SUDO!" || echo "✗ requires password or denied"
else
    echo "✗ sudo: not found"
fi

echo -n "Root access: "
if [ "$(id -u)" -eq 0 ]; then
    echo "✓ RUNNING AS ROOT"
else
    echo "✗ non-root (UID: $(id -u))"
fi
echo ""

# =============================================================================
# 5. GHDL INVESTIGATION
# =============================================================================
echo "🔍 5. GHDL INVESTIGATION"
echo "-----------------------------------"
if command -v ghdl >/dev/null 2>&1; then
    echo "✓ GHDL already installed!"
    echo "  Location: $(which ghdl)"
    echo "  Version:"
    ghdl --version 2>&1 | head -5 | sed 's/^/    /'
else
    echo "✗ GHDL not found in PATH"

    # Check if it exists but not in PATH
    echo ""
    echo "  Searching for ghdl binaries..."
    find /usr /opt /home -name ghdl -type f 2>/dev/null | head -5 | sed 's/^/    /' || echo "    (none found)"

    # Check available packages
    echo ""
    echo "  Checking available GHDL packages..."
    if command -v apt-cache >/dev/null 2>&1; then
        echo "    APT packages:"
        apt-cache search ghdl 2>/dev/null | head -10 | sed 's/^/      /' || echo "      (search failed)"
    fi
fi
echo ""

# =============================================================================
# 6. DEVELOPMENT TOOLS
# =============================================================================
echo "🛠️  6. DEVELOPMENT TOOLS"
echo "-----------------------------------"
command -v gcc >/dev/null 2>&1 && echo "✓ gcc: $(gcc --version 2>&1 | head -1)" || echo "✗ gcc: not found"
command -v g++ >/dev/null 2>&1 && echo "✓ g++: $(g++ --version 2>&1 | head -1)" || echo "✗ g++: not found"
command -v clang >/dev/null 2>&1 && echo "✓ clang: $(clang --version 2>&1 | head -1)" || echo "✗ clang: not found"
command -v llvm-config >/dev/null 2>&1 && echo "✓ llvm-config: $(llvm-config --version 2>/dev/null)" || echo "✗ llvm-config: not found"
command -v python3 >/dev/null 2>&1 && echo "✓ python3: $(python3 --version 2>&1)" || echo "✗ python3: not found"
command -v git >/dev/null 2>&1 && echo "✓ git: $(git --version 2>&1)" || echo "✗ git: not found"
command -v make >/dev/null 2>&1 && echo "✓ make: $(make --version 2>&1 | head -1)" || echo "✗ make: not found"
echo ""

# =============================================================================
# 7. NETWORK / INTERNET
# =============================================================================
echo "🌐 7. NETWORK / INTERNET"
echo "-----------------------------------"
echo -n "Internet access: "
if timeout 3 ping -c 1 8.8.8.8 >/dev/null 2>&1; then
    echo "✓ can ping 8.8.8.8"
elif timeout 3 curl -s http://www.google.com >/dev/null 2>&1; then
    echo "✓ HTTP works (ping blocked)"
else
    echo "✗ no internet detected"
fi

echo -n "DNS resolution: "
timeout 3 nslookup google.com >/dev/null 2>&1 && echo "✓ working" || echo "✗ failed"
echo ""

# =============================================================================
# 8. DISK / STORAGE
# =============================================================================
echo "💾 8. DISK / STORAGE"
echo "-----------------------------------"
echo "Disk usage:"
df -h . 2>/dev/null | sed 's/^/  /' || echo "  (df command failed)"
echo ""
echo "Available space in current dir:"
df -h . 2>/dev/null | tail -1 | awk '{print "  " $4 " available"}' || echo "  (unavailable)"
echo ""

# =============================================================================
# 9. CONTAINER DETECTION
# =============================================================================
echo "📦 9. CONTAINER / VIRTUALIZATION DETECTION"
echo "-----------------------------------"
if [ -f /.dockerenv ]; then
    echo "✓ Docker container detected (/.dockerenv exists)"
elif grep -q docker /proc/1/cgroup 2>/dev/null; then
    echo "✓ Docker container detected (cgroup)"
elif [ -f /run/.containerenv ]; then
    echo "✓ Podman container detected"
else
    echo "✗ No obvious container markers"
fi

if [ -f /proc/version ]; then
    grep -qi microsoft /proc/version && echo "✓ WSL detected" || true
fi
echo ""

# =============================================================================
# 10. SANDBOX CONSTRAINTS
# =============================================================================
echo "🔒 10. SANDBOX CONSTRAINTS"
echo "-----------------------------------"
echo "Testing write permissions..."
TEST_FILE="/tmp/recon-test-$$"
if echo "test" > "$TEST_FILE" 2>/dev/null; then
    echo "  ✓ /tmp writable"
    rm -f "$TEST_FILE"
else
    echo "  ✗ /tmp not writable"
fi

echo "Testing network tools..."
command -v curl >/dev/null 2>&1 && echo "  ✓ curl available" || echo "  ✗ curl not found"
command -v wget >/dev/null 2>&1 && echo "  ✓ wget available" || echo "  ✗ wget not found"
echo ""

# =============================================================================
# 11. ENVIRONMENT VARIABLES
# =============================================================================
echo "🔧 11. KEY ENVIRONMENT VARIABLES"
echo "-----------------------------------"
echo "PATH:"
echo "$PATH" | tr ':' '\n' | sed 's/^/  /'
echo ""
echo "Selected vars:"
echo "  HOME=$HOME"
echo "  USER=$USER"
echo "  SHELL=$SHELL"
echo "  TERM=$TERM"
[ -n "$CONTAINER" ] && echo "  CONTAINER=$CONTAINER"
[ -n "$KUBERNETES_SERVICE_HOST" ] && echo "  KUBERNETES_SERVICE_HOST=$KUBERNETES_SERVICE_HOST"
echo ""

# =============================================================================
# 12. GHDL INSTALLATION TEST
# =============================================================================
echo "🧪 12. GHDL INSTALLATION DRY-RUN"
echo "-----------------------------------"
if command -v apt-get >/dev/null 2>&1; then
    echo "Testing apt-get access..."
    echo "  Update repos (dry-run):"
    sudo -n apt-get update --dry-run 2>&1 | head -5 | sed 's/^/    /' || echo "    ✗ Failed (no sudo or denied)"

    echo ""
    echo "  GHDL package info:"
    apt-cache show ghdl-llvm 2>/dev/null | grep -E "^(Package|Version|Description):" | sed 's/^/    /' || echo "    ✗ Package not available"
fi
echo ""

# =============================================================================
# SUMMARY
# =============================================================================
echo "=================================="
echo "📊 SUMMARY"
echo "=================================="
echo ""

# Determine OS
OS_TYPE="Unknown"
if [ -f /etc/os-release ]; then
    OS_TYPE=$(grep "^PRETTY_NAME" /etc/os-release 2>/dev/null | cut -d'"' -f2)
fi

echo "System: $OS_TYPE"
echo "Package Manager: "
command -v apt-get >/dev/null 2>&1 && echo "  - apt-get (Debian/Ubuntu)"
command -v yum >/dev/null 2>&1 && echo "  - yum (RHEL/CentOS)"
command -v brew >/dev/null 2>&1 && echo "  - brew (macOS/Linux)"
echo ""

echo "GHDL Status: "
if command -v ghdl >/dev/null 2>&1; then
    echo "  ✅ INSTALLED"
else
    echo "  ❌ NOT INSTALLED"
    echo ""
    echo "  Recommended installation command:"
    if command -v apt-get >/dev/null 2>&1; then
        if timeout 2 sudo -n true 2>/dev/null; then
            echo "    sudo apt-get update && sudo apt-get install -y ghdl-llvm"
        else
            echo "    (sudo access needed - run: apt-get install ghdl-llvm)"
        fi
    elif command -v brew >/dev/null 2>&1; then
        echo "    brew install ghdl"
    else
        echo "    (no recognized package manager)"
    fi
fi
echo ""

echo "Sudo Access: "
if timeout 2 sudo -n true 2>/dev/null; then
    echo "  ✅ PASSWORDLESS SUDO AVAILABLE"
else
    echo "  ❌ NO PASSWORDLESS SUDO"
fi
echo ""

echo "=================================="
echo "Reconnaissance complete!"
echo "Save this output for debugging."
echo "=================================="
