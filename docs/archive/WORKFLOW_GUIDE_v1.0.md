# Development Workflow Guide

Quick reference for common development workflows in this mono-repo.

## Daily Workflow

### Starting Your Day

```bash
# 1. Make sure you're on main and up-to-date
git checkout main
git pull origin main

# 2. Update submodules (foundational libraries might have updates)
git submodule update --init --recursive

# 3. Check what probes exist
# (Use Claude Code agent command)
/probe-status
```

---

## Developing a New Probe

### Workflow: New Probe from Scratch

**Branch naming:** `feature/probe-name` (e.g., `feature/ds1180-laser`)

```bash
# 1. Create feature branch
git checkout -b feature/ds1180-laser

# 2. Initialize probe structure
/init-probe DS1180_LASER

# 3. Edit YAML specification
# Edit: forge/apps/DS1180_LASER/DS1180_LASER.yaml
# - Define datatypes (voltage, time, boolean signals)
# - Set platform (moku_go, moku_lab, moku_pro, moku_delta)
# - Choose mapping strategy (type_clustering recommended)

# 4. Validate YAML
/validate forge/apps/DS1180_LASER/DS1180_LASER.yaml

# 5. Generate VHDL package
/generate forge/apps/DS1180_LASER/DS1180_LASER.yaml
# This creates:
#   - DS1180_LASER_custom_inst_shim.vhd (auto-generated, DON'T EDIT)
#   - DS1180_LASER_custom_inst_main.vhd (your implementation goes here)
#   - manifest.json
#   - control_registers.json

# 6. Implement custom VHDL
# Edit: forge/apps/DS1180_LASER/DS1180_LASER_custom_inst_main.vhd
# Use friendly signal names from manifest.json

# 7. (Optional) Cross-validate implementation
/cross-validate DS1180_LASER

# 8. Commit your work
git add forge/apps/DS1180_LASER/
git commit -m "feat: Add DS1180 laser probe YAML spec and implementation

- Define 8 datatypes for laser control
- Implement FSM with READY/ARMED/FIRING/COOLING states
- Target platform: moku_go"

# 9. Deploy to hardware (when ready)
/deploy DS1180_LASER --device 192.168.1.100

# 10. Monitor and debug
/monitor-state DS1180_LASER
```

---

## Iterating on Existing Probe

**Branch naming:** `feat/probe-enhancement` or `fix/probe-issue`

```bash
# 1. Create branch
git checkout -b feat/ds1180-add-triggers

# 2. Edit YAML (add new signals, modify mappings)
# Edit: forge/apps/DS1180_LASER/DS1180_LASER.yaml

# 3. Regenerate package
/generate forge/apps/DS1180_LASER/DS1180_LASER.yaml --force

# 4. Update custom VHDL for new signals
# Edit: forge/apps/DS1180_LASER/DS1180_LASER_custom_inst_main.vhd

# 5. Test and commit
git add forge/apps/DS1180_LASER/
git commit -m "feat: Add trigger inputs to DS1180 laser probe"

# 6. Redeploy
/deploy DS1180_LASER --device 192.168.1.100
```

---

## Fixing a Bug

**Branch naming:** `fix/bug-description`

```bash
# 1. Create fix branch
git checkout -b fix/voltage-threshold-off-by-one

# 2. Make changes in appropriate location:
#    - YAML spec: forge/apps/<probe>/
#    - VHDL implementation: forge/apps/<probe>/*_main.vhd
#    - Foundational library: update submodule (see below)

# 3. Test the fix
/deploy <probe> --device <ip>
/monitor-state <probe>

# 4. Commit with clear description
git add .
git commit -m "fix: Correct voltage threshold calculation in DS1180

The threshold was off by one due to signed/unsigned conversion.
Changed comparison from >= to > in FSM state machine.

Fixes: voltage trigger not firing at exact threshold"

# 5. Merge when verified
git checkout main
git merge fix/voltage-threshold-off-by-one --no-ff
git push origin main
```

---

## Working with Submodules

### Updating a Foundational Library

If you need to fix/enhance a foundational library (basic-app-datatypes, moku-models, riscure-models):

```bash
# 1. Navigate to the submodule
cd forge/libs/basic-app-datatypes

# 2. Create branch IN THE SUBMODULE
git checkout -b fix/add-10v-voltage-type

# 3. Make changes, commit IN THE SUBMODULE
git add .
git commit -m "feat: Add voltage_output_10v_s16 type"

# 4. Push THE SUBMODULE (to its own repo)
git push origin fix/add-10v-voltage-type

# 5. Create PR in the submodule repo, merge it

# 6. Return to mono-repo root
cd ../../..

# 7. Update submodule reference to new commit
cd forge/libs/basic-app-datatypes
git checkout main
git pull origin main
cd ../../..

# 8. Commit the submodule update in parent repo
git add forge/libs/basic-app-datatypes
git commit -m "chore: Update basic-app-datatypes - add 10V voltage type"
git push origin main
```

**Note:** Submodule work requires access to individual submodule repositories.

---

## Merging Your Work

### After Branch is Complete

```bash
# 1. Make sure branch is up-to-date with main
git checkout main
git pull origin main
git checkout feature/ds1180-laser
git merge main  # or rebase if you prefer

# 2. Run final checks
/probe-status  # Should show your probe as valid

# 3. Merge to main
git checkout main
git merge feature/ds1180-laser --no-ff

# 4. Push
git push origin main

# 5. Clean up branch
git branch -d feature/ds1180-laser
```

### Creating a Release

When you've completed a significant milestone:

```bash
# 1. Make sure main is clean
git checkout main
git status

# 2. Tag with semantic version
git tag -a v1.2.0 -m "v1.2.0: Add DS1180 laser probe support"

# 3. Push tag
git push origin v1.2.0

# 4. Create GitHub release
gh release create v1.2.0 \
  --title "v1.2.0 - DS1180 Laser Probe Support" \
  --notes "Added support for DS1180 laser probe with FSM control"
```

---

## Common Patterns

### Check Status of Everything

```bash
# What probes do I have?
/probe-status

# What's the git status?
git status

# Are submodules up-to-date?
git submodule status

# What branch am I on?
git branch
```

### Emergency: Reset Everything

```bash
# Discard all uncommitted changes
git restore .
git clean -fd

# Reset submodules to expected state
git submodule update --init --recursive --force

# Start fresh
git checkout main
git pull origin main
```

---

## Claude Code Agents Available

Your repo has specialized AI agents. Use them!

### Monorepo-level Agents

Located in `.claude/agents/`:

- **probe-design-orchestrator** - Coordinates complete probe workflows
- **deployment-orchestrator** - Handles hardware deployment
- **hardware-debug** - FSM debugging and signal analysis

### Forge-level Agents

Located in `forge/.claude/agents/`:

- **forge-context** - YAML validation and package generation
- **docgen-context** - Documentation generation
- **forge-pipe-fitter** - Multi-stage pipeline coordination

### Commands Available

- `/init-probe <name>` - Create new probe structure
- `/probe-status` - Show all probe states
- `/validate <yaml>` - Validate YAML spec
- `/generate <yaml>` - Generate VHDL from YAML
- `/deploy <probe> --device <ip>` - Deploy to hardware
- `/cross-validate <probe>` - Verify VHDL ↔ package compatibility
- `/sync-submodules` - Update all submodules

---

## Tips & Best Practices

### Branch Hygiene

- ✅ Create branches for ALL changes (even small ones)
- ✅ Use descriptive branch names
- ✅ Delete branches after merging
- ✅ Keep branches short-lived (< 1 week if possible)

### Commit Messages

Good commit format:
```
<type>: <short summary>

<optional detailed description>

<optional footer>
```

Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`

### Before Committing

- ✅ Run `/probe-status` to verify probe validity
- ✅ Check `git status` to see what's staged
- ✅ Write clear commit messages
- ✅ Don't commit `.obsidian/` or other IDE files

### Submodule Safety

- ⚠️ Be careful when working in submodules
- ⚠️ Always commit in the submodule FIRST, then update parent
- ⚠️ Never force-push to submodule repos without coordinating
- ⚠️ Run `git submodule status` regularly to check for drift

---

## Quick Reference Card

```bash
# Start new probe
git checkout -b feature/probe-name
/init-probe PROBE_NAME
# ... edit YAML, generate, implement ...
git commit -m "feat: Add probe-name support"

# Fix bug
git checkout -b fix/bug-description
# ... make changes ...
git commit -m "fix: Description of what was fixed"

# Merge and release
git checkout main
git merge feature/probe-name --no-ff
git push origin main
git tag -a v1.x.0 -m "Release message"
git push origin v1.x.0
gh release create v1.x.0 --title "..." --notes "..."

# Check status
/probe-status
git submodule status
git status
```

---

**Last Updated:** 2025-11-03
**Repo Version:** v1.1.0
