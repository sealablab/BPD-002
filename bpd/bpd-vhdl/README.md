# BPD VHDL

Vendor-agnostic VHDL components for FI probe control.

## Overview

Provides reusable VHDL interfaces for fault injection probe control on Moku FPGA.

## Components

### fi_probe_interface.vhd

Standard interface for FI probe control:
- Configurable pulse width (generic PULSE_WIDTH_BITS)
- Configurable voltage control (generic VOLTAGE_BITS)
- Arm/trigger control
- Status feedback (ready, busy, fault)

Inspired by Riscure DS1120A interface but vendor-agnostic.

## Testing

Uses CocoTB for VHDL verification:

```bash
cd tests/
pytest test_fi_interface.py
```

## Integration

```vhdl
library work;
use work.fi_probe_interface;

-- Instantiate in your design
probe_ctrl : entity work.fi_probe_interface
    generic map (
        PULSE_WIDTH_BITS => 16,
        VOLTAGE_BITS => 16
    )
    port map (
        clk => clk,
        rst_n => rst_n,
        trigger_in => trigger,
        arm => arm_signal,
        -- ... other signals
    );
```
