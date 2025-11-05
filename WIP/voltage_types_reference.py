"""
Voltage Type System - Python Reference Implementation

Type-safe voltage domain classes that mirror forge-vhdl voltage packages.
Designed for clarity and type-checking at assignment, not rich semantics.

Design Principles:
1. Units cannot detach from type (no naked float voltages)
2. Type-checking at assignment (Python type system + runtime validation)
3. Explicit conversions only (no arithmetic that loses unit information)
4. 1:1 mapping with VHDL packages (forge_voltage_*_pkg.vhd)

Usage:
    from voltage_types import Voltage_3V3, Voltage_5V_Bipolar

    # Type-safe assignment
    trigger = Voltage_3V3(2.5)              # OK
    dac = Voltage_5V_Bipolar(-3.0)          # OK

    # Type mismatch caught by mypy
    trigger = dac  # Type error!

    # Range validation at runtime
    bad = Voltage_3V3(5.0)  # ValueError!

    # Explicit conversion to digital
    trigger_digital = trigger.to_digital()  # int for register write

Mirrors VHDL packages:
- Voltage_3V3         → forge_voltage_3v3_pkg.vhd
- Voltage_5V0         → forge_voltage_5v0_pkg.vhd
- Voltage_5V_Bipolar  → forge_voltage_5v_bipolar_pkg.vhd

Version: 1.0
Date: 2025-11-04
Repository: TBD (see VOLTAGE_TYPE_SYSTEM_DESIGN.md for placement options)
"""

from typing import Final


class Voltage_3V3:
    """0-3.3V unipolar voltage domain (TTL/digital logic).

    Mirrors: forge_voltage_3v3_pkg.vhd
    Use for: GPIO, TTL probe interfaces, digital glitch, 3.3V I/O

    Type-safe wrapper ensuring voltage values cannot detach from unit.
    Prevents mixing voltage domains via Python type checking.

    Examples:
        >>> trigger = Voltage_3V3(2.5)
        >>> trigger.volts
        2.5
        >>> trigger.to_digital()
        24812
        >>> Voltage_3V3.from_digital(24812)
        Voltage_3V3(2.5V)
        >>> Voltage_3V3(5.0)  # Out of range
        ValueError: Voltage 5.0V out of range for Voltage_3V3 [0.0, 3.3]V
    """

    V_MIN: Final[float] = 0.0
    V_MAX: Final[float] = 3.3
    SCALE_FACTOR: Final[float] = 32767.0 / 3.3  # ~9930.0 digital units per volt

    def __init__(self, volts: float):
        """Create voltage value in 0-3.3V domain.

        Args:
            volts: Voltage value in volts

        Raises:
            ValueError: If voltage out of range [0.0, 3.3]V
        """
        if not (self.V_MIN <= volts <= self.V_MAX):
            raise ValueError(
                f"Voltage {volts}V out of range for Voltage_3V3 "
                f"[{self.V_MIN}, {self.V_MAX}]V"
            )
        self._volts = volts

    @property
    def volts(self) -> float:
        """Get voltage value in volts (read-only to prevent detachment)."""
        return self._volts

    def to_digital(self) -> int:
        """Convert to 16-bit signed digital value (mirrors VHDL to_digital).

        Returns:
            Digital value in range [0, 32767] for 16-bit signed representation
        """
        digital = int(self._volts * self.SCALE_FACTOR + 0.5)  # Round to nearest
        return max(0, min(32767, digital))  # Clamp to valid range

    @classmethod
    def from_digital(cls, digital: int) -> 'Voltage_3V3':
        """Create from 16-bit signed digital value (mirrors VHDL from_digital).

        Args:
            digital: Digital value in range [0, 32767]

        Returns:
            Voltage_3V3 instance

        Raises:
            ValueError: If resulting voltage out of range
        """
        volts = digital / cls.SCALE_FACTOR
        return cls(volts)  # Validates range via __init__

    def __repr__(self) -> str:
        return f"Voltage_3V3({self._volts}V)"

    def __str__(self) -> str:
        return f"{self._volts}V (0-3.3V domain)"

    # Prevent arithmetic operations (units would detach)
    def __add__(self, other):
        raise TypeError(
            "Cannot add Voltage_3V3 (units would detach). "
            "Use explicit conversions if cross-domain math needed."
        )

    def __sub__(self, other):
        raise TypeError(
            "Cannot subtract Voltage_3V3 (units would detach). "
            "Use explicit conversions if cross-domain math needed."
        )

    def __mul__(self, other):
        raise TypeError(
            "Cannot multiply Voltage_3V3 (units would detach). "
            "Use explicit conversions if scaling needed."
        )

    def __truediv__(self, other):
        raise TypeError(
            "Cannot divide Voltage_3V3 (units would detach). "
            "Use explicit conversions if scaling needed."
        )


class Voltage_5V0:
    """0-5.0V unipolar voltage domain (unipolar supply).

    Mirrors: forge_voltage_5v0_pkg.vhd
    Use for: 0-5V DAC outputs, sensor power, unipolar analog

    Type-safe wrapper ensuring voltage values cannot detach from unit.
    Prevents mixing voltage domains via Python type checking.

    Examples:
        >>> supply = Voltage_5V0(3.3)
        >>> supply.volts
        3.3
        >>> supply.to_digital()
        21627
        >>> Voltage_5V0.from_digital(21627)
        Voltage_5V0(3.3V)
    """

    V_MIN: Final[float] = 0.0
    V_MAX: Final[float] = 5.0
    SCALE_FACTOR: Final[float] = 32767.0 / 5.0  # 6553.4 digital units per volt

    def __init__(self, volts: float):
        """Create voltage value in 0-5.0V domain.

        Args:
            volts: Voltage value in volts

        Raises:
            ValueError: If voltage out of range [0.0, 5.0]V
        """
        if not (self.V_MIN <= volts <= self.V_MAX):
            raise ValueError(
                f"Voltage {volts}V out of range for Voltage_5V0 "
                f"[{self.V_MIN}, {self.V_MAX}]V"
            )
        self._volts = volts

    @property
    def volts(self) -> float:
        """Get voltage value in volts (read-only to prevent detachment)."""
        return self._volts

    def to_digital(self) -> int:
        """Convert to 16-bit signed digital value (mirrors VHDL to_digital).

        Returns:
            Digital value in range [0, 32767] for 16-bit signed representation
        """
        digital = int(self._volts * self.SCALE_FACTOR + 0.5)  # Round to nearest
        return max(0, min(32767, digital))  # Clamp to valid range

    @classmethod
    def from_digital(cls, digital: int) -> 'Voltage_5V0':
        """Create from 16-bit signed digital value (mirrors VHDL from_digital).

        Args:
            digital: Digital value in range [0, 32767]

        Returns:
            Voltage_5V0 instance

        Raises:
            ValueError: If resulting voltage out of range
        """
        volts = digital / cls.SCALE_FACTOR
        return cls(volts)  # Validates range via __init__

    def __repr__(self) -> str:
        return f"Voltage_5V0({self._volts}V)"

    def __str__(self) -> str:
        return f"{self._volts}V (0-5.0V domain)"

    # Prevent arithmetic operations (units would detach)
    def __add__(self, other):
        raise TypeError("Cannot add Voltage_5V0 (units would detach).")

    def __sub__(self, other):
        raise TypeError("Cannot subtract Voltage_5V0 (units would detach).")

    def __mul__(self, other):
        raise TypeError("Cannot multiply Voltage_5V0 (units would detach).")

    def __truediv__(self, other):
        raise TypeError("Cannot divide Voltage_5V0 (units would detach).")


class Voltage_5V_Bipolar:
    """±5.0V bipolar voltage domain (AC/bipolar signals).

    Mirrors: forge_voltage_5v_bipolar_pkg.vhd
    Use for: Moku DAC/ADC, AC signals, most analog work

    Type-safe wrapper ensuring voltage values cannot detach from unit.
    Prevents mixing voltage domains via Python type checking.

    Examples:
        >>> dac = Voltage_5V_Bipolar(-3.0)
        >>> dac.volts
        -3.0
        >>> dac.to_digital()
        -19661
        >>> Voltage_5V_Bipolar.from_digital(-19661)
        Voltage_5V_Bipolar(-3.0V)
        >>> Voltage_5V_Bipolar(6.0)  # Out of range
        ValueError: Voltage 6.0V out of range for Voltage_5V_Bipolar [-5.0, 5.0]V
    """

    V_MIN: Final[float] = -5.0
    V_MAX: Final[float] = 5.0
    SCALE_FACTOR: Final[float] = 32767.0 / 5.0  # 6553.4 digital units per volt

    def __init__(self, volts: float):
        """Create voltage value in ±5.0V domain.

        Args:
            volts: Voltage value in volts

        Raises:
            ValueError: If voltage out of range [-5.0, 5.0]V
        """
        if not (self.V_MIN <= volts <= self.V_MAX):
            raise ValueError(
                f"Voltage {volts}V out of range for Voltage_5V_Bipolar "
                f"[{self.V_MIN}, {self.V_MAX}]V"
            )
        self._volts = volts

    @property
    def volts(self) -> float:
        """Get voltage value in volts (read-only to prevent detachment)."""
        return self._volts

    def to_digital(self) -> int:
        """Convert to 16-bit signed digital value (mirrors VHDL to_digital).

        Returns:
            Digital value in range [-32768, 32767] for 16-bit signed representation
        """
        digital = int(self._volts * self.SCALE_FACTOR + (0.5 if self._volts >= 0 else -0.5))
        return max(-32768, min(32767, digital))  # Clamp to valid range

    @classmethod
    def from_digital(cls, digital: int) -> 'Voltage_5V_Bipolar':
        """Create from 16-bit signed digital value (mirrors VHDL from_digital).

        Args:
            digital: Digital value in range [-32768, 32767]

        Returns:
            Voltage_5V_Bipolar instance

        Raises:
            ValueError: If resulting voltage out of range
        """
        volts = digital / cls.SCALE_FACTOR
        return cls(volts)  # Validates range via __init__

    def __repr__(self) -> str:
        return f"Voltage_5V_Bipolar({self._volts}V)"

    def __str__(self) -> str:
        return f"{self._volts}V (±5.0V domain)"

    # Prevent arithmetic operations (units would detach)
    def __add__(self, other):
        raise TypeError("Cannot add Voltage_5V_Bipolar (units would detach).")

    def __sub__(self, other):
        raise TypeError("Cannot subtract Voltage_5V_Bipolar (units would detach).")

    def __mul__(self, other):
        raise TypeError("Cannot multiply Voltage_5V_Bipolar (units would detach).")

    def __truediv__(self, other):
        raise TypeError("Cannot divide Voltage_5V_Bipolar (units would detach).")


# Type checking example (for mypy/pyright)
def set_trigger_voltage(voltage: Voltage_3V3) -> None:
    """Example function that accepts only 3.3V domain voltages.

    Type checker will catch if you pass Voltage_5V0 or Voltage_5V_Bipolar.
    """
    digital_value = voltage.to_digital()
    print(f"Setting trigger to {voltage} (digital: {digital_value})")


def set_dac_voltage(voltage: Voltage_5V_Bipolar) -> None:
    """Example function that accepts only ±5V bipolar voltages.

    Type checker will catch if you pass Voltage_3V3 or Voltage_5V0.
    """
    digital_value = voltage.to_digital()
    print(f"Setting DAC to {voltage} (digital: {digital_value})")


if __name__ == "__main__":
    # Demonstration of type safety
    print("=== Voltage Type System Demo ===\n")

    # Create voltages in different domains
    trigger = Voltage_3V3(2.5)
    supply = Voltage_5V0(3.3)
    dac = Voltage_5V_Bipolar(-3.0)

    print(f"Trigger: {trigger}")
    print(f"Supply: {supply}")
    print(f"DAC: {dac}\n")

    # Digital conversion
    print(f"Trigger digital: {trigger.to_digital()}")
    print(f"Supply digital: {supply.to_digital()}")
    print(f"DAC digital: {dac.to_digital()}\n")

    # Type-safe function calls
    set_trigger_voltage(trigger)  # OK
    set_dac_voltage(dac)  # OK

    # These would be caught by type checker:
    # set_trigger_voltage(dac)  # Type error!
    # set_dac_voltage(supply)   # Type error!

    # Range validation
    try:
        bad = Voltage_3V3(5.0)
    except ValueError as e:
        print(f"\nRange validation: {e}")

    # Arithmetic prevention
    try:
        result = trigger + dac
    except TypeError as e:
        print(f"Arithmetic prevention: {e}")
