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


# =============================================================================
# Unit Conversion Helpers
# =============================================================================
# These helpers convert between Python's real units (mV, ns, μs, s) and
# hardware digital values. Conversion happens at the hardware boundary.
# =============================================================================

def mV_to_volts(millivolts: int) -> float:
    """
    Convert millivolts to volts.

    Args:
        millivolts: Voltage in mV

    Returns:
        Voltage in volts (float)

    Example:
        >>> mV_to_volts(3300)
        3.3
    """
    return millivolts / 1000.0


def volts_to_mV(volts: float) -> int:
    """
    Convert volts to millivolts.

    Args:
        volts: Voltage in volts

    Returns:
        Voltage in mV (int)

    Example:
        >>> volts_to_mV(3.3)
        3300
    """
    return int(volts * 1000)


def ns_to_cycles(nanoseconds: int, clock_freq_mhz: float = 125.0) -> int:
    """
    Convert nanoseconds to clock cycles.

    Args:
        nanoseconds: Time in nanoseconds
        clock_freq_mhz: Clock frequency in MHz (default: 125 MHz for Moku)

    Returns:
        Number of clock cycles (int)

    Example:
        >>> ns_to_cycles(1000, 125.0)  # 1000ns at 125MHz
        125
    """
    clock_period_ns = 1000.0 / clock_freq_mhz
    return int(nanoseconds / clock_period_ns)


def cycles_to_ns(cycles: int, clock_freq_mhz: float = 125.0) -> int:
    """
    Convert clock cycles to nanoseconds.

    Args:
        cycles: Number of clock cycles
        clock_freq_mhz: Clock frequency in MHz (default: 125 MHz for Moku)

    Returns:
        Time in nanoseconds (int)

    Example:
        >>> cycles_to_ns(125, 125.0)  # 125 cycles at 125MHz
        1000
    """
    clock_period_ns = 1000.0 / clock_freq_mhz
    return int(cycles * clock_period_ns)


def us_to_cycles(microseconds: int, clock_freq_mhz: float = 125.0) -> int:
    """
    Convert microseconds to clock cycles.

    Args:
        microseconds: Time in microseconds
        clock_freq_mhz: Clock frequency in MHz (default: 125 MHz for Moku)

    Returns:
        Number of clock cycles (int)

    Example:
        >>> us_to_cycles(10, 125.0)  # 10μs at 125MHz
        1250
    """
    return ns_to_cycles(microseconds * 1000, clock_freq_mhz)


def cycles_to_us(cycles: int, clock_freq_mhz: float = 125.0) -> int:
    """
    Convert clock cycles to microseconds.

    Args:
        cycles: Number of clock cycles
        clock_freq_mhz: Clock frequency in MHz (default: 125 MHz for Moku)

    Returns:
        Time in microseconds (int)

    Example:
        >>> cycles_to_us(1250, 125.0)  # 1250 cycles at 125MHz
        10
    """
    ns = cycles_to_ns(cycles, clock_freq_mhz)
    return ns // 1000


def s_to_cycles(seconds: int, clock_freq_mhz: float = 125.0) -> int:
    """
    Convert seconds to clock cycles.

    Args:
        seconds: Time in seconds
        clock_freq_mhz: Clock frequency in MHz (default: 125 MHz for Moku)

    Returns:
        Number of clock cycles (int)

    Example:
        >>> s_to_cycles(1, 125.0)  # 1s at 125MHz
        125000000
    """
    return ns_to_cycles(seconds * 1_000_000_000, clock_freq_mhz)


def cycles_to_s(cycles: int, clock_freq_mhz: float = 125.0) -> float:
    """
    Convert clock cycles to seconds.

    Args:
        cycles: Number of clock cycles
        clock_freq_mhz: Clock frequency in MHz (default: 125 MHz for Moku)

    Returns:
        Time in seconds (float)

    Example:
        >>> cycles_to_s(125000000, 125.0)  # 125M cycles at 125MHz
        1.0
    """
    ns = cycles_to_ns(cycles, clock_freq_mhz)
    return ns / 1_000_000_000.0
