# BPD Core

Generic probe driver framework for Moku platform.

## Overview

Provides abstract interfaces and utilities for building probe drivers that work across multiple FI probe vendors.

## Key Components

- `FIProbeInterface` - Abstract protocol for probe drivers
- `ProbeCapabilities` - Hardware capability specifications
- `ProbeRegistry` - Driver discovery and loading
- `validate_probe_moku_compatibility()` - Safety validation

## Usage

```python
from bpd_core import FIProbeInterface, ProbeCapabilities

class MyProbeDriver:
    """Implement the FIProbeInterface protocol."""

    @property
    def capabilities(self) -> ProbeCapabilities:
        return ProbeCapabilities(
            min_voltage_v=0.0,
            max_voltage_v=3.3,
            min_pulse_width_ns=10,
            max_pulse_width_ns=10000,
            pulse_width_resolution_ns=1,
            supports_external_trigger=True,
            supports_internal_trigger=False,
        )

    def initialize(self) -> None:
        # Hardware init
        pass

    # ... implement other interface methods
```
