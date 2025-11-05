# Validate Probe Structure

Check that probe package follows Option A structure.

**Agent:** probe-design-orchestrator

---

## Usage

```
/validate-probe-structure <probe_name>
```

**Example:**
```
/validate-probe-structure DS1140_PD
```

## What It Checks (Option A Architecture)

### Required Directory
- [ ] `forge/apps/<probe_name>/` exists

### Required Files
- [ ] `forge/apps/<probe_name>/<probe_name>.yaml` exists
- [ ] YAML is valid (parseable, correct schema)

### Generated Files (if package has been generated)
- [ ] `forge/apps/<probe_name>/<probe_name>_custom_inst_shim.vhd` exists
- [ ] `forge/apps/<probe_name>/<probe_name>_custom_inst_main.vhd` exists
- [ ] Generated files are newer than YAML (not stale)

### Optional Files (won't fail validation)
- `forge/apps/<probe_name>/README.md` - Documentation
- `forge/apps/<probe_name>/manifest.json` - Package metadata (future)

### Consistency Checks
- [ ] Package `app_name` in YAML matches directory name
- [ ] Platform specified is valid (moku_go/lab/pro/delta)
- [ ] All datatypes reference valid BasicAppDataTypes

## Example Output - Valid Structure

```
✅ Probe structure validation: PASSED

Probe: DS1140_PD
Location: forge/apps/DS1140_PD/

Required files:
  ✅ DS1140_PD.yaml - Found (65 lines)
  ✅ YAML valid - 8 datatypes, platform: moku_go

Generated files:
  ✅ DS1140_PD_custom_inst_shim.vhd - Found (8.0 KB, auto-generated)
  ✅ DS1140_PD_custom_inst_main.vhd - Found (6.9 KB, template)
  ✅ Files up-to-date (YAML not modified after generation)

Optional:
  ✅ README.md - Found

Consistency checks:
  ✅ app_name matches directory: DS1140_PD
  ✅ Platform valid: moku_go
  ✅ All 8 datatypes valid BasicAppDataTypes

No issues found.
```

## Example Output - Issues Found

```
❌ Probe structure validation: FAILED

Probe: DS1180_LASER
Location: forge/apps/DS1180_LASER/

Required directories:
  ✅ specs/ - Found
  ✅ vhdl/ - Found
  ❌ docs/ - MISSING

Required files:
  ✅ specs/DS1180_LASER.yaml - Found (189 lines)
  ❌ docs/README.md - MISSING

Optional:
  ⚠️  tests/ - Not found (optional)
  ⚠️  vhdl/*.vhd - No VHDL files found

Package consistency:
  ✅ forge/apps/DS1180_LASER/ - Found
  ⚠️  app_name mismatch: YAML says 'DS1180_Laser', expected 'DS1180_LASER'

---
Issues found: 3
Warnings: 3
```

## Fix Suggestions

### Missing directories
```bash
mkdir -p forge/apps/<probe_name>/docs
mkdir -p forge/apps/<probe_name>/tests
```

### Missing README
Use template from `/init-probe` command or create basic README:
```markdown
# <probe_name> Probe

[Description]

## Signals
[List signals from YAML]

## Usage
[Basic usage instructions]
```

### app_name mismatch
Edit YAML file to match directory name:
```yaml
app_name: DS1180_LASER  # Must match directory name exactly
```

### No VHDL files
This is expected before implementation. After package generation:
1. Review `forge/apps/<probe_name>/*_main.vhd` template
2. Create custom VHDL in `forge/apps/<probe_name>/vhdl/`

## When to Use

### Before Starting Work
Verify probe structure is correct before beginning development.

### After Manual Changes
If you created directories/files manually, verify structure.

### Before Package Generation
Ensure structure is correct before running `/generate`.

### Troubleshooting Build Issues
Structural issues can cause generation or deployment failures.

### Code Review
Verify probe follows standard structure before committing.

## Integration with Other Commands

**After `/init-probe`:**
```
/init-probe DS1220_OPTICAL
/validate-probe-structure DS1220_OPTICAL
✅ Should pass (template creates correct structure)
```

**Before `/generate`:**
```
/validate-probe-structure DS1180_LASER
[Fix any issues]
/validate forge/apps/DS1180_LASER/specs/DS1180_LASER.yaml
/generate forge/apps/DS1180_LASER/specs/DS1180_LASER.yaml
```

**Part of `/probe-status`:**
Structure validation is part of overall probe status check.

## Notes

- This validates STRUCTURE only, not YAML content (use `/validate` for that)
- Package consistency checks require package to exist (optional)
- Warnings don't fail validation, only errors do
- Use `/init-probe` to create correct structure from template

## Expected Directory Structure

```
forge/apps/<probe_name>/
├── specs/                          # Required
│   └── <probe_name>.yaml           # Required (exact name match)
├── vhdl/                           # Required (can be empty initially)
│   ├── <probe_name>_logic.vhd      # Custom VHDL (user creates)
│   └── <probe_name>_fsm.vhd        # Additional VHDL (optional)
├── docs/                           # Required
│   ├── README.md                   # Required
│   └── diagrams/                   # Optional
│       └── fsm.png
└── tests/                          # Optional
    └── <probe_name>_tb.vhd         # Test benches
```

## Validation Levels

### Level 1: Basic Structure (Required)
- Directories exist (specs/, vhdl/, docs/)
- Required files exist (YAML, README)

### Level 2: Consistency (Important)
- app_name matches directory name
- Package exists and matches
- No conflicting metadata

### Level 3: Completeness (Nice-to-have)
- VHDL files present
- Tests exist
- Comprehensive documentation

This command checks all three levels and reports issues/warnings accordingly.
