# Probe Development Workflow

**Version:** 1.0
**Purpose:** End-to-end guide for probe development in this monorepo
**Audience:** AI agents coordinating probe development

---

## Overview

This document provides step-by-step workflows for probe development, from initial specification to deployed hardware. Use this when guiding users through probe creation, iteration, or debugging.

---

## Workflow 1: New Probe Development (Complete Pipeline)

### Prerequisites
- Git submodules synced (`/sync-submodules`)
- Basic understanding of probe requirements

### Step 1: Create Probe Directory in forge/apps/

**Command:** `mkdir -p forge/apps/<probe_name>`

**Creates:**
```
forge/apps/<probe_name>/
└── (ready for YAML specification)
```

---

### Step 2: Write YAML Specification

**User creates:** `forge/apps/<probe_name>/<probe_name>.yaml`

**Template structure:**
```yaml
app_name: <probe_name>
version: 1.0.0
description: Probe description here
platform: moku_go  # or moku_lab, moku_pro, moku_delta

datatypes:
  - name: signal_name_1
    datatype: voltage_output_05v_s16  # See type reference
    description: Signal description
    default_value: 0
    display_name: Signal 1
    units: V
    min_value: -32768
    max_value: 32767

  - name: signal_name_2
    datatype: time_milliseconds_u16
    description: Timing parameter
    default_value: 100
    display_name: Signal 2
    units: ms

  - name: control_flag
    datatype: boolean_1
    description: Control flag
    default_value: 0

mapping_strategy: type_clustering  # Recommended
```

**Type Reference:**
- See `forge/libs/basic-app-datatypes/llms.txt` for complete type list
- Common types:
  - Voltage: `voltage_output_05v_s16` (±5V), `voltage_signed_s16`
  - Time: `time_milliseconds_u16`, `time_cycles_u8`
  - Boolean: `boolean_1`

**Platform Reference:**
- See `forge/libs/moku-models/llms.txt` for platform specs
- Platforms: `moku_go` (125 MHz), `moku_lab` (500 MHz), `moku_pro` (1.25 GHz), `moku_delta` (5 GHz)

---

### Step 3: Validate YAML Specification

**Delegate to:** forge-context

**Command:** `/validate forge/apps/<probe_name>/<probe_name>.yaml`

**What it checks:**
- YAML syntax valid
- Required fields present (app_name, platform, datatypes)
- Datatypes exist in BasicAppDataTypes enum
- Default values within type ranges
- Signal names valid (snake_case, no VHDL keywords)

**Expected output:**
```
✅ Validation successful
- app_name: <probe_name>
- platform: moku_go
- datatypes: 3 signals defined
- No errors found
```

**If errors:**
```
❌ Validation failed

Error 1 (line 8): Unknown datatype 'voltage_10v_s16'
  Fix: Use 'voltage_output_05v_s16' or check type reference

Error 2 (line 12): default_value 40000 out of range for voltage_output_05v_s16 (max: 32767)
  Fix: Reduce default_value to 32767 or use larger type
```

**User Action:** Fix errors, re-validate until clean

---

### Step 4: Generate Package

**Delegate to:** forge-context or forge-pipe-fitter

**Option A - Just generate:**
```
/generate forge/apps/<probe_name>/<probe_name>.yaml
```

**Option B - Full pipeline (recommended):**
```
/workflow new-probe forge/apps/<probe_name>/<probe_name>.yaml
```

**What it generates:**
```
forge/apps/<probe_name>/
├── <probe_name>_custom_inst_shim.vhd     # Auto-generated register mapping
├── <probe_name>_custom_inst_main.vhd     # Template for custom logic
├── manifest.json                          # Package metadata
├── control_registers.json                 # Initial CR values
└── <probe_name>.yaml                      # Copy of spec
```

**Expected output:**
```
✅ Package generated successfully

Package: <probe_name> v1.0.0
Platform: moku_go
Signals: 3 datatypes defined
Register efficiency: 67/96 bits used (69.8%)
Strategy: type_clustering

Generated files:
- forge/apps/<probe_name>/<probe_name>_custom_inst_shim.vhd
- forge/apps/<probe_name>/<probe_name>_custom_inst_main.vhd
- forge/apps/<probe_name>/manifest.json
- forge/apps/<probe_name>/control_registers.json
```

**What to inspect:**
1. **manifest.json** - Verify signals, register mappings
2. **control_registers.json** - Check default values (CR6-CR15)
3. **shim.vhd** - Auto-generated, DO NOT EDIT
4. **main.vhd** - Template, shows signal interfaces

---

### Step 5: Understand Register Mapping

**Inspect:** `forge/apps/<probe_name>/manifest.json`

**Key section - register_mappings:**
```json
{
  "register_mappings": [
    {
      "signal_name": "signal_name_1",
      "cr_number": 6,
      "bit_slice": "15:0",
      "vhdl_type": "voltage_output_05v_s16"
    },
    {
      "signal_name": "signal_name_2",
      "cr_number": 6,
      "bit_slice": "31:16",
      "vhdl_type": "time_milliseconds_u16"
    },
    {
      "signal_name": "control_flag",
      "cr_number": 7,
      "bit_slice": "31:31",
      "vhdl_type": "boolean_1"
    }
  ]
}
```

**What this means:**
- `signal_name_1` → CR6[15:0] (16 bits)
- `signal_name_2` → CR6[31:16] (16 bits)
- `control_flag` → CR7[31] (1 bit)

**Shim layer handles extraction:**
```vhdl
-- In *_shim.vhd (auto-generated)
signal signal_name_1 : voltage_output_05v_s16;
signal signal_name_2 : time_milliseconds_u16;
signal control_flag : std_logic;

-- Bit extraction from Control Registers
signal_name_1 <= voltage_output_05v_s16(unsigned(Control6(15 downto 0)));
signal_name_2 <= time_milliseconds_u16(unsigned(Control6(31 downto 16)));
control_flag <= Control7(31);
```

**User works with friendly names, no CR knowledge needed in custom VHDL!**

---

### Step 6: Implement Custom VHDL Logic

**User edits:** `forge/apps/<probe_name>/<probe_name>_custom_inst_main.vhd`

**Template generated in Step 4** - shows signal interfaces and structure

**Key principles:**

1. **Use friendly signal names** (from manifest.json)
   ```vhdl
   -- Good
   if signal_name_1 > threshold then
       output <= high_value;
   end if;

   -- Bad (don't reference CRs directly)
   if Control6(15 downto 0) > threshold then
       output <= high_value;
   end if;
   ```

2. **Use VHDL types from manifest** (shim handles conversion)
   ```vhdl
   signal my_voltage : voltage_output_05v_s16;  -- From manifest
   signal my_time : time_milliseconds_u16;       -- From manifest
   ```

3. **Implement FSM if needed**
   ```vhdl
   type state_type is (READY, ARMED, FIRING, COOLING);
   signal current_state : state_type := READY;

   process(clk)
   begin
       if rising_edge(clk) then
           case current_state is
               when READY =>
                   if arm_probe = '1' then
                       current_state <= ARMED;
                   end if;
               when ARMED =>
                   if trigger_detected = '1' then
                       current_state <= FIRING;
                   end if;
               -- etc.
           end case;
       end if;
   end process;
   ```

4. **Drive outputs**
   ```vhdl
   output_a <= intensity when current_state = FIRING else (others => '0');
   fsm_state_debug <= state_to_vector(current_state);
   ```

**Common patterns:**
- FSM control (READY → ARMED → FIRING → COOLING)
- Pulse generation (duration controlled by timing signals)
- Threshold detection (voltage comparisons)
- Safety clamping (limit outputs to safe ranges)

---

### Step 7: Cross-Validate Implementation

**Command:** `/cross-validate <probe_name>`

**What it checks:**
1. Signal names in VHDL match manifest.json
2. VHDL types compatible with manifest types
3. Required signals used
4. No CR direct references (should use friendly names)

**Expected output:**
```
✅ Cross-validation successful

Signals verified:
- signal_name_1: Found, type matches (voltage_output_05v_s16)
- signal_name_2: Found, type matches (time_milliseconds_u16)
- control_flag: Found, type matches (boolean_1)

No issues found.
```

**If errors:**
```
❌ Cross-validation failed

Issue 1: Signal 'threshold' not found in manifest.json
  Fix: Add 'threshold' to YAML spec and regenerate package

Issue 2: Signal 'intensity' has type mismatch
  Expected: voltage_output_05v_s16
  Found: std_logic_vector(15 downto 0)
  Fix: Use voltage_output_05v_s16 type directly

Issue 3: Direct CR reference found: Control6(15 downto 0)
  Fix: Use friendly signal name instead
```

**User Action:** Fix issues, re-validate until clean

---

### Step 8: Compile Bitstream (External Step)

**Note:** Bitstream compilation is typically done outside this monorepo

**Required:**
- VHDL files from forge/apps/<probe_name>/
- Custom VHDL from forge/apps/<probe_name>/
- Moku build toolchain

**Output:**
- `<probe_name>.tar.gz` (bitstream package)

**Placement:**
- Copy to `forge/apps/<probe_name>/<probe_name>.tar.gz`

**Not covered by this workflow** - Assumes external build process

---

### Step 9: Discover Moku Devices

**Delegate to:** deployment-context

**Command:** `/discover`

**Expected output:**
```
Discovered Moku devices:
========================

1. Moku:Go (MG12345)
   IP: 192.168.1.100
   Platform: moku_go
   Status: Available

2. Moku:Lab (ML67890)
   IP: 192.168.1.101
   Platform: moku_lab
   Status: In use
```

**User Action:** Select device, note IP address

---

### Step 10: Deploy to Hardware

**Delegate to:** deployment-context

**Command:** `/deploy <probe_name> --device <ip>`

**Example:**
```
/deploy <probe_name> --device 192.168.1.100
```

**What it does:**
1. Verify package exists (manifest.json, control_registers.json)
2. Connect to Moku device
3. Deploy CloudCompile instrument (with bitstream)
4. Deploy Oscilloscope (for monitoring)
5. Set control registers (from control_registers.json)
6. Configure routing (input → custom instrument → output)

**Expected output:**
```
✅ Deployment successful

Package: <probe_name> v1.0.0
Device: 192.168.1.100 (Moku:Go)
Slot: 2 (CloudCompile)
Control registers: 3 configured (CR6-CR7)
Routing: 3 connections configured

Deployment complete! Device ready for operation.
```

**If errors:**
```
❌ Deployment failed

Error: Bitstream not found at forge/apps/<probe_name>/<probe_name>.tar.gz
  Fix: Compile bitstream and place in package directory

Error: Platform mismatch (spec: moku_go, device: moku_lab)
  Fix: Deploy to correct platform or regenerate for moku_lab

Error: Device not reachable at 192.168.1.100
  Fix: Check network connection, verify IP with /discover
```

---

### Step 11: Monitor and Verify

**Delegate to:** hardware-debug-context

**Command:** `/monitor-state <probe_name>`

**What it does:**
1. Connect to deployed device
2. Read oscilloscope data
3. Monitor FSM state (if exposed via debug signals)
4. Display real-time values

**Expected output:**
```
Monitoring <probe_name> on 192.168.1.100...

FSM State: READY
Outputs:
- output_a: 0.00V
- output_b: 0.00V

Control Signals:
- signal_name_1: 0.00V (default)
- signal_name_2: 100ms (default)
- control_flag: 0 (default)

Press Ctrl+C to stop monitoring...
```

**User Action:** Verify expected behavior, adjust control registers if needed

---

### Step 12: Iterate (if needed)

**Quick iteration workflow:**

1. **Tweak YAML** (adjust defaults, add signals)
2. **Regenerate:** `/workflow iterate forge/apps/<probe_name>/<probe_name>.yaml --deploy`
3. **Verify:** `/monitor-state <probe_name>`

**Custom VHDL changes:**
1. Edit `forge/apps/<probe_name>/*.vhd`
2. Cross-validate: `/cross-validate <probe_name>`
3. Recompile bitstream (external)
4. Redeploy: `/deploy <probe_name> --device <ip> --force`

---

## Workflow 2: Iterative Development (Fast Cycles)

### Use Case
Quick YAML tweaks during development, skip validation for speed

### Prerequisites
- Package already generated once
- Device known from previous deployment

### Steps

1. **Edit YAML** (adjust defaults, mapping strategy)
2. **Regenerate + redeploy:**
   ```
   /workflow iterate forge/apps/<probe_name>/<probe_name>.yaml --deploy
   ```
3. **Verify:** `/monitor-state <probe_name>`

**What it skips:**
- Validation (assumes YAML valid)
- Device discovery (uses cached device)
- Documentation generation

**Speed:** ~30s vs ~2min for full workflow

---

## Workflow 3: Debugging Probe Behavior

### Use Case
Probe deployed but not behaving as expected

### Steps

1. **Check FSM state:**
   ```
   /debug-fsm <probe_name>
   ```
   Expected: State trace, transition log

2. **Trace signals:**
   ```
   /trace-signals <probe_name>
   ```
   Expected: Real-time signal values from oscilloscope

3. **Analyze timing:**
   ```
   /analyze-timing <probe_name>
   ```
   Expected: Timing analysis, clock checks

4. **Check control registers:**
   - Read current values
   - Compare with control_registers.json defaults
   - Verify user hasn't changed values

5. **Review VHDL logic:**
   - Load `forge/apps/<probe_name>/*.vhd`
   - Check FSM transitions
   - Verify output logic

6. **Redeploy with fresh config:**
   ```
   /deploy <probe_name> --device <ip> --force
   ```

---

## Workflow 4: Multi-Probe Management

### Use Case
Working on multiple probes simultaneously

### Steps

1. **Check status:**
   ```
   /probe-status
   ```
   Expected: Dashboard of all probes

2. **For each probe:**
   - Validate structure: `/validate-probe-structure <probe_name>`
   - Check YAML validity: Inspect status output
   - Verify package status: Check timestamps

3. **Prioritize work:**
   - Probes with ❌ need attention
   - Probes with ⚠️ need validation
   - Probes with ✅ are ready

---

## Common Patterns

### Pattern 1: FSM-Based Probe

**Use case:** State machine control (READY → ARMED → FIRING → COOLING)

**YAML signals:**
```yaml
datatypes:
  - name: arm_probe
    datatype: boolean_1
    description: Arm the probe (one-shot)
    default_value: 0

  - name: force_fire
    datatype: boolean_1
    description: Force immediate firing
    default_value: 0

  - name: reset_fsm
    datatype: boolean_1
    description: Reset FSM to READY
    default_value: 0

  - name: firing_duration
    datatype: time_cycles_u8
    description: Duration to stay in FIRING state
    default_value: 32
```

**VHDL FSM:**
```vhdl
type state_type is (READY, ARMED, FIRING, COOLING);
signal current_state : state_type := READY;

process(clk)
begin
    if rising_edge(clk) then
        if reset_fsm = '1' then
            current_state <= READY;
        else
            case current_state is
                when READY =>
                    if arm_probe = '1' or force_fire = '1' then
                        current_state <= FIRING;
                    end if;
                when FIRING =>
                    if cycle_count >= firing_duration then
                        current_state <= COOLING;
                    end if;
                when COOLING =>
                    if cool_down_complete then
                        current_state <= READY;
                    end if;
            end case;
        end if;
    end if;
end process;
```

---

### Pattern 2: Voltage Clamping

**Use case:** Limit output voltage to safe range

**YAML signals:**
```yaml
datatypes:
  - name: intensity
    datatype: voltage_output_05v_s16
    description: Desired output intensity
    default_value: 2400  # ~0.37V

  - name: max_voltage
    datatype: voltage_output_05v_s16
    description: Safety limit
    default_value: 19600  # ~3.0V (clamped from 5V max)
```

**VHDL clamping:**
```vhdl
signal clamped_intensity : voltage_output_05v_s16;

process(intensity, max_voltage)
begin
    if intensity > max_voltage then
        clamped_intensity <= max_voltage;
    else
        clamped_intensity <= intensity;
    end if;
end process;

output_a <= clamped_intensity;
```

---

### Pattern 3: Timing Control

**Use case:** Pulse generation with configurable duration

**YAML signals:**
```yaml
datatypes:
  - name: pulse_duration
    datatype: time_cycles_u8
    description: Pulse width in clock cycles
    default_value: 64

  - name: trigger
    datatype: boolean_1
    description: Trigger pulse generation
    default_value: 0
```

**VHDL pulse generation:**
```vhdl
signal counter : unsigned(7 downto 0) := (others => '0');
signal pulse_active : std_logic := '0';

process(clk)
begin
    if rising_edge(clk) then
        if trigger = '1' and pulse_active = '0' then
            pulse_active <= '1';
            counter <= (others => '0');
        elsif pulse_active = '1' then
            if counter < pulse_duration then
                counter <= counter + 1;
            else
                pulse_active <= '0';
            end if;
        end if;
    end if;
end process;

output <= pulse_active;
```

---

## Troubleshooting Guide

### Issue: YAML Validation Fails

**Symptoms:**
- Unknown datatype errors
- Default value out of range
- Invalid signal names

**Solutions:**
1. Check type reference: `forge/libs/basic-app-datatypes/llms.txt`
2. Verify default values within type range (see type metadata)
3. Use snake_case for signal names, avoid VHDL keywords

---

### Issue: Package Generation Fails

**Symptoms:**
- Template errors
- Mapping failures
- Missing files

**Solutions:**
1. Run validation first: `/validate <yaml_file>`
2. Check YAML syntax (indentation, quotes)
3. Verify all required fields present

---

### Issue: Cross-Validation Fails

**Symptoms:**
- Signal names don't match
- Type mismatches
- Direct CR references found

**Solutions:**
1. Update VHDL signal names to match manifest.json exactly
2. Use VHDL types from manifest (voltage_output_05v_s16, not std_logic_vector)
3. Replace CR references with friendly signal names

---

### Issue: Deployment Fails

**Symptoms:**
- Device not found
- Platform mismatch
- Bitstream missing

**Solutions:**
1. Run `/discover` to find devices
2. Check platform in YAML matches device
3. Verify bitstream compiled and placed in forge/apps/<probe_name>/

---

### Issue: FSM Stuck in Wrong State

**Symptoms:**
- FSM not transitioning
- Outputs not changing
- Unexpected behavior

**Solutions:**
1. Use `/debug-fsm <probe_name>` to see state trace
2. Check transition conditions in VHDL
3. Verify control signals are set correctly (use /monitor-state)
4. Add reset: Set `reset_fsm` signal to force READY state

---

## Success Criteria

Before considering probe complete:

- [ ] Probe structure validated
- [ ] YAML validated by forge-context
- [ ] Package generated successfully
- [ ] Custom VHDL cross-validated
- [ ] Bitstream compiled
- [ ] Deployed to hardware
- [ ] FSM behavior verified
- [ ] Outputs correct
- [ ] Documentation generated (optional)

---

## Next Steps After Deployment

### Production Deployment
1. Generate documentation: `/workflow document <probe_name>`
2. Create Python API: `/gen-python-api <probe_name>`
3. Test with actual hardware (external)
4. Create user guide (external)

### Iteration
1. Monitor real-world usage
2. Identify improvements
3. Update YAML spec
4. Iterate using `/workflow iterate`

---

**Last Updated:** 2025-11-03
**Maintained By:** moku-instrument-forge team
