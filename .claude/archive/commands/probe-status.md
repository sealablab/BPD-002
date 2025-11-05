# Probe Status

Show development status of all probes in the monorepo.

**Agent:** probe-design-orchestrator

---

## Usage

```
/probe-status
```

No arguments required - scans `forge/apps/` directory (Option A architecture).

## What It Shows

For each probe discovered:
1. **YAML Status** - Valid, invalid, or missing
2. **Package Status** - Generated files present
3. **Deployment Status** - Deployed device IP or not deployed

## Example Output

```
Probe Development Status (Option A)
====================================

DS1140_PD
  ✅ YAML: Valid (forge/apps/DS1140_PD/DS1140_PD.yaml)
  ✅ Package: Generated (2025-11-03 14:30)
     - DS1140_PD_custom_inst_shim.vhd (8.0 KB)
     - DS1140_PD_custom_inst_main.vhd (6.9 KB)
  ✅ Validated: 8 datatypes, 3 registers
  ❌ Deployed: No

DS1180_LASER
  ⚠️  YAML: Not validated
  ✅ Package: Generated (2025-11-02 10:15)
  ❌ Deployed: No

DS1200_EM
  ⚠️  YAML: Stale (modified after generation)
  ⚠️  Package: Needs regeneration
  ❌ Deployed: No

DS1220_OPTICAL
  ❌ YAML: Missing (forge/apps/DS1220_OPTICAL/DS1220_OPTICAL.yaml not found)
  ❌ Package: Not generated
  ❌ Deployed: No

---
Total: 4 probes
Ready: 1 (DS1140_PD)
Need attention: 3
```

## Status Indicators

### YAML Status

**✅ Valid**
- YAML file exists
- Recently validated by forge-context
- No schema errors

**⚠️ Not validated**
- YAML file exists
- Not validated recently
- May have errors

**⚠️ Validation errors**
- YAML file exists but has errors
- Shows error count
- Need to fix and re-validate

**❌ Missing**
- No YAML file found in specs/
- Need to create specification

### Package Status

**✅ Generated**
- Package exists in forge/apps/<probe_name>/
- manifest.json and VHDL files present
- Up-to-date with YAML

**⚠️ Stale**
- Package exists but YAML modified after generation
- Need to regenerate package

**❌ Not generated**
- No package directory found
- Need to run `/generate`

### Deployment Status

**✅ Deployed**
- Device IP shown
- Slot number shown (if known)
- Last deployment timestamp

**❌ Not deployed**
- No active deployment found
- Need to run `/deploy`

## Checks Performed

1. **Scan forge/apps/ directory** for probe packages
2. **For each probe:**
   - Check `forge/apps/<probe_name>/<probe_name>.yaml` exists
   - Read YAML (if exists) and basic syntax check
   - Check generated VHDL files exist (*_shim.vhd, *_main.vhd)
   - Compare timestamps (YAML vs generated files)
   - Check deployment cache (if maintained)

## Use Cases

### Project Overview
Run at start of work session to see all probe states.

### Identify Stale Probes
Find probes where YAML changed but package not regenerated.

### Multi-Probe Development
Track status when working on multiple probes simultaneously.

### Onboarding
New team members can see all available probes.

## Next Actions by Status

### Probe with validation errors
```
/validate forge/apps/<probe_name>/<probe_name>.yaml
```
Fix errors, re-validate.

### Probe with stale package
```
/generate forge/apps/<probe_name>/<probe_name>.yaml --force
```

### Probe not deployed
```
/deploy <probe_name> --device <ip>
```

### Probe ready
No action needed, or monitor with:
```
/monitor-state <probe_name>
```

## Notes

- Deployment status requires deployment tracking (may be limited)
- YAML validation status cached from recent `/validate` calls
- Package staleness determined by file timestamps
- Use this before starting work to prioritize tasks

## Example Session

```
User: What probes need attention?

Agent: /probe-status

Output shows:
- DS1140_PD: All green, ready
- DS1180_LASER: Package stale, need regeneration
- DS1200_EM: Not deployed
- DS1220_OPTICAL: YAML errors

User: Fix DS1220_OPTICAL first

Agent: /validate forge/apps/DS1220_OPTICAL/DS1220_OPTICAL.yaml
[Shows errors]

User: [Fixes YAML]

Agent: /validate forge/apps/DS1220_OPTICAL/DS1220_OPTICAL.yaml
✅ Now valid

Agent: /probe-status
[Shows DS1220_OPTICAL now has valid YAML, ready to generate]
```
