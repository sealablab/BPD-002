"""
Riscure DS1120A probe driver.

Implements BPD FIProbeInterface for the Riscure DS1120A EMFI probe.
Uses riscure-models for hardware specifications.
"""

from typing import Optional
import time

from bpd_core import FIProbeInterface, ProbeCapabilities, register_driver
from bpd_core.validation import validate_voltage_safe, validate_pulse_width_safe
from riscure_models import DS1120A_PLATFORM


@register_driver("ds1120a")
class DS1120ADriver:
    """
    Driver for Riscure DS1120A EMFI probe.

    This is the reference implementation showing how to use riscure-models
    specifications with the BPD framework.

    Example:
        >>> from bpd_drivers import DS1120ADriver
        >>> from moku_models import MOKU_GO_PLATFORM
        >>> from bpd_core import validate_probe_moku_compatibility
        >>>
        >>> driver = DS1120ADriver()
        >>> driver.initialize()
        >>> validate_probe_moku_compatibility(driver, MOKU_GO_PLATFORM)
        >>> driver.set_voltage(3.3)
        >>> driver.set_pulse_width(100)
        >>> driver.arm()
        >>> driver.trigger()
    """

    def __init__(self):
        """Initialize DS1120A driver using specifications from riscure-models."""
        self._probe_spec = DS1120A_PLATFORM
        self._armed = False
        self._initialized = False

        # Current configuration
        self._voltage_v: float = 0.0
        self._pulse_width_ns: int = 0

        # Get digital glitch port specs from riscure-models
        self._glitch_port = self._probe_spec.get_port_by_id("digital_glitch")

        # Build capabilities from probe specs
        self._capabilities = ProbeCapabilities(
            min_voltage_v=self._glitch_port.voltage_min,
            max_voltage_v=self._glitch_port.voltage_max,
            min_pulse_width_ns=10,  # DS1120A typical minimum
            max_pulse_width_ns=10000,  # DS1120A typical maximum
            pulse_width_resolution_ns=1,  # 1ns resolution
            supports_external_trigger=True,
            supports_internal_trigger=False,  # Needs external trigger
            supports_voltage_sweep=False,  # Manual control only
            supports_pulse_train=False,  # Single pulses
        )

        # Timing tracking
        self._last_trigger_time: Optional[float] = None

    @property
    def capabilities(self) -> ProbeCapabilities:
        """Get DS1120A hardware capabilities."""
        return self._capabilities

    def initialize(self) -> None:
        """
        Initialize DS1120A probe.

        In a real implementation, this would:
        - Establish communication with probe hardware
        - Run self-test
        - Set safe default parameters
        - Verify voltage/current limits

        For this reference implementation, we simulate initialization.
        """
        if self._initialized:
            return

        # TODO: Real hardware initialization
        # - Connect to probe via USB/Ethernet
        # - Run built-in self-test (BIST)
        # - Configure safety limits

        # Set safe defaults
        self._voltage_v = 0.0
        self._pulse_width_ns = 100  # Safe default pulse width

        self._initialized = True
        print(f"✓ DS1120A initialized (voltage range: {self._capabilities.min_voltage_v}V - {self._capabilities.max_voltage_v}V)")

    def set_voltage(self, voltage_v: float) -> None:
        """
        Set DS1120A output voltage.

        Args:
            voltage_v: Voltage in volts (0-3.3V for DS1120A)

        Raises:
            ValueError: If voltage out of range
            RuntimeError: If not initialized
        """
        if not self._initialized:
            raise RuntimeError("Driver not initialized. Call initialize() first.")

        # Validate against probe capabilities
        validate_voltage_safe(
            voltage_v,
            self._capabilities.min_voltage_v,
            self._capabilities.max_voltage_v,
        )

        # Additional validation using riscure-models
        if not self._glitch_port.is_voltage_compatible(voltage_v):
            raise ValueError(
                f"Voltage {voltage_v}V not compatible with DS1120A digital glitch port"
            )

        # TODO: Send voltage command to hardware
        self._voltage_v = voltage_v
        print(f"✓ DS1120A voltage set to {voltage_v}V")

    def set_pulse_width(self, width_ns: int) -> None:
        """
        Set DS1120A pulse width.

        Args:
            width_ns: Pulse width in nanoseconds

        Raises:
            ValueError: If width out of range
            RuntimeError: If not initialized
        """
        if not self._initialized:
            raise RuntimeError("Driver not initialized. Call initialize() first.")

        # Validate against probe capabilities
        validate_pulse_width_safe(
            width_ns,
            self._capabilities.min_pulse_width_ns,
            self._capabilities.max_pulse_width_ns,
        )

        # TODO: Send pulse width command to hardware
        self._pulse_width_ns = width_ns
        print(f"✓ DS1120A pulse width set to {width_ns}ns")

    def arm(self) -> None:
        """
        Arm DS1120A probe for triggering.

        After arming, probe will fire on next external trigger.
        """
        if not self._initialized:
            raise RuntimeError("Driver not initialized. Call initialize() first.")

        # TODO: Send arm command to hardware
        self._armed = True
        self._last_trigger_time = None
        print("✓ DS1120A armed")

    def trigger(self) -> None:
        """
        Manually trigger DS1120A (software trigger).

        Note: DS1120A primarily uses external hardware triggers,
        but supports software trigger for testing.

        Raises:
            RuntimeError: If not armed
        """
        if not self._armed:
            raise RuntimeError("Probe not armed. Call arm() first.")

        # TODO: Send trigger command to hardware
        self._last_trigger_time = time.time()
        print(f"✓ DS1120A triggered (voltage={self._voltage_v}V, width={self._pulse_width_ns}ns)")

        # Note: In real hardware, probe would auto-disarm after trigger
        # For now, keep armed for simplicity

    def disarm(self) -> None:
        """
        Disarm DS1120A probe (safe state).

        After disarming, probe will not respond to triggers.
        """
        # TODO: Send disarm command to hardware
        self._armed = False
        print("✓ DS1120A disarmed")

    def get_status(self) -> dict:
        """
        Get current DS1120A status.

        Returns:
            Dictionary with status information
        """
        status = {
            "armed": self._armed,
            "ready": self._initialized and not self._armed,
            "fault": False,  # TODO: Read actual fault status from hardware
            "voltage_v": self._voltage_v,
            "pulse_width_ns": self._pulse_width_ns,
        }

        if self._last_trigger_time is not None:
            status["last_trigger_time"] = time.time() - self._last_trigger_time

        return status

    def shutdown(self) -> None:
        """
        Safely shut down DS1120A probe.

        Returns probe to safe idle state and closes communication.
        """
        if self._armed:
            self.disarm()

        # TODO: Close hardware connection
        self._initialized = False
        print("✓ DS1120A shutdown")

    def __repr__(self) -> str:
        return (
            f"DS1120ADriver(voltage={self._voltage_v}V, "
            f"pulse_width={self._pulse_width_ns}ns, "
            f"armed={self._armed})"
        )
