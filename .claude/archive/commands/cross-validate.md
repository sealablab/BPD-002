# Cross-Validate Probe

Verify probe VHDL implementation is compatible with generated package.

**Agent:** probe-design-orchestrator

---

## Usage

```
/cross-validate <probe_name>
```

**Example:**
```
/cross-validate DS1140_PD
```

## What It Validates

### 1. Signal Name Matching
Check that signals used in custom VHDL exist in manifest.json.

### 2. Type Compatibility
Verify VHDL types match expected types from manifest.

### 3. Signal Usage
Confirm all required signals are used (not just declared).

### 4. No Direct CR References
Ensure custom VHDL uses friendly names, not Control Register direct access.

## Prerequisites

- Probe structure valid (`/validate-probe-structure`)
- Package generated (`forge/apps/<probe_name>/` exists)
- Custom VHDL implemented in `forge/apps/<probe_name>/<probe_name>_custom_inst_main.vhd`

## Example Output - Valid

```
✅ Cross-validation successful

Probe: DS1140_PD
Location: forge/apps/DS1140_PD/
VHDL: DS1140_PD_custom_inst_main.vhd

Signal verification:
  ✅ intensity (voltage_output_05v_s16)
     Found in: DS1140_PD_logic.vhd:42
     Type matches manifest

  ✅ arm_timeout (time_milliseconds_u16)
     Found in: DS1140_PD_logic.vhd:56
     Type matches manifest

  ✅ trigger_threshold (voltage_signed_s16)
     Found in: DS1140_PD_fsm.vhd:23
     Type matches manifest

  ✅ cooling_duration (time_cycles_u8)
     Found in: DS1140_PD_fsm.vhd:78
     Type matches manifest

  ✅ firing_duration (time_cycles_u8)
     Found in: DS1140_PD_fsm.vhd:82
     Type matches manifest

  ✅ arm_probe (boolean_1 → std_logic)
     Found in: DS1140_PD_fsm.vhd:45
     Type compatible

  ✅ force_fire (boolean_1 → std_logic)
     Found in: DS1140_PD_fsm.vhd:48
     Type compatible

  ✅ reset_fsm (boolean_1 → std_logic)
     Found in: DS1140_PD_fsm.vhd:51
     Type compatible

Best practices:
  ✅ No direct CR references found
  ✅ All signals from manifest are used
  ✅ No undeclared signals referenced

No issues found. Probe ready for compilation and deployment.
```

## Example Output - Issues Found

```
❌ Cross-validation failed

Probe: DS1180_LASER
Package: forge/apps/DS1180_LASER/
VHDL: forge/apps/DS1180_LASER/vhdl/

Signal verification:
  ✅ laser_intensity (voltage_output_05v_s16)
     Found in: DS1180_LASER_logic.vhd:32
     Type matches manifest

  ❌ trigger_mode (NOT FOUND)
     Referenced in: DS1180_LASER_logic.vhd:56
     NOT in manifest.json
     Fix: Add 'trigger_mode' to YAML spec or remove from VHDL

  ⚠️  pulse_duration (TYPE MISMATCH)
     Found in: DS1180_LASER_logic.vhd:67
     Expected type: time_cycles_u8
     Found in VHDL: std_logic_vector(15 downto 0)
     Fix: Change VHDL type to 'time_cycles_u8'

  ✅ enable_laser (boolean_1 → std_logic)
     Found in: DS1180_LASER_logic.vhd:89
     Type compatible

Best practices:
  ❌ Direct CR reference found!
     File: DS1180_LASER_logic.vhd:102
     Code: if Control6(15 downto 0) > threshold then
     Fix: Use friendly signal name instead: if laser_intensity > threshold then

  ⚠️  Unused signal: safety_threshold
     Declared in manifest.json
     Not found in any VHDL file
     Consider: Either use in VHDL or remove from YAML spec

---
Issues found: 3
Warnings: 2
```

## Validation Details

### Signal Name Matching

**Checks:**
- Every signal in custom VHDL exists in manifest.json
- Signal names match exactly (case-sensitive)

**Common issues:**
```
YAML:      arm_probe
VHDL:      ArmProbe        ❌ Case mismatch
Fix:       arm_probe       ✅

YAML:      intensity
VHDL:      output_intensity ❌ Name mismatch
Fix:       intensity        ✅
```

### Type Compatibility

**Checks:**
- VHDL types match manifest types
- Conversions are appropriate

**Allowed conversions:**
```yaml
# manifest.json
"vhdl_type": "voltage_output_05v_s16"
```

```vhdl
-- VHDL - Direct use (best)
signal intensity : voltage_output_05v_s16;  ✅

-- VHDL - With conversion (ok if needed)
signal intensity_raw : signed(15 downto 0);
intensity_raw <= signed(intensity);         ⚠️  (conversion needed?)

-- VHDL - Wrong type
signal intensity : std_logic_vector(15 downto 0);  ❌
```

**Boolean special case:**
```yaml
# manifest.json
"vhdl_type": "boolean_1"
```

```vhdl
-- VHDL - Both acceptable
signal arm_probe : std_logic;               ✅ (common)
signal arm_probe : boolean;                 ✅ (explicit)
```

### No Direct CR References

**Bad pattern (don't do this):**
```vhdl
-- Direct Control Register access
if Control6(15 downto 0) > threshold then   ❌
    output <= high_value;
end if;
```

**Good pattern (use friendly names):**
```vhdl
-- Use signal names from manifest
if intensity > threshold then               ✅
    output <= high_value;
end if;
```

**Why this matters:**
- Shim layer handles CR extraction
- Custom VHDL should be CR-agnostic
- Easier to maintain and understand
- Portable across register mapping changes

### Unused Signals

**Warning (not error):**
Signal in manifest but not used in VHDL.

**Possible reasons:**
1. Signal defined but implementation incomplete
2. Signal planned but not yet used
3. Signal no longer needed (remove from YAML)

**Action:** Review and either use signal or remove from spec.

## Fix Workflow

### Issue: Signal not in manifest

**Problem:**
```
❌ trigger_mode (NOT FOUND)
   Referenced in: DS1180_LASER_logic.vhd:56
   NOT in manifest.json
```

**Fix Option 1 - Add to YAML:**
```yaml
datatypes:
  - name: trigger_mode
    datatype: boolean_1  # or appropriate type
    description: Trigger mode selection
    default_value: 0
```

Then regenerate package:
```
/generate forge/apps/DS1180_LASER/specs/DS1180_LASER.yaml --force
```

**Fix Option 2 - Remove from VHDL:**
Remove references to `trigger_mode` in VHDL files.

---

### Issue: Type mismatch

**Problem:**
```
⚠️  pulse_duration (TYPE MISMATCH)
   Expected: time_cycles_u8
   Found: std_logic_vector(15 downto 0)
```

**Fix - Use correct VHDL type:**
```vhdl
-- Before
signal pulse_duration : std_logic_vector(15 downto 0);  ❌

-- After
signal pulse_duration : time_cycles_u8;                 ✅
```

---

### Issue: Direct CR reference

**Problem:**
```
❌ Direct CR reference found!
   Code: if Control6(15 downto 0) > threshold then
```

**Fix - Use friendly name:**
```vhdl
-- Before
if Control6(15 downto 0) > threshold then    ❌

-- After (look up signal name in manifest.json)
if intensity > threshold then                ✅
```

Check manifest.json to find which signal maps to CR6[15:0].

---

### Issue: Unused signal

**Problem:**
```
⚠️  Unused signal: safety_threshold
   Declared in manifest.json
   Not found in any VHDL file
```

**Fix Option 1 - Use in VHDL:**
```vhdl
-- Add usage
if intensity > safety_threshold then
    intensity_clamped <= safety_threshold;
else
    intensity_clamped <= intensity;
end if;
```

**Fix Option 2 - Remove from YAML:**
If signal is no longer needed, remove from YAML spec and regenerate.

## When to Use

### Before Deployment
Always cross-validate before deploying to ensure VHDL matches package.

### After VHDL Changes
Verify changes didn't break compatibility.

### After YAML Regeneration
Confirm VHDL still compatible after package regeneration.

### Debugging Deployment Issues
If deployment fails, cross-validation may reveal mismatches.

## Integration with Workflow

**Complete workflow:**
```
1. /init-probe DS1220_OPTICAL
2. [Edit YAML spec]
3. /validate forge/apps/DS1220_OPTICAL/specs/DS1220_OPTICAL.yaml
4. /generate forge/apps/DS1220_OPTICAL/specs/DS1220_OPTICAL.yaml
5. [Write custom VHDL in forge/apps/DS1220_OPTICAL/vhdl/]
6. /cross-validate DS1220_OPTICAL  ← YOU ARE HERE
7. [Fix any issues]
8. /cross-validate DS1220_OPTICAL  (repeat until clean)
9. [Compile bitstream]
10. /deploy DS1220_OPTICAL --device 192.168.1.100
```

## Technical Details

### Files Analyzed

**manifest.json:**
```json
{
  "datatypes": [
    {
      "name": "intensity",
      "datatype": "voltage_output_05v_s16",
      ...
    }
  ],
  "register_mappings": [
    {
      "signal_name": "intensity",
      "cr_number": 6,
      "bit_slice": "15:0",
      "vhdl_type": "voltage_output_05v_s16"
    }
  ]
}
```

**Custom VHDL:**
All `.vhd` files in `forge/apps/<probe_name>/vhdl/` are scanned for:
- Signal declarations
- Signal usage
- Type definitions
- Control Register references (antipattern check)

### Validation Algorithm

1. Parse manifest.json → extract expected signals and types
2. Parse all VHDL files → extract declared/used signals
3. Match signals (name and type)
4. Check for CR references (regex search for `Control[0-9]+`)
5. Report mismatches, missing signals, type errors

## Notes

- This validates VHDL ↔ package compatibility only
- Does not validate VHDL syntax (use GHDL or synthesis tools)
- Does not validate VHDL logic correctness (use simulation)
- Focus is on interface compatibility with generated package
- Clean cross-validation required before deployment

## Success Criteria

Cross-validation passes when:
- [ ] All VHDL signals exist in manifest
- [ ] All types match or are compatible
- [ ] No direct CR references
- [ ] All manifest signals used (optional, warning only)

**When all green:** Probe VHDL is compatible with package, ready for compilation and deployment.
