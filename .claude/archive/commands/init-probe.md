# Initialize Probe

Create standard probe directory structure with templates.

**Agent:** probe-design-orchestrator

---

## Usage

```
/init-probe <probe_name>
```

**Example:**
```
/init-probe DS1180_LASER
```

## What It Creates (Option A)

```
forge/apps/<probe_name>/
├── <probe_name>.yaml          # Template YAML specification
└── README.md                  # Template documentation
```

**Note:** VHDL files (*_shim.vhd, *_main.vhd) are generated after running `/generate`.

## Template YAML

**File:** `forge/apps/<probe_name>/<probe_name>.yaml`

```yaml
app_name: <probe_name>
version: 1.0.0
description: Probe description here
platform: moku_go  # Options: moku_go, moku_lab, moku_pro, moku_delta

datatypes:
  - name: signal_example
    datatype: voltage_output_05v_s16  # See type reference
    description: Example signal
    default_value: 0
    display_name: Example Signal
    units: V
    min_value: -32768
    max_value: 32767

  - name: timing_example
    datatype: time_milliseconds_u16
    description: Example timing parameter
    default_value: 100
    display_name: Timing
    units: ms

  - name: control_flag
    datatype: boolean_1
    description: Example control flag
    default_value: 0

mapping_strategy: type_clustering  # Options: first_fit, best_fit, type_clustering
```

## Template README

**File:** `forge/apps/<probe_name>/README.md`

```markdown
# <probe_name> Probe

## Description

[Describe probe purpose and functionality]

## Signals

### Control Signals

- `signal_example` - [Description]
- `timing_example` - [Description]
- `control_flag` - [Description]

### Outputs

- [List probe outputs]

## FSM States

[If using FSM, describe states]

- READY - [Description]
- ARMED - [Description]
- FIRING - [Description]
- COOLING - [Description]

## Safety Considerations

[Important safety notes for this probe]

## Usage

1. Deploy probe: `/deploy <probe_name> --device <ip>`
2. Set control registers via Python API or TUI
3. Monitor with `/monitor-state <probe_name>`

## Development Notes

[Internal notes for developers]
```

## Next Steps

After running `/init-probe`:

1. **Edit YAML spec** (`forge/apps/<probe_name>/<probe_name>.yaml`)
   - Update description
   - Add/modify datatypes
   - Choose platform
   - Set mapping_strategy

2. **Validate spec**
   ```
   /validate forge/apps/<probe_name>/<probe_name>.yaml
   ```

3. **Generate package**
   ```
   /generate forge/apps/<probe_name>/<probe_name>.yaml
   ```
   Or use full workflow:
   ```
   /workflow new-probe forge/apps/<probe_name>/<probe_name>.yaml
   ```

4. **Implement custom VHDL**
   - Edit `forge/apps/<probe_name>/<probe_name>_custom_inst_main.vhd`
   - Shim file (*_shim.vhd) is auto-generated, DO NOT EDIT

5. **Deploy and test**
   ```
   /deploy <probe_name> --device <ip>
   ```

## Type Reference

Common datatypes (see `forge/libs/basic-app-datatypes/llms.txt` for complete list):

**Voltage:**
- `voltage_output_05v_s16` - ±5V signed 16-bit
- `voltage_output_05v_u16` - 0-5V unsigned 16-bit
- `voltage_signed_s16` - Generic ±5V signed
- `voltage_millivolts_s16` - ±32767 mV signed

**Time:**
- `time_milliseconds_u16` - 0-65535 ms
- `time_microseconds_u16` - 0-65535 µs
- `time_cycles_u8` - 0-255 clock cycles
- `time_cycles_u16` - 0-65535 clock cycles

**Boolean:**
- `boolean_1` - 1-bit true/false

## Platform Reference

- `moku_go` - 125 MHz, 2 slots, development/small probes
- `moku_lab` - 500 MHz, 2 slots, lab instrumentation
- `moku_pro` - 1.25 GHz, 4 slots, high-performance
- `moku_delta` - 5 GHz, 3 slots, RF and high-speed

See `forge/libs/moku-models/llms.txt` for detailed specs.

## Notes

- Probe name should match directory name
- Use PascalCase or snake_case for probe names
- YAML field `app_name` must match probe name
- Edit templates after creation, don't use as-is
