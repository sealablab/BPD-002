"""
BPD Framework Quick Start Example

Demonstrates basic usage of BPD with DS1120A probe and Moku Go platform.
"""

from bpd_drivers import DS1120ADriver
from bpd_core import validate_probe_moku_compatibility, ProbeRegistry
from moku_models import MOKU_GO_PLATFORM


def main():
    print("=== BPD Framework Quick Start ===\n")

    # 1. Create driver for DS1120A probe
    print("1. Creating DS1120A driver...")
    driver = DS1120ADriver()
    print(f"   Driver created: {driver}\n")

    # 2. Initialize probe
    print("2. Initializing probe...")
    driver.initialize()
    print(f"   Capabilities: {driver.capabilities}\n")

    # 3. Validate compatibility with Moku Go
    print("3. Validating Moku Go compatibility...")
    validate_probe_moku_compatibility(
        driver,
        MOKU_GO_PLATFORM,
        output_id="OUT1",  # Using Moku Go OUT1
    )
    print("   ✓ Probe compatible with Moku Go\n")

    # 4. Configure probe parameters
    print("4. Configuring probe...")
    driver.set_voltage(3.3)  # 3.3V TTL level
    driver.set_pulse_width(100)  # 100ns pulse
    print("   ✓ Voltage: 3.3V")
    print("   ✓ Pulse width: 100ns\n")

    # 5. Arm probe
    print("5. Arming probe...")
    driver.arm()
    status = driver.get_status()
    print(f"   Status: {status}\n")

    # 6. Trigger probe (software trigger for demo)
    print("6. Triggering probe...")
    driver.trigger()
    print("   ✓ Probe triggered!\n")

    # 7. Check final status
    print("7. Final status:")
    final_status = driver.get_status()
    for key, value in final_status.items():
        print(f"   {key}: {value}")

    # 8. Disarm and shutdown
    print("\n8. Shutting down...")
    driver.disarm()
    driver.shutdown()
    print("   ✓ Probe safely shut down\n")

    # 9. Show registered drivers
    print("9. Available drivers in registry:")
    for driver_name in ProbeRegistry.list_drivers():
        print(f"   - {driver_name}")

    print("\n=== Quick Start Complete ===")


if __name__ == "__main__":
    main()
