# 🔓 GHDL Installation Challenge: Unlock the Sandbox

**Mission:** Install GHDL in the Claude Code web sandbox despite sudo restrictions.

**Background:** Previous session (P2) completed a 471-line VHDL FSM but couldn't test it because GHDL installation failed with sudo permission errors. Your job: Find a way to install GHDL **without sudo**.

---

## 🎯 Challenge Objectives

1. **Primary Goal:** Get `ghdl --version` working in the sandbox
2. **Secondary Goal:** Compile the P2 FSM to verify it works
3. **Bonus:** Document the solution for future sessions

---

## ⚠️ Known Blocker (Kink #6)

Previous attempt failed with:
```bash
sudo apt-get install ghdl-llvm

# Error:
sudo: /etc/sudo.conf is owned by uid 999, should be 0
sudo: /etc/sudoers is owned by uid 999, should be 0
sudo: error initializing audit plugin sudoers_audit
```

**Constraint:** Sandbox runs as non-root user (uid 999) with broken sudo config.

---

## 🔍 Step 1: Reconnaissance

First, understand your environment:

```bash
# Run the recon script
bash tools/sandbox-recon.sh > sandbox-recon-output.txt

# Review what you have
cat sandbox-recon-output.txt
```

Key questions:
- What OS/distro? (Ubuntu? Debian? Alpine?)
- What package managers are available?
- Do you have write access to `/usr/local`?
- Do you have write access to `$HOME`?
- Is `/tmp` writable?
- Can you download files? (curl/wget available?)

---

## 💡 Installation Strategies to Try

### Strategy 1: User-Local Install (No Sudo)

**Idea:** Build GHDL from source in `$HOME` or `/tmp`

```bash
# Check if you can write to home
mkdir -p $HOME/local
cd $HOME/local

# Try downloading GHDL source
curl -L https://github.com/ghdl/ghdl/archive/refs/tags/v4.1.0.tar.gz -o ghdl.tar.gz

# Extract and build
tar xzf ghdl.tar.gz
cd ghdl-4.1.0

# Configure for user install
./configure --prefix=$HOME/local

# Build
make

# Install to $HOME/local/bin
make install

# Add to PATH
export PATH=$HOME/local/bin:$PATH

# Test
ghdl --version
```

**Pros:** No sudo needed
**Cons:** Requires build tools (gcc, make), takes time

---

### Strategy 2: Pre-built Binary

**Idea:** Download pre-compiled GHDL binary

```bash
# Find GHDL releases
# https://github.com/ghdl/ghdl/releases

# Download appropriate binary for your architecture
cd $HOME
curl -L <BINARY_URL> -o ghdl-binary.tar.gz

# Extract
tar xzf ghdl-binary.tar.gz

# Add to PATH
export PATH=$HOME/ghdl/bin:$PATH

# Test
ghdl --version
```

**Pros:** Fastest if binary exists
**Cons:** Need correct arch/OS match

---

### Strategy 3: Conda/Mamba Install

**Idea:** Use conda package manager (no sudo required)

```bash
# Check if conda/mamba available
command -v conda || command -v mamba

# If not, install miniconda
curl -L https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o miniconda.sh
bash miniconda.sh -b -p $HOME/miniconda
export PATH=$HOME/miniconda/bin:$PATH

# Search for GHDL
conda search ghdl

# Install if available
conda install -c conda-forge ghdl

# Test
ghdl --version
```

**Pros:** Conda doesn't need sudo
**Cons:** Large download, might not have GHDL

---

### Strategy 4: Nix Package Manager

**Idea:** Nix allows user-level package installs

```bash
# Install Nix (single-user mode, no sudo)
curl -L https://nixos.org/nix/install | sh -s -- --no-daemon

# Source nix
. $HOME/.nix-profile/etc/profile.d/nix.sh

# Install GHDL
nix-env -iA nixpkgs.ghdl

# Test
ghdl --version
```

**Pros:** Powerful, no sudo
**Cons:** Nix is heavy, slow first time

---

### Strategy 5: AppImage / Portable Binary

**Idea:** Self-contained executable

```bash
# Check if GHDL has an AppImage
# (Search: ghdl appimage)

# If found:
cd $HOME
curl -L <APPIMAGE_URL> -o ghdl.AppImage
chmod +x ghdl.AppImage

# Run directly
./ghdl.AppImage --version

# Or create wrapper
mkdir -p $HOME/bin
echo '#!/bin/bash' > $HOME/bin/ghdl
echo "$HOME/ghdl.AppImage \"\$@\"" >> $HOME/bin/ghdl
chmod +x $HOME/bin/ghdl
export PATH=$HOME/bin:$PATH
```

**Pros:** Single file, no install
**Cons:** AppImage may not exist for GHDL

---

### Strategy 6: Docker/Podman Container

**Idea:** Run GHDL inside container

```bash
# Check if docker/podman available
command -v docker || command -v podman

# Pull GHDL container
docker pull ghdl/ghdl:latest

# Run compilation inside container
docker run --rm -v $(pwd):/work ghdl/ghdl:latest ghdl -a --std=08 /work/bpd/bpd-vhdl/src/basic_probe_driver_custom_inst_main.vhd
```

**Pros:** Isolated, reproducible
**Cons:** Requires docker access (might also be restricted)

---

### Strategy 7: Use System GHDL (If Exists)

**Idea:** Maybe GHDL is already installed but not in PATH

```bash
# Search entire filesystem
find /usr /opt /snap /home -name ghdl -type f 2>/dev/null

# If found, create symlink or add to PATH
ln -s /path/to/ghdl $HOME/bin/ghdl
export PATH=$HOME/bin:$PATH
```

**Pros:** Instant if it exists
**Cons:** Unlikely in sandbox

---

## 🧪 Step 2: Test Installation

Once you think GHDL is installed:

```bash
# Verify installation
ghdl --version

# Should show something like:
# GHDL 4.1.0 (v4.1.0)
#  Compiled with GNAT Version: XX.X.X
#  llvm code generator

# Test basic compilation
cd bpd/bpd-vhdl/src
ghdl -a --std=08 basic_probe_driver_custom_inst_main.vhd

# If successful:
echo "✅ GHDL INSTALLED AND WORKING!"
```

---

## 📝 Step 3: Compile P2 FSM

```bash
cd bpd/bpd-vhdl

# Compile dependencies first (if needed)
# You may need to compile forge-vhdl packages

# Compile the FSM
ghdl -a --std=08 src/basic_probe_driver_custom_inst_main.vhd

# Check for errors
# If compilation succeeds → P2 FSM is valid!
# If errors → document syntax issues as new kink
```

---

## 📊 Step 4: Document Your Solution

Update `bpd/bpd-sessions/DRY-RUN-FINDINGS.md`:

```markdown
### 🟢 KINK #6: GHDL Installation in Sandbox (RESOLVED)

**Problem:** Sudo blocked in Claude Code web sandbox

**Solution:** [Describe what worked]

**Steps:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Installation command:**
```bash
[Your winning command]
```

**Verification:**
```bash
ghdl --version
# [Output]
```

**Status:** ✅ RESOLVED
```

---

## 🎯 Success Criteria

### Minimum Success
- [ ] `ghdl --version` works
- [ ] Can compile simple VHDL file
- [ ] Document solution in DRY-RUN-FINDINGS.md

### Full Success
- [ ] P2 FSM compiles without errors
- [ ] Installation is reproducible (script/command)
- [ ] Solution works in future web sessions

### Bonus Points
- [ ] Installation takes < 5 minutes
- [ ] Doesn't require large downloads (> 500MB)
- [ ] Can be added to setup.sh as fallback

---

## 🆘 If All Else Fails

**Document the failure thoroughly:**

1. List all strategies attempted
2. Include error messages
3. Save recon output
4. Note what permissions/tools were missing

**Then:**
- Mark Kink #6 as "BLOCKED - requires different sandbox environment"
- Recommend testing FSM compilation outside sandbox
- Proceed to document FSM design decisions instead

---

## 💭 Creative Ideas

**Think outside the box:**
- Can you use `pip` to install a Python wrapper for GHDL?
- Can you cross-compile on a different system and copy binary?
- Can you use WebAssembly version of GHDL?
- Can you use VHDL linter instead of compiler?
- Can you request different sandbox environment from Claude?

---

## 🚀 Ready?

```bash
# 1. Recon
bash tools/sandbox-recon.sh > recon.txt
cat recon.txt

# 2. Pick a strategy
# (Start with Strategy 1 or 2 - fastest)

# 3. Try it!

# 4. Document results
```

**Good luck! Break down that wall! 🔨**

---

**Previous P2 Work:**
- FSM implementation: `bpd/bpd-vhdl/src/basic_probe_driver_custom_inst_main.vhd`
- Kink #6 documentation: `bpd/bpd-sessions/DRY-RUN-FINDINGS.md`
- Web AI session: `claude/vhdl-fsm-implementation-011CUqE8U5XD3ffqygntJxua`

