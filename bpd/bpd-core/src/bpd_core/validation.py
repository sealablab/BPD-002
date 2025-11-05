"""
Validation utilities for probe-Moku platform compatibility.

Ensures safe electrical interfacing between probes and Moku hardware.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from moku_models import MokuPlatform
    from bpd_core.interface import FIProbeInterface


class ProbeValidationError(Exception):
    """Raised when probe is incompatible with Moku platform."""

    pass


def validate_probe_moku_compatibility(
    probe: "FIProbeInterface",
    moku_platform: "MokuPlatform",
    output_id: str = "OUT1",
    input_id: str = "IN1",
) -> None:
    """
    Validate that probe can safely interface with Moku platform.

    Checks:
    - Voltage compatibility (probe input vs Moku output)
    - Timing constraints
    - Signal levels

    Args:
        probe: Probe driver instance
        moku_platform: Moku platform (Go/Lab/Pro/Delta)
        output_id: Moku output channel to use (default: OUT1)
        input_id: Moku input channel to use (default: IN1)

    Raises:
        ProbeValidationError: If incompatibility detected

    Example:
        >>> from moku_models import MOKU_GO_PLATFORM
        >>> from bpd_drivers import DS1120ADriver
        >>> driver = DS1120ADriver()
        >>> validate_probe_moku_compatibility(driver, MOKU_GO_PLATFORM)
    """
    # Get Moku output specs
    try:
        moku_output = moku_platform.get_analog_output_by_id(output_id)
    except (AttributeError, KeyError):
        raise ProbeValidationError(
            f"Moku platform '{moku_platform.name}' does not have output '{output_id}'"
        )

    # Check voltage compatibility
    probe_caps = probe.capabilities
    moku_max_v = moku_output.voltage_range_vpp / 2  # Peak voltage (Vpp to ±V)

    if probe_caps.max_voltage_v > moku_max_v:
        raise ProbeValidationError(
            f"Probe max voltage ({probe_caps.max_voltage_v}V) exceeds "
            f"Moku {output_id} max output ({moku_max_v}V)"
        )

    # TODO: Add more validation as needed:
    # - Input voltage compatibility (probe output → Moku input)
    # - Timing/bandwidth checks
    # - Impedance matching warnings

    # If we get here, compatibility check passed
    pass


def validate_voltage_safe(voltage_v: float, min_v: float, max_v: float) -> None:
    """
    Validate that voltage is within safe range.

    Args:
        voltage_v: Requested voltage
        min_v: Minimum safe voltage
        max_v: Maximum safe voltage

    Raises:
        ValueError: If voltage out of range
    """
    if not (min_v <= voltage_v <= max_v):
        raise ValueError(
            f"Voltage {voltage_v}V out of safe range [{min_v}V, {max_v}V]"
        )


def validate_pulse_width_safe(width_ns: int, min_ns: int, max_ns: int) -> None:
    """
    Validate that pulse width is within safe range.

    Args:
        width_ns: Requested pulse width (nanoseconds)
        min_ns: Minimum safe width
        max_ns: Maximum safe width

    Raises:
        ValueError: If width out of range
    """
    if not (min_ns <= width_ns <= max_ns):
        raise ValueError(
            f"Pulse width {width_ns}ns out of safe range [{min_ns}ns, {max_ns}ns]"
        )
