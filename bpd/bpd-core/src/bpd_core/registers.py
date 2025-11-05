"""
Basic Probe Driver register definitions.

This module defines the register interface for the Basic Probe Driver,
aligned with bpd/bpd-specs/basic_probe_driver.yaml (13 register fields).

All units match the YAML spec:
- Voltages in millivolts (mV)
- Time in nanoseconds (ns), microseconds (μs), or seconds (s)
- Defaults match YAML default_value
"""

from typing import Optional


class BasicProbeDriverRegisters:
    """
    Register interface for Basic Probe Driver.

    Implements all 13 register fields from basic_probe_driver.yaml:
    - 3 arming & lifecycle fields
    - 5 output drive control fields
    - 5 probe monitoring fields (+ 1 read-only feedback)

    All voltage values are in millivolts (mV).
    All timing values preserve units from YAML (ns, μs, s).
    """

    def __init__(self):
        """Initialize all registers with YAML default values."""
        # Arming & Lifecycle (3 fields)
        self._trigger_wait_timeout: int = 2  # seconds (YAML default)
        self._auto_rearm_enable: bool = False  # YAML default
        self._fault_clear: bool = False  # YAML default

        # Output Drive Controls (5 fields)
        self._trig_out_voltage: int = 0  # mV (YAML default)
        self._trig_out_duration: int = 100  # ns (YAML default)
        self._intensity_voltage: int = 0  # mV (YAML default)
        self._intensity_duration: int = 200  # ns (YAML default)
        self._cooldown_interval: int = 10  # μs (YAML default)

        # Probe Monitoring (6 fields)
        self._probe_monitor_feedback: int = 0  # mV (read-only, YAML default)
        self._monitor_enable: bool = True  # YAML default
        self._monitor_threshold_voltage: int = -200  # mV (YAML default)
        self._monitor_expect_negative: bool = True  # YAML default
        self._monitor_window_start: int = 0  # ns (YAML default)
        self._monitor_window_duration: int = 5000  # ns (YAML default)

    # =========================================================================
    # Arming & Lifecycle (3 fields)
    # =========================================================================

    @property
    def trigger_wait_timeout(self) -> int:
        """
        Maximum time to wait in ARMED state before timing out.

        Units: seconds
        Range: 0-3600 (YAML: pulse_duration_s_u16)
        Default: 2
        """
        return self._trigger_wait_timeout

    @trigger_wait_timeout.setter
    def trigger_wait_timeout(self, value: int) -> None:
        if not 0 <= value <= 3600:
            raise ValueError(
                f"trigger_wait_timeout must be 0-3600 seconds, got {value}"
            )
        self._trigger_wait_timeout = value

    @property
    def auto_rearm_enable(self) -> bool:
        """
        When true, FSM re-enters ARMED after cooldown instead of idling.

        Type: boolean
        Default: False (one-shot semantics for safety)
        """
        return self._auto_rearm_enable

    @auto_rearm_enable.setter
    def auto_rearm_enable(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise TypeError(f"auto_rearm_enable must be bool, got {type(value)}")
        self._auto_rearm_enable = value

    @property
    def fault_clear(self) -> bool:
        """
        Write 1 to clear fault state and re-arm eligibility.

        Type: boolean
        Default: False
        Note: Sticky faults require acknowledgement
        """
        return self._fault_clear

    @fault_clear.setter
    def fault_clear(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise TypeError(f"fault_clear must be bool, got {type(value)}")
        self._fault_clear = value

    # =========================================================================
    # Output Drive Controls (5 fields)
    # =========================================================================

    @property
    def trig_out_voltage(self) -> int:
        """
        Output voltage level for the digital trigger line.

        Units: millivolts (mV)
        Range: -5000 to 5000 (±5V)
        Default: 0
        """
        return self._trig_out_voltage

    @trig_out_voltage.setter
    def trig_out_voltage(self, value: int) -> None:
        if not -5000 <= value <= 5000:
            raise ValueError(
                f"trig_out_voltage must be -5000 to 5000 mV, got {value}"
            )
        self._trig_out_voltage = value

    @property
    def trig_out_duration(self) -> int:
        """
        Duration of the trigger_out pulse.

        Units: nanoseconds (ns)
        Range: 20-50000
        Default: 100
        """
        return self._trig_out_duration

    @trig_out_duration.setter
    def trig_out_duration(self, value: int) -> None:
        if not 20 <= value <= 50000:
            raise ValueError(
                f"trig_out_duration must be 20-50000 ns, got {value}"
            )
        self._trig_out_duration = value

    @property
    def intensity_voltage(self) -> int:
        """
        Analog intensity/power control voltage delivered to the probe.

        Units: millivolts (mV)
        Range: -5000 to 5000 (±5V)
        Default: 0
        """
        return self._intensity_voltage

    @intensity_voltage.setter
    def intensity_voltage(self, value: int) -> None:
        if not -5000 <= value <= 5000:
            raise ValueError(
                f"intensity_voltage must be -5000 to 5000 mV, got {value}"
            )
        self._intensity_voltage = value

    @property
    def intensity_duration(self) -> int:
        """
        Duration of the intensity drive window.

        Units: nanoseconds (ns)
        Range: 20-50000
        Default: 200
        """
        return self._intensity_duration

    @intensity_duration.setter
    def intensity_duration(self, value: int) -> None:
        if not 20 <= value <= 50000:
            raise ValueError(
                f"intensity_duration must be 20-50000 ns, got {value}"
            )
        self._intensity_duration = value

    @property
    def cooldown_interval(self) -> int:
        """
        Cooldown dwell enforced between pulses.

        Units: microseconds (μs)
        Range: 1-500000 (24-bit, >16s span)
        Default: 10
        """
        return self._cooldown_interval

    @cooldown_interval.setter
    def cooldown_interval(self, value: int) -> None:
        if not 1 <= value <= 500000:
            raise ValueError(
                f"cooldown_interval must be 1-500000 μs, got {value}"
            )
        self._cooldown_interval = value

    # =========================================================================
    # Probe Monitoring (6 fields)
    # =========================================================================

    @property
    def probe_monitor_feedback(self) -> int:
        """
        Signed probe current monitor (mV); negative indicates rising current draw.

        Units: millivolts (mV)
        Range: -5000 to 5000
        Default: 0
        Note: READ-ONLY from hardware
        """
        return self._probe_monitor_feedback

    def _set_probe_monitor_feedback(self, value: int) -> None:
        """
        Internal method to update probe_monitor_feedback from hardware.

        Not exposed as a setter since this is a read-only register
        from the user's perspective.
        """
        if not -5000 <= value <= 5000:
            raise ValueError(
                f"probe_monitor_feedback must be -5000 to 5000 mV, got {value}"
            )
        self._probe_monitor_feedback = value

    @property
    def monitor_enable(self) -> bool:
        """
        Enable probe monitor threshold evaluation.

        Type: boolean
        Default: True
        Note: Gate the monitoring block; disable for probes lacking feedback
        """
        return self._monitor_enable

    @monitor_enable.setter
    def monitor_enable(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise TypeError(f"monitor_enable must be bool, got {type(value)}")
        self._monitor_enable = value

    @property
    def monitor_threshold_voltage(self) -> int:
        """
        Threshold (mV) the monitor must cross within the observation window.

        Units: millivolts (mV)
        Range: -5000 to 5000
        Default: -200
        """
        return self._monitor_threshold_voltage

    @monitor_threshold_voltage.setter
    def monitor_threshold_voltage(self, value: int) -> None:
        if not -5000 <= value <= 5000:
            raise ValueError(
                f"monitor_threshold_voltage must be -5000 to 5000 mV, got {value}"
            )
        self._monitor_threshold_voltage = value

    @property
    def monitor_expect_negative(self) -> bool:
        """
        True when a negative-going crossing counts as "probe fired".

        Type: boolean
        Default: True
        Note: Flip for probes that spike positive
        """
        return self._monitor_expect_negative

    @monitor_expect_negative.setter
    def monitor_expect_negative(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise TypeError(f"monitor_expect_negative must be bool, got {type(value)}")
        self._monitor_expect_negative = value

    @property
    def monitor_window_start(self) -> int:
        """
        Delay after trigger before monitoring window opens.

        Units: nanoseconds (ns)
        Range: 0-2000000000 (2 billion ns = 2 seconds)
        Default: 0
        """
        return self._monitor_window_start

    @monitor_window_start.setter
    def monitor_window_start(self, value: int) -> None:
        if not 0 <= value <= 2000000000:
            raise ValueError(
                f"monitor_window_start must be 0-2000000000 ns, got {value}"
            )
        self._monitor_window_start = value

    @property
    def monitor_window_duration(self) -> int:
        """
        Length of monitoring window starting at monitor_window_start.

        Units: nanoseconds (ns)
        Range: 100-2000000000 (2 billion ns = 2 seconds)
        Default: 5000
        """
        return self._monitor_window_duration

    @monitor_window_duration.setter
    def monitor_window_duration(self, value: int) -> None:
        if not 100 <= value <= 2000000000:
            raise ValueError(
                f"monitor_window_duration must be 100-2000000000 ns, got {value}"
            )
        self._monitor_window_duration = value

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def to_dict(self) -> dict:
        """
        Export all register values as dictionary.

        Useful for logging, debugging, or serialization.
        """
        return {
            # Arming & Lifecycle
            "trigger_wait_timeout": self._trigger_wait_timeout,
            "auto_rearm_enable": self._auto_rearm_enable,
            "fault_clear": self._fault_clear,
            # Output Drive Controls
            "trig_out_voltage": self._trig_out_voltage,
            "trig_out_duration": self._trig_out_duration,
            "intensity_voltage": self._intensity_voltage,
            "intensity_duration": self._intensity_duration,
            "cooldown_interval": self._cooldown_interval,
            # Probe Monitoring
            "probe_monitor_feedback": self._probe_monitor_feedback,
            "monitor_enable": self._monitor_enable,
            "monitor_threshold_voltage": self._monitor_threshold_voltage,
            "monitor_expect_negative": self._monitor_expect_negative,
            "monitor_window_start": self._monitor_window_start,
            "monitor_window_duration": self._monitor_window_duration,
        }

    def __repr__(self) -> str:
        """String representation showing key register values."""
        return (
            f"BasicProbeDriverRegisters("
            f"trig_out_voltage={self._trig_out_voltage}mV, "
            f"intensity_voltage={self._intensity_voltage}mV, "
            f"cooldown={self._cooldown_interval}μs, "
            f"monitor_enable={self._monitor_enable})"
        )
