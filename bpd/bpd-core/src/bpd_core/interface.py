"""
Generic FI probe driver interface.

Defines the abstract protocol that all probe-specific drivers must implement.
Design is inspired by Riscure DS1120A (de facto standard) but vendor-agnostic.
"""

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable
from pydantic import BaseModel, Field


class ProbeCapabilities(BaseModel):
    """Hardware capabilities of an FI probe."""

    # Voltage specifications
    min_voltage_v: float = Field(description="Minimum output voltage (volts)")
    max_voltage_v: float = Field(description="Maximum output voltage (volts)")

    # Timing specifications
    min_pulse_width_ns: int = Field(description="Minimum pulse width (nanoseconds)")
    max_pulse_width_ns: int = Field(description="Maximum pulse width (nanoseconds)")
    pulse_width_resolution_ns: int = Field(description="Pulse width step size (ns)")

    # Triggering
    supports_external_trigger: bool = Field(default=True, description="Accepts external trigger")
    supports_internal_trigger: bool = Field(default=False, description="Has internal trigger generator")

    # Advanced features
    supports_voltage_sweep: bool = Field(default=False, description="Can sweep voltage automatically")
    supports_pulse_train: bool = Field(default=False, description="Can generate pulse trains")


@runtime_checkable
class FIProbeInterface(Protocol):
    """
    Abstract interface for fault injection probe drivers.

    All probe-specific drivers (DS1120A, laser FI, etc.) must implement this protocol.
    Inspired by Riscure DS1120A control interface but designed to be vendor-agnostic.
    """

    @property
    @abstractmethod
    def capabilities(self) -> ProbeCapabilities:
        """Get probe hardware capabilities."""
        ...

    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize probe hardware.

        Should perform:
        - Hardware self-test
        - Set safe default parameters
        - Verify Moku platform compatibility

        Raises:
            RuntimeError: If initialization fails
        """
        ...

    @abstractmethod
    def set_voltage(self, voltage_v: float) -> None:
        """
        Set probe output voltage.

        Args:
            voltage_v: Voltage in volts

        Raises:
            ValueError: If voltage out of probe's supported range
        """
        ...

    @abstractmethod
    def set_pulse_width(self, width_ns: int) -> None:
        """
        Set fault injection pulse width.

        Args:
            width_ns: Pulse width in nanoseconds

        Raises:
            ValueError: If width out of probe's supported range
        """
        ...

    @abstractmethod
    def arm(self) -> None:
        """
        Arm the probe for triggering.

        After arming, probe will fire on next trigger event.
        """
        ...

    @abstractmethod
    def trigger(self) -> None:
        """
        Manually trigger fault injection pulse (if probe supports manual trigger).

        Raises:
            RuntimeError: If probe not armed or doesn't support manual trigger
        """
        ...

    @abstractmethod
    def disarm(self) -> None:
        """
        Disarm the probe (safe state).

        After disarming, probe will not respond to triggers.
        """
        ...

    @abstractmethod
    def get_status(self) -> dict:
        """
        Get current probe status.

        Returns:
            Dictionary with keys:
            - armed: bool
            - ready: bool
            - fault: bool (any hardware fault)
            - last_trigger_time: float (seconds since arm)
        """
        ...

    @abstractmethod
    def shutdown(self) -> None:
        """
        Safely shut down probe hardware.

        Should return probe to safe idle state.
        """
        ...


class BaseFIProbeDriver(ABC):
    """
    Abstract base class for FI probe drivers (alternative to Protocol).

    Use this if you want concrete implementation helpers and inheritance.
    Use FIProbeInterface (Protocol) if you want duck typing and flexibility.
    """

    def __init__(self):
        self._armed = False

    @property
    @abstractmethod
    def capabilities(self) -> ProbeCapabilities:
        """Get probe hardware capabilities."""
        pass

    @abstractmethod
    def initialize(self) -> None:
        """Initialize probe hardware."""
        pass

    @abstractmethod
    def set_voltage(self, voltage_v: float) -> None:
        """Set probe output voltage."""
        pass

    @abstractmethod
    def set_pulse_width(self, width_ns: int) -> None:
        """Set fault injection pulse width."""
        pass

    def arm(self) -> None:
        """Arm the probe for triggering."""
        self._armed = True

    def disarm(self) -> None:
        """Disarm the probe (safe state)."""
        self._armed = False

    @abstractmethod
    def trigger(self) -> None:
        """Manually trigger fault injection pulse."""
        pass

    @abstractmethod
    def get_status(self) -> dict:
        """Get current probe status."""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Safely shut down probe hardware."""
        pass
