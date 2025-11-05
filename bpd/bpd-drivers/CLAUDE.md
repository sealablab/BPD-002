# CLAUDE.md - BPD Drivers

## Project Overview

**bpd-drivers** contains probe-specific driver implementations for the BPD framework. Each driver implements the `FIProbeInterface` protocol from bpd-core and provides hardware-specific control logic for different FI probe types.

**Purpose:** Translate generic probe operations (arm, trigger, set_voltage) into hardware-specific commands for:
- EMFI probes (DS1120A, DS1140A)
- Laser FI probes (planned)
- RF injection probes (planned)
- Voltage glitching probes (planned)

**Part of:** BPD-002 (Basic Probe Driver) - Multi-vendor probe integration for Moku

**Design Philosophy:** One driver per probe model, all implementing same interface for easy swapping.

---

## Quick Start

```python
from bpd_drivers import DS1120ADriver
from bpd_core import validate_probe_moku_compatibility
from moku_models import MOKU_GO_PLATFORM

# Initialize DS1120A driver
driver = DS1120ADriver()
driver.initialize()

# Validate compatibility
validate_probe_moku_compatibility(driver, MOKU_GO_PLATFORM)

# Use probe
driver.set_voltage(3.3)
driver.set_pulse_width(50)  # Fixed at 50ns for DS1120A
driver.arm()
driver.trigger()
driver.disarm()
```

---

## Available Drivers

### DS1120A - Riscure EMFI Probe (Reference Implementation)

**Hardware:** High-power unidirectional electromagnetic fault injection

**Specifications:**
- Pulse width: 50ns (fixed, hardware limitation)
- Voltage: 0-3.3V TTL trigger input
- Power: 24-450V external PSU required
- Probe tips: Interchangeable 1.5mm/4mm variants
- Max current: 64A (coil)

**Electrical specs:** From `riscure-models.DS1120A_PLATFORM`

**Implementation highlights:**

```python
from bpd_core import FIProbeInterface, ProbeCapabilities, register_driver, ProbeStatus
from riscure_models import DS1120A_PLATFORM

@register_driver("ds1120a")
class DS1120ADriver:
    """Driver for Riscure DS1120A EMFI probe."""

    def __init__(self):
        self._probe_spec = DS1120A_PLATFORM
        self._armed = False
        self._voltage = 0.0
        self._hw_connected = False

    @property
    def capabilities(self) -> ProbeCapabilities:
        """Capabilities from riscure-models specs."""
        return ProbeCapabilities(
            min_voltage_v=0.0,
            max_voltage_v=3.3,
            min_pulse_width_ns=50,
            max_pulse_width_ns=50,  # Fixed for DS1120A
            pulse_width_resolution_ns=1,
            supports_external_trigger=True,
            supports_internal_trigger=False,
        )

    def initialize(self) -> None:
        """Initialize connection (or simulation mode)."""
        try:
            # Attempt hardware connection
            self._connect_to_probe()
            self._hw_connected = True
        except HardwareError:
            # Graceful degradation: simulation
            self._hw_connected = False
            print("[SIM] DS1120A in simulation mode")

    def set_voltage(self, voltage_v: float) -> None:
        """Set trigger threshold voltage."""
        if not (0.0 <= voltage_v <= 3.3):
            raise ValueError(f"Voltage {voltage_v}V out of range [0, 3.3]")
        self._voltage = voltage_v
        if self._hw_connected:
            self._hw_set_voltage(voltage_v)

    def set_pulse_width(self, width_ns: int) -> None:
        """Pulse width is fixed at 50ns for DS1120A."""
        if width_ns != 50:
            raise ValueError("DS1120A pulse width is fixed at 50ns (hardware)")
        # No-op: hardware always uses 50ns

    def arm(self) -> None:
        """Arm probe for trigger."""
        self._armed = True
        if self._hw_connected:
            self._hw_arm()

    def trigger(self) -> None:
        """Fire EMFI pulse."""
        if not self._armed:
            raise RuntimeError("DS1120A not armed")
        if self._hw_connected:
            self._hw_trigger()
        else:
            print(f"[SIM] DS1120A pulse: {self._voltage}V, 50ns")

    def disarm(self) -> None:
        """Disarm probe (safe state)."""
        self._armed = False
        if self._hw_connected:
            self._hw_disarm()

    def get_status(self) -> ProbeStatus:
        """Query probe state."""
        return ProbeStatus(
            ready=not self._armed,
            busy=False,
            armed=self._armed,
            fault=False,
        )

    def shutdown(self) -> None:
        """Safe shutdown."""
        self.disarm()
        if self._hw_connected:
            self._hw_disconnect()
```

**Key design decisions:**
- Uses `riscure-models` for electrical specs (single source of truth)
- Validates pulse width is 50ns (hardware constraint)
- Graceful degradation to simulation if hardware unavailable
- Auto-registers with `@register_driver("ds1120a")`

---

## Driver Development Guide

### Step-by-Step: Adding New Probe

**Example:** Adding laser FI probe support

#### 1. Create Driver Module

```python
# src/bpd_drivers/laser_fi.py

from bpd_core import FIProbeInterface, ProbeCapabilities, register_driver, ProbeStatus

@register_driver("laser_fi")
class LaserFIDriver:
    """Driver for laser fault injection probe."""

    def __init__(self):
        self._armed = False
        self._voltage = 0.0  # Laser power analog
        self._pulse_width = 0
        self._hw_connected = False

    @property
    def capabilities(self) -> ProbeCapabilities:
        """Laser probe capabilities."""
        return ProbeCapabilities(
            min_voltage_v=0.0,
            max_voltage_v=5.0,  # Laser power control
            min_pulse_width_ns=1,
            max_pulse_width_ns=1000,
            pulse_width_resolution_ns=1,
            supports_external_trigger=True,
            supports_internal_trigger=True,
        )

    def initialize(self) -> None:
        """Initialize laser hardware connection."""
        try:
            # Laser-specific initialization
            self._connect_laser()
            self._hw_connected = True
        except Exception:
            self._hw_connected = False
            print("[SIM] Laser in simulation mode")

    def set_voltage(self, voltage_v: float) -> None:
        """Set laser power (voltage analog)."""
        if not (0.0 <= voltage_v <= 5.0):
            raise ValueError(f"Laser power {voltage_v}V out of range")
        self._voltage = voltage_v
        if self._hw_connected:
            self._set_laser_power(voltage_v)

    def set_pulse_width(self, width_ns: int) -> None:
        """Set laser pulse duration."""
        if not (1 <= width_ns <= 1000):
            raise ValueError(f"Pulse width {width_ns}ns out of range")
        self._pulse_width = width_ns
        if self._hw_connected:
            self._set_laser_pulse_width(width_ns)

    def arm(self) -> None:
        """Arm laser for trigger."""
        self._armed = True
        if self._hw_connected:
            self._arm_laser()

    def trigger(self) -> None:
        """Fire laser pulse."""
        if not self._armed:
            raise RuntimeError("Laser not armed")
        if self._hw_connected:
            self._fire_laser()
        else:
            print(f"[SIM] Laser pulse: {self._voltage}V, {self._pulse_width}ns")

    def disarm(self) -> None:
        """Disarm laser (safe)."""
        self._armed = False
        if self._hw_connected:
            self._disarm_laser()

    def get_status(self) -> ProbeStatus:
        """Query laser state."""
        return ProbeStatus(
            ready=not self._armed,
            busy=False,
            armed=self._armed,
            fault=False,
        )

    def shutdown(self) -> None:
        """Safe shutdown."""
        self.disarm()
        if self._hw_connected:
            self._disconnect_laser()

    # Hardware-specific methods (private)
    def _connect_laser(self) -> None:
        # Laser connection logic
        pass

    def _set_laser_power(self, power_v: float) -> None:
        # Laser power control
        pass

    def _set_laser_pulse_width(self, width_ns: int) -> None:
        # Laser timing control
        pass

    def _arm_laser(self) -> None:
        # Laser arming
        pass

    def _fire_laser(self) -> None:
        # Laser trigger
        pass

    def _disarm_laser(self) -> None:
        # Laser safe state
        pass

    def _disconnect_laser(self) -> None:
        # Laser shutdown
        pass
```

#### 2. Add to Package Exports

```python
# src/bpd_drivers/__init__.py

from bpd_drivers.ds1120a import DS1120ADriver
from bpd_drivers.laser_fi import LaserFIDriver  # Add import

__all__ = [
    "DS1120ADriver",
    "LaserFIDriver",  # Add to exports
]
```

#### 3. Create Tests

```python
# tests/test_laser_fi.py

import pytest
from bpd_drivers import LaserFIDriver

def test_laser_capabilities():
    driver = LaserFIDriver()
    caps = driver.capabilities

    assert caps.min_voltage_v == 0.0
    assert caps.max_voltage_v == 5.0
    assert caps.min_pulse_width_ns == 1
    assert caps.max_pulse_width_ns == 1000

def test_laser_voltage_validation():
    driver = LaserFIDriver()
    driver.initialize()

    # Valid
    driver.set_voltage(2.5)

    # Invalid
    with pytest.raises(ValueError):
        driver.set_voltage(6.0)  # Exceeds max

def test_laser_arm_trigger():
    driver = LaserFIDriver()
    driver.initialize()

    # Cannot trigger before arm
    with pytest.raises(RuntimeError):
        driver.trigger()

    # Arm then trigger
    driver.arm()
    driver.trigger()  # Should succeed

    driver.disarm()
```

#### 4. Use Driver

```python
from bpd_drivers import LaserFIDriver
from bpd_core import validate_probe_moku_compatibility
from moku_models import MOKU_GO_PLATFORM

# Initialize
driver = LaserFIDriver()
driver.initialize()

# Validate
validate_probe_moku_compatibility(driver, MOKU_GO_PLATFORM)

# Configure
driver.set_voltage(3.0)  # Laser power
driver.set_pulse_width(100)  # 100ns pulse

# Use
driver.arm()
driver.trigger()
driver.disarm()
```

---

## Testing Strategies

### Unit Testing (Simulation Mode)

```python
import pytest
from bpd_drivers import DS1120ADriver

def test_ds1120a_capabilities():
    """Test driver reports correct capabilities."""
    driver = DS1120ADriver()
    caps = driver.capabilities

    # From riscure-models specs
    assert caps.max_voltage_v == 3.3
    assert caps.min_pulse_width_ns == 50
    assert caps.max_pulse_width_ns == 50

def test_ds1120a_voltage_range():
    """Test voltage validation."""
    driver = DS1120ADriver()
    driver.initialize()

    # Valid
    driver.set_voltage(0.0)
    driver.set_voltage(1.65)
    driver.set_voltage(3.3)

    # Invalid
    with pytest.raises(ValueError):
        driver.set_voltage(-0.1)
    with pytest.raises(ValueError):
        driver.set_voltage(5.0)

def test_ds1120a_pulse_width_fixed():
    """Test pulse width constraint."""
    driver = DS1120ADriver()
    driver.initialize()

    # Valid (only 50ns accepted)
    driver.set_pulse_width(50)

    # Invalid (not 50ns)
    with pytest.raises(ValueError):
        driver.set_pulse_width(100)

def test_ds1120a_state_machine():
    """Test arm → trigger → disarm sequence."""
    driver = DS1120ADriver()
    driver.initialize()

    # Initial state: ready
    status = driver.get_status()
    assert status.ready
    assert not status.armed

    # Arm
    driver.arm()
    status = driver.get_status()
    assert status.armed
    assert not status.ready

    # Trigger (works when armed)
    driver.trigger()

    # Disarm
    driver.disarm()
    status = driver.get_status()
    assert status.ready
    assert not status.armed

def test_ds1120a_trigger_without_arm():
    """Test trigger fails if not armed."""
    driver = DS1120ADriver()
    driver.initialize()

    with pytest.raises(RuntimeError, match="not armed"):
        driver.trigger()
```

### Integration Testing (Hardware)

```python
import pytest
from bpd_drivers import DS1120ADriver

@pytest.mark.hardware
@pytest.mark.skipif(not hardware_available(), reason="Hardware not connected")
def test_ds1120a_real_hardware():
    """Test with actual DS1120A probe."""
    driver = DS1120ADriver()
    driver.initialize()

    # Should connect to hardware
    assert driver._hw_connected

    # Configure
    driver.set_voltage(3.3)
    driver.set_pulse_width(50)

    # Arm
    driver.arm()
    status = driver.get_status()
    assert status.armed

    # Trigger
    driver.trigger()

    # Check for faults
    import time
    time.sleep(0.01)  # Wait for pulse completion
    status = driver.get_status()
    assert not status.fault

    # Disarm
    driver.disarm()
    driver.shutdown()

def hardware_available() -> bool:
    """Check if hardware is connected."""
    try:
        driver = DS1120ADriver()
        driver.initialize()
        connected = driver._hw_connected
        driver.shutdown()
        return connected
    except:
        return False
```

---

## Common Tasks

### Query Driver Capabilities

```python
from bpd_drivers import DS1120ADriver

driver = DS1120ADriver()
caps = driver.capabilities

print(f"Voltage: {caps.min_voltage_v}V - {caps.max_voltage_v}V")
print(f"Pulse width: {caps.min_pulse_width_ns}ns - {caps.max_pulse_width_ns}ns")
print(f"Resolution: {caps.pulse_width_resolution_ns}ns")
print(f"External trigger: {caps.supports_external_trigger}")
print(f"Internal trigger: {caps.supports_internal_trigger}")
```

### Validate with Multiple Platforms

```python
from bpd_core import validate_probe_moku_compatibility
from bpd_drivers import DS1120ADriver
from moku_models import MOKU_GO_PLATFORM, MOKU_LAB_PLATFORM, MOKU_PRO_PLATFORM

driver = DS1120ADriver()

platforms = [MOKU_GO_PLATFORM, MOKU_LAB_PLATFORM, MOKU_PRO_PLATFORM]

for platform in platforms:
    try:
        validate_probe_moku_compatibility(driver, platform)
        print(f"✓ Compatible with {platform.name}")
    except Exception as e:
        print(f"✗ Incompatible with {platform.name}: {e}")
```

### Switch Between Probes

```python
from bpd_core import get_driver

# Config-driven probe selection
probe_configs = {
    "emfi": {"type": "ds1120a", "voltage": 3.3, "pulse_width": 50},
    "laser": {"type": "laser_fi", "voltage": 3.0, "pulse_width": 100},
}

for campaign, config in probe_configs.items():
    print(f"\nCampaign: {campaign}")

    # Load driver
    DriverClass = get_driver(config["type"])
    driver = DriverClass()
    driver.initialize()

    # Configure
    driver.set_voltage(config["voltage"])
    driver.set_pulse_width(config["pulse_width"])

    # Use (same code for all probes!)
    driver.arm()
    driver.trigger()
    driver.disarm()
```

---

## File Structure

```
bpd-drivers/
├── src/
│   └── bpd_drivers/
│       ├── __init__.py            # Public API
│       ├── ds1120a.py             # DS1120A driver (reference)
│       ├── laser_fi.py            # (Future) Laser FI driver
│       ├── rf_inject.py           # (Future) RF injection driver
│       └── voltage_glitch.py      # (Future) Voltage glitching driver
├── tests/
│   ├── test_ds1120a.py            # DS1120A tests
│   ├── test_laser_fi.py           # (Future) Laser tests
│   └── test_registry.py           # Auto-discovery tests
├── pyproject.toml
├── llms.txt                       # Tier 1 quick reference
├── CLAUDE.md                      # This file (Tier 2 deep dive)
└── README.md
```

---

## Dependencies

**Direct:**
- `bpd-core` - FIProbeInterface protocol
- `riscure-models` - DS1120A specs (DS1120A driver only)
- Python 3.9+

**Used by:**
- User applications
- BPD integration examples

---

## Development Workflow

```bash
# Install in editable mode
cd bpd/bpd-drivers
uv pip install -e .

# Run tests
pytest tests/

# Run hardware tests (if connected)
pytest tests/ -m hardware

# Skip hardware tests
pytest tests/ -m "not hardware"

# Type check
mypy src/bpd_drivers/

# Format
black src/
ruff check src/
```

---

## Future Enhancements

**Planned:**
- [ ] Laser FI driver implementation
- [ ] RF injection driver
- [ ] Voltage glitching driver
- [ ] DS1140A driver (bidirectional EMFI)
- [ ] Driver configuration validation

**Potential:**
- [ ] Driver auto-detection (USB VID/PID)
- [ ] Firmware version checking
- [ ] Calibration data loading
- [ ] Real-time monitoring (temperature, current)

---

**Last Updated:** 2025-11-04
**Maintainer:** BPD Development Team
**License:** MIT
**Part of:** BPD-002 (Basic Probe Driver)
