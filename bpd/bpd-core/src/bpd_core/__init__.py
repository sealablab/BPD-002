"""
BPD Core - Generic probe driver framework for Moku platform.

This package provides abstract interfaces and utilities for building
probe drivers that work across multiple FI probe vendors.
"""

from bpd_core.interface import FIProbeInterface, ProbeCapabilities
from bpd_core.registry import ProbeRegistry, register_driver
from bpd_core.validation import validate_probe_moku_compatibility

__version__ = "0.1.0"

__all__ = [
    "FIProbeInterface",
    "ProbeCapabilities",
    "ProbeRegistry",
    "register_driver",
    "validate_probe_moku_compatibility",
]
