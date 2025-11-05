"""
Basic Probe Driver - Complete Register Example

Demonstrates all 13 register fields from basic_probe_driver.yaml:
- Arming & lifecycle control
- Output drive parameters (trigger + intensity)
- Probe monitoring configuration

This example shows the Python layer aligned with the YAML spec.
Hardware implementation (VHDL FSM) will be added in Phase P2.
"""

from bpd_core import BasicProbeDriverRegisters
from bpd_core.validation import mV_to_volts, ns_to_cycles, us_to_cycles


def main():
    print("=" * 70)
    print("Basic Probe Driver - Complete Register Configuration")
    print("=" * 70)
    print()

    # Create register interface
    regs = BasicProbeDriverRegisters()
    print(f"✓ Registers initialized with YAML defaults")
    print(f"  {regs}")
    print()

    # =========================================================================
    # Section 1: Arming & Lifecycle Configuration
    # =========================================================================
    print("1. Arming & Lifecycle Configuration")
    print("-" * 70)

    # Set timeout for ARMED state (max wait for trigger)
    regs.trigger_wait_timeout = 10  # seconds
    print(f"   trigger_wait_timeout = {regs.trigger_wait_timeout}s")
    print(f"     (Max time to wait in ARMED before timeout)")

    # Enable auto-rearm for burst mode (default: False for safety)
    regs.auto_rearm_enable = False
    print(f"   auto_rearm_enable = {regs.auto_rearm_enable}")
    print(f"     (If True: auto-rearm after cooldown; False: one-shot)")

    # Fault clear (write 1 to acknowledge and clear faults)
    regs.fault_clear = False
    print(f"   fault_clear = {regs.fault_clear}")
    print(f"     (Write True to clear sticky fault state)")
    print()

    # =========================================================================
    # Section 2: Output Drive Controls
    # =========================================================================
    print("2. Output Drive Controls")
    print("-" * 70)

    # Trigger output configuration
    regs.trig_out_voltage = 3300  # 3.3V TTL level
    regs.trig_out_duration = 100  # 100ns pulse
    print(f"   Trigger Output:")
    print(f"     trig_out_voltage = {regs.trig_out_voltage} mV ({mV_to_volts(regs.trig_out_voltage)}V)")
    print(f"     trig_out_duration = {regs.trig_out_duration} ns ({ns_to_cycles(regs.trig_out_duration)} cycles @ 125MHz)")

    # Intensity/power output configuration
    regs.intensity_voltage = 2500  # 2.5V for probe power
    regs.intensity_duration = 500  # 500ns intensity pulse
    print(f"   Intensity/Power Output:")
    print(f"     intensity_voltage = {regs.intensity_voltage} mV ({mV_to_volts(regs.intensity_voltage)}V)")
    print(f"     intensity_duration = {regs.intensity_duration} ns ({ns_to_cycles(regs.intensity_duration)} cycles @ 125MHz)")

    # Cooldown between pulses (thermal safety)
    regs.cooldown_interval = 1000  # 1000μs = 1ms
    print(f"   Cooldown:")
    print(f"     cooldown_interval = {regs.cooldown_interval} μs ({us_to_cycles(regs.cooldown_interval)} cycles @ 125MHz)")
    print(f"     (Enforced delay between pulses for thermal safety)")
    print()

    # =========================================================================
    # Section 3: Probe Monitoring Configuration
    # =========================================================================
    print("3. Probe Monitoring Configuration")
    print("-" * 70)

    # Enable monitoring
    regs.monitor_enable = True
    print(f"   monitor_enable = {regs.monitor_enable}")
    print(f"     (Enable threshold checking on probe feedback)")

    # Threshold voltage (what voltage indicates "probe fired")
    regs.monitor_threshold_voltage = -300  # -300mV threshold
    regs.monitor_expect_negative = True  # Negative-going = fired
    print(f"   Threshold:")
    print(f"     monitor_threshold_voltage = {regs.monitor_threshold_voltage} mV")
    print(f"     monitor_expect_negative = {regs.monitor_expect_negative}")
    print(f"     (Negative-going crossing indicates probe fired)")

    # Monitoring window (when to check for threshold crossing)
    regs.monitor_window_start = 50  # Start monitoring 50ns after trigger
    regs.monitor_window_duration = 10000  # Monitor for 10μs
    print(f"   Monitoring Window:")
    print(f"     monitor_window_start = {regs.monitor_window_start} ns")
    print(f"     monitor_window_duration = {regs.monitor_window_duration} ns")
    print(f"     (Check threshold from {regs.monitor_window_start}ns to "
          f"{regs.monitor_window_start + regs.monitor_window_duration}ns after trigger)")

    # Read-only feedback (would be updated by hardware)
    print(f"   Current Feedback (read-only):")
    print(f"     probe_monitor_feedback = {regs.probe_monitor_feedback} mV")
    print(f"     (Hardware updates this register with ADC reading)")
    print()

    # =========================================================================
    # Section 4: Validation Examples
    # =========================================================================
    print("4. Validation Examples")
    print("-" * 70)

    # Show validation working
    try:
        print("   Testing validation: Setting invalid voltage...")
        regs.trig_out_voltage = 10000  # Out of range!
    except ValueError as e:
        print(f"   ✓ Validation caught error: {e}")

    try:
        print("   Testing validation: Setting invalid duration...")
        regs.trig_out_duration = 100000  # Out of range!
    except ValueError as e:
        print(f"   ✓ Validation caught error: {e}")

    try:
        print("   Testing validation: Setting invalid timeout...")
        regs.trigger_wait_timeout = 5000  # Out of range!
    except ValueError as e:
        print(f"   ✓ Validation caught error: {e}")

    print()

    # =========================================================================
    # Section 5: Export Configuration
    # =========================================================================
    print("5. Complete Register Dump")
    print("-" * 70)

    config = regs.to_dict()
    print("   All 13 register fields:")
    for field, value in config.items():
        print(f"     {field:30s} = {value}")

    print()
    print("=" * 70)
    print("✓ All 13 YAML register fields demonstrated")
    print("  Next: Phase P2 will implement VHDL FSM using these registers")
    print("=" * 70)


if __name__ == "__main__":
    main()
