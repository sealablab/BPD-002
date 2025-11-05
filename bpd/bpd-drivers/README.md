# BPD Drivers

Probe-specific driver implementations for BPD framework.

## Overview

Each driver implements the `FIProbeInterface` from bpd-core for specific probe hardware.

## Available Drivers

### DS1120A (Riscure EMFI Probe)

```python
from bpd_drivers import DS1120ADriver
from moku_models import MOKU_GO_PLATFORM
from bpd_core import validate_probe_moku_compatibility

# Create driver
driver = DS1120ADriver()
driver.initialize()

# Validate compatibility with Moku
validate_probe_moku_compatibility(driver, MOKU_GO_PLATFORM)

# Configure and use
driver.set_voltage(3.3)
driver.set_pulse_width(100)
driver.arm()
driver.trigger()
```

## Adding New Drivers

1. Create new module in `src/bpd_drivers/`
2. Implement `FIProbeInterface` protocol
3. Use `@register_driver("name")` decorator
4. Add to `__init__.py` exports
