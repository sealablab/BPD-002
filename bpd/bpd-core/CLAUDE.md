# CLAUDE.md - BPD Core Framework

## Project Overview

**bpd-core** is the generic fault injection probe driver framework for Moku platform development. It provides vendor-agnostic interfaces that enable writing probe drivers once and using them across multiple FI probe types (EMFI, laser FI, RF injection, voltage glitching).

**Purpose:** Abstract probe hardware differences behind a common Python protocol, enabling:
- Easy probe swapping without code changes
- Voltage safety validation before hardware connection
- Driver discovery via automatic registration
- Simulation without physical hardware

**Part of:** BPD-002 (Basic Probe Driver) - Multi-vendor probe integration for Moku

**Design Philosophy:** Protocol-based (duck typing) rather than inheritance, inspired by DS1120A standard but extended for multi-vendor support.

---

## Quick Start

```python
from bpd_core import FIProbeInterface, ProbeCapabilities, register_driver
from bpd_core import validate_probe_moku_compatibility
from moku_models import MOKU_GO_PLATFORM

# Create driver (manual or via registry)
from bpd_drivers import DS1120ADriver
driver = DS1120ADriver()

# Validate voltage safety
validate_probe_moku_compatibility(driver, MOKU_GO_PLATFORM)

# Use probe
driver.initialize()
driver.set_voltage(3.3)
driver.set_pulse_width(100)
driver.arm()
driver.trigger()
```

---

## Architecture

### Core Components

**1. FIProbeInterface (Protocol)**

Abstract interface defining probe driver contract:

```python
from typing import Protocol
from dataclasses import dataclass

class FIProbeInterface(Protocol):
    """Protocol that all probe drivers must implement."""

    @property
    def capabilities(self) -> ProbeCapabilities:
        """Return hardware capability specifications."""
        ...

    def initialize(self) -> None:
        """Initialize hardware connection."""
        ...

    def set_voltage(self, voltage_v: float) -> None:
        """Set probe voltage/power level."""
        ...

    def set_pulse_width(self, width_ns: int) -> None:
        """Set pulse duration in nanoseconds."""
        ...

    def arm(self) -> None:
        """Arm probe for trigger."""
        ...

    def trigger(self) -> None:
        """Execute fault injection pulse."""
        ...

    def disarm(self) -> None:
        """Disarm probe (safe state)."""
        ...

    def get_status(self) -> ProbeStatus:
        """Query probe state."""
        ...

    def shutdown(self) -> None:
        """Safe shutdown sequence."""
        ...
```

**Design rationale:**
- Protocol (not ABC) enables duck typing flexibility
- No inheritance hierarchy simplifies driver implementation
- Methods correspond to DS1120A control patterns (widely adopted)
- Can be extended per-driver without breaking interface

**2. ProbeCapabilities (Dataclass)**

Hardware specification model:

```python
@dataclass
class ProbeCapabilities:
    """Probe hardware capability specification."""

    min_voltage_v: float
    max_voltage_v: float
    min_pulse_width_ns: int
    max_pulse_width_ns: int
    pulse_width_resolution_ns: int
    supports_external_trigger: bool
    supports_internal_trigger: bool
```

**Usage:**
- Drivers return this from `.capabilities` property
- Validation framework checks Moku compatibility
- User code can query before configuration

**3. ProbeRegistry (Singleton)**

Driver discovery and loading system:

```python
class ProbeRegistry:
    """Central registry for probe drivers."""

    _drivers: Dict[str, Type] = {}

    @classmethod
    def register(cls, name: str, driver_class: Type) -> None:
        """Register driver by name."""
        cls._drivers[name] = driver_class

    @classmethod
    def get(cls, name: str) -> Type:
        """Retrieve driver class by name."""
        return cls._drivers[name]

    @classmethod
    def list_drivers(cls) -> List[str]:
        """List all registered driver names."""
        return list(cls._drivers.keys())
```

**Usage via decorator:**
```python
@register_driver("my_probe")
class MyProbeDriver:
    # Implementation
    pass
```

**4. Validation Framework**

Voltage safety checking before hardware connection:

```python
def validate_probe_moku_compatibility(
    probe_driver: FIProbeInterface,
    platform: MokuPlatform,
    output_id: str = "OUT1"
) -> None:
    """
    Validate probe voltage compatibility with Moku platform.

    Raises:
        ProbeValidationError: If voltage mismatch detected
    """
    caps = probe_driver.capabilities
    moku_output = platform.get_analog_output_by_id(output_id)

    # Check voltage range
    if caps.max_voltage_v > moku_output.voltage_range_vpp:
        raise ProbeValidationError(
            f"Probe requires {caps.max_voltage_v}V but "
            f"Moku {output_id} max is {moku_output.voltage_range_vpp}V"
        )

    # Additional checks...
```

**Safety checks:**
- Probe max voltage ≤ Moku output voltage
- Signal type compatibility (digital vs analog)
- Timing constraint validation

---

## Design Rationale

### Why Protocol (Not ABC)?

**Decision:** Use `typing.Protocol` instead of `abc.ABC`

**Rationale:**
- Duck typing: Drivers don't need explicit inheritance
- Flexibility: Can implement interface retroactively
- Simplicity: No `@abstractmethod` boilerplate
- Type checking: mypy validates protocol compliance

**Trade-off:** No runtime enforcement (but mypy catches at dev time)

### Why Registry Pattern?

**Decision:** Central driver registry with decorator-based registration

**Rationale:**
- Auto-discovery: Drivers self-register on import
- Loose coupling: No hardcoded driver imports
- Extensibility: New drivers added without core changes
- User choice: Load drivers by name (config-driven)

**Implementation:**
```python
# Driver module (auto-registers on import)
@register_driver("ds1120a")
class DS1120ADriver:
    pass

# User code (load by name)
DriverClass = get_driver("ds1120a")
driver = DriverClass()
```

### Why Capabilities Dataclass?

**Decision:** Structured hardware spec (not kwargs or dict)

**Rationale:**
- Type safety: Pydantic/dataclass validation
- Discoverability: IDE autocomplete
- Documentation: Self-documenting fields
- Reusability: Shared by validation framework

**Alternative considered:** Plain dict (rejected for lack of type safety)

### Why Separate Validation?

**Decision:** `validate_probe_moku_compatibility()` as standalone function

**Rationale:**
- Separation of concerns: Drivers shouldn't know about Moku
- Reusability: Works with any ProbeCapabilities
- Testability: Easy to unit test
- Flexibility: Can add platform-specific logic

**Integration point:** Depends on both `bpd-core` and `moku-models`

---

## Integration Patterns

### Pattern 1: Driver Development

**Creating a new probe driver:**

```python
# Step 1: Define driver class
from bpd_core import FIProbeInterface, ProbeCapabilities, register_driver, ProbeStatus

@register_driver("laser_fi")
class LaserFIDriver:
    """Laser fault injection probe driver."""

    def __init__(self):
        self._armed = False
        self._voltage = 0.0
        self._pulse_width = 0
        # Hardware connection state
        self._hw_connected = False

    # Step 2: Implement capabilities
    @property
    def capabilities(self) -> ProbeCapabilities:
        return ProbeCapabilities(
            min_voltage_v=0.0,
            max_voltage_v=5.0,
            min_pulse_width_ns=1,
            max_pulse_width_ns=1000,
            pulse_width_resolution_ns=1,
            supports_external_trigger=True,
            supports_internal_trigger=True,
        )

    # Step 3: Implement interface methods
    def initialize(self) -> None:
        """Initialize laser hardware (or simulate)."""
        # Try hardware connection
        try:
            self._connect_to_hardware()
            self._hw_connected = True
        except HardwareError:
            # Graceful degradation: simulation mode
            self._hw_connected = False

    def set_voltage(self, voltage_v: float) -> None:
        """Set laser power (voltage analog)."""
        caps = self.capabilities
        if not (caps.min_voltage_v <= voltage_v <= caps.max_voltage_v):
            raise ValueError(f"Voltage {voltage_v}V out of range")
        self._voltage = voltage_v
        if self._hw_connected:
            self._hw_set_power(voltage_v)

    def set_pulse_width(self, width_ns: int) -> None:
        """Set laser pulse duration."""
        caps = self.capabilities
        if not (caps.min_pulse_width_ns <= width_ns <= caps.max_pulse_width_ns):
            raise ValueError(f"Pulse width {width_ns}ns out of range")
        self._pulse_width = width_ns
        if self._hw_connected:
            self._hw_set_pulse_width(width_ns)

    def arm(self) -> None:
        """Arm laser for trigger."""
        self._armed = True
        if self._hw_connected:
            self._hw_arm()

    def trigger(self) -> None:
        """Fire laser pulse."""
        if not self._armed:
            raise RuntimeError("Probe not armed")
        if self._hw_connected:
            self._hw_trigger()
        else:
            # Simulation: just log
            print(f"[SIM] Laser pulse: {self._voltage}V, {self._pulse_width}ns")

    def disarm(self) -> None:
        """Disarm laser (safe state)."""
        self._armed = False
        if self._hw_connected:
            self._hw_disarm()

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
            self._hw_disconnect()

    # Hardware abstraction (driver-specific)
    def _connect_to_hardware(self) -> None:
        # Driver-specific hardware init
        pass

    def _hw_set_power(self, voltage_v: float) -> None:
        # Driver-specific power control
        pass

    # ... other hardware methods
```

**Key patterns:**
- Graceful degradation: Works without hardware (simulation)
- Validation: Range checking in setters
- Hardware abstraction: Private methods for hardware I/O
- Auto-registration: `@register_driver()` decorator

### Pattern 2: Platform Validation

**Validating probe before wiring:**

```python
from bpd_core import validate_probe_moku_compatibility, ProbeValidationError
from bpd_drivers import DS1120ADriver
from moku_models import MOKU_GO_PLATFORM, MOKU_LAB_PLATFORM

driver = DS1120ADriver()

# Validate with Moku Go
try:
    validate_probe_moku_compatibility(
        probe_driver=driver,
        platform=MOKU_GO_PLATFORM,
        output_id="OUT1"
    )
    print("✓ Safe: Moku Go OUT1 → DS1120A digital_glitch (3.3V TTL)")
except ProbeValidationError as e:
    print(f"✗ Unsafe: {e}")

# Validate with Moku Lab
try:
    validate_probe_moku_compatibility(
        probe_driver=driver,
        platform=MOKU_LAB_PLATFORM,
        output_id="OUT2"
    )
    print("✓ Safe: Moku Lab OUT2 → DS1120A")
except ProbeValidationError as e:
    print(f"✗ Unsafe: {e}")
```

**What it checks:**
- Probe `max_voltage_v` ≤ Moku output voltage
- Signal compatibility (TTL vs analog)
- Impedance matching (future)

### Pattern 3: Dynamic Driver Loading

**Config-driven probe selection:**

```python
from bpd_core import get_driver, list_drivers
import yaml

# Load user configuration
with open("config.yaml") as f:
    config = yaml.safe_load(f)

probe_name = config["probe"]["type"]  # "ds1120a", "laser_fi", etc.

# List available drivers
print(f"Available: {list_drivers()}")

# Load driver by name
DriverClass = get_driver(probe_name)
driver = DriverClass()

# Same code works for any probe!
driver.initialize()
driver.set_voltage(config["probe"]["voltage"])
driver.set_pulse_width(config["probe"]["pulse_width"])
driver.arm()
driver.trigger()
```

**Benefits:**
- User configures probe without code changes
- Testing: Swap probes during development
- Deployment: Different probes per campaign

---

## Testing Strategies

### Unit Testing (Without Hardware)

```python
import pytest
from bpd_drivers import DS1120ADriver

def test_capabilities():
    driver = DS1120ADriver()
    caps = driver.capabilities

    assert caps.min_voltage_v == 0.0
    assert caps.max_voltage_v == 3.3
    assert caps.min_pulse_width_ns == 50
    assert caps.max_pulse_width_ns == 50  # Fixed for DS1120A

def test_voltage_validation():
    driver = DS1120ADriver()
    driver.initialize()

    # Valid voltage
    driver.set_voltage(3.3)

    # Invalid voltage
    with pytest.raises(ValueError):
        driver.set_voltage(5.0)  # Exceeds max

def test_arm_trigger_sequence():
    driver = DS1120ADriver()
    driver.initialize()

    # Cannot trigger before arming
    with pytest.raises(RuntimeError):
        driver.trigger()

    # Arm then trigger
    driver.arm()
    driver.trigger()  # Should succeed

def test_platform_validation():
    from bpd_core import validate_probe_moku_compatibility
    from moku_models import MOKU_GO_PLATFORM

    driver = DS1120ADriver()

    # Should pass (DS1120A max 3.3V, Moku Go supports TTL)
    validate_probe_moku_compatibility(driver, MOKU_GO_PLATFORM)
```

### Integration Testing (With Hardware)

```python
@pytest.mark.hardware
def test_real_hardware_trigger():
    """Test with actual DS1120A probe connected."""
    driver = DS1120ADriver()
    driver.initialize()

    # Configure
    driver.set_voltage(3.3)
    driver.set_pulse_width(50)

    # Arm and trigger
    driver.arm()
    status = driver.get_status()
    assert status.armed

    driver.trigger()

    # Wait for completion
    import time
    time.sleep(0.001)

    status = driver.get_status()
    assert not status.busy
    assert not status.fault

    driver.disarm()
```

**Test organization:**
- Unit tests: No hardware required (default)
- Integration tests: `@pytest.mark.hardware` (skip by default)
- Simulation: Drivers work without hardware

---

## Common Tasks

### Add New Probe Type

See `../bpd-drivers/CLAUDE.md` for complete guide.

**Summary:**
1. Create driver module implementing `FIProbeInterface`
2. Define `ProbeCapabilities` property
3. Add `@register_driver("name")` decorator
4. Implement all interface methods
5. Add to `bpd-drivers/__init__.py` exports
6. Write tests

### Query Driver Capabilities

```python
from bpd_drivers import DS1120ADriver

driver = DS1120ADriver()
caps = driver.capabilities

print(f"Voltage: {caps.min_voltage_v}V - {caps.max_voltage_v}V")
print(f"Pulse width: {caps.min_pulse_width_ns}ns - {caps.max_pulse_width_ns}ns")
print(f"Resolution: {caps.pulse_width_resolution_ns}ns")
print(f"External trigger: {caps.supports_external_trigger}")
```

### Handle Probe Faults

```python
from bpd_drivers import DS1120ADriver

driver = DS1120ADriver()
driver.initialize()
driver.arm()

try:
    driver.trigger()
except ProbeError as e:
    print(f"Probe fault: {e}")
    driver.disarm()  # Safe state

# Check status
status = driver.get_status()
if status.fault:
    print("Fault detected, check hardware")
```

### Simulate Without Hardware

```python
# Driver automatically falls back to simulation if hardware unavailable
driver = DS1120ADriver()
driver.initialize()  # Tries hardware, falls back to sim

# Works same as hardware mode
driver.set_voltage(3.3)
driver.arm()
driver.trigger()  # Prints simulation message instead of real pulse
```

---

## Error Handling

### Custom Exceptions

```python
class ProbeError(Exception):
    """Base exception for probe errors."""
    pass

class ProbeValidationError(ProbeError):
    """Voltage/platform incompatibility."""
    pass

class ProbeHardwareError(ProbeError):
    """Hardware communication failure."""
    pass

class ProbeStateError(ProbeError):
    """Invalid state transition (e.g., trigger before arm)."""
    pass
```

### Error Patterns

**Validation errors:**
```python
# Raised by validate_probe_moku_compatibility()
try:
    validate_probe_moku_compatibility(driver, platform)
except ProbeValidationError as e:
    print(f"Incompatible: {e}")
    # Don't wire probe to Moku!
```

**Hardware errors:**
```python
# Raised during hardware communication
try:
    driver.initialize()
except ProbeHardwareError as e:
    print(f"Hardware unavailable: {e}")
    # Driver falls back to simulation
```

**State errors:**
```python
# Raised for invalid operations
try:
    driver.trigger()  # Before arming
except ProbeStateError as e:
    print(f"Invalid operation: {e}")
    driver.arm()  # Fix state, retry
```

---

## File Structure

```
bpd-core/
├── src/
│   └── bpd_core/
│       ├── __init__.py           # Public API exports
│       ├── interface.py          # FIProbeInterface protocol
│       ├── capabilities.py       # ProbeCapabilities dataclass
│       ├── registry.py           # ProbeRegistry, @register_driver
│       ├── validation.py         # validate_probe_moku_compatibility()
│       ├── exceptions.py         # Custom exceptions
│       └── status.py             # ProbeStatus dataclass
├── tests/
│   ├── test_interface.py         # Protocol compliance tests
│   ├── test_registry.py          # Driver discovery tests
│   └── test_validation.py        # Voltage safety tests
├── pyproject.toml
├── llms.txt                      # Tier 1 quick reference
├── CLAUDE.md                     # This file (Tier 2 deep dive)
└── README.md
```

---

## Dependencies

**Direct:**
- `moku-models` - Platform specifications for validation
- Python 3.9+ - Protocol support, type hints

**Optional:**
- `riscure-models` - DS1120A specs (only if using DS1120A driver)
- `pydantic` - Enhanced validation (future)

**Used by:**
- `bpd-drivers` - Probe-specific implementations
- User applications

---

## Development Workflow

```bash
# Install in editable mode
cd bpd/bpd-core
uv pip install -e .

# Run tests
pytest tests/

# Run with coverage
pytest --cov=bpd_core tests/

# Type check
mypy src/bpd_core/

# Format
black src/
ruff check src/
```

---

## Future Enhancements

**Planned:**
- [ ] Pydantic validation for ProbeCapabilities
- [ ] Probe calibration data models
- [ ] Multi-probe coordination (simultaneous use)
- [ ] Probe health monitoring (temperature, current)
- [ ] Extended validation (impedance, timing)

**Potential:**
- [ ] Probe switching/multiplexing
- [ ] Advanced triggering patterns (burst, sweep)
- [ ] Real-time feedback (coil current, reflection)

---

**Last Updated:** 2025-11-04
**Maintainer:** BPD Development Team
**License:** MIT
**Part of:** BPD-002 (Basic Probe Driver)
