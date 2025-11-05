"""
Probe driver registry for dynamic discovery and loading.

Allows applications to discover available probe drivers at runtime.
"""

from typing import Dict, Type, Optional
from bpd_core.interface import FIProbeInterface


class ProbeRegistry:
    """
    Registry for probe driver implementations.

    Allows dynamic discovery of available probe drivers without
    hardcoding dependencies on specific implementations.
    """

    _drivers: Dict[str, Type[FIProbeInterface]] = {}

    @classmethod
    def register(cls, name: str, driver_class: Type[FIProbeInterface]) -> None:
        """
        Register a probe driver implementation.

        Args:
            name: Human-readable probe name (e.g., "ds1120a", "laser_fi")
            driver_class: Driver class implementing FIProbeInterface

        Example:
            >>> ProbeRegistry.register("ds1120a", DS1120ADriver)
        """
        cls._drivers[name.lower()] = driver_class

    @classmethod
    def get_driver(cls, name: str) -> Optional[Type[FIProbeInterface]]:
        """
        Get registered probe driver by name.

        Args:
            name: Probe name (case-insensitive)

        Returns:
            Driver class or None if not found
        """
        return cls._drivers.get(name.lower())

    @classmethod
    def list_drivers(cls) -> list[str]:
        """
        List all registered probe drivers.

        Returns:
            List of probe names
        """
        return list(cls._drivers.keys())

    @classmethod
    def clear(cls) -> None:
        """Clear registry (mainly for testing)."""
        cls._drivers.clear()


def register_driver(name: str):
    """
    Decorator to auto-register probe driver classes.

    Example:
        >>> @register_driver("ds1120a")
        >>> class DS1120ADriver:
        >>>     ...
    """

    def decorator(driver_class: Type[FIProbeInterface]):
        ProbeRegistry.register(name, driver_class)
        return driver_class

    return decorator
