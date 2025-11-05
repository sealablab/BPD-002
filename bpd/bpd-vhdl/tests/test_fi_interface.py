"""
CocoTB tests for fi_probe_interface.vhd

Tests the vendor-agnostic FI probe VHDL interface.
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer, ClockCycles


@cocotb.test()
async def test_basic_trigger_sequence(dut):
    """Test basic arm → trigger → pulse sequence."""

    # Start clock
    clock = Clock(dut.clk, 10, units="ns")  # 100MHz
    cocotb.start_soon(clock.start())

    # Reset
    dut.rst_n.value = 0
    dut.arm.value = 0
    dut.trigger_in.value = 0
    dut.pulse_width.value = 100  # 100ns pulse
    dut.voltage_level.value = 0x1000  # Some voltage level
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

    # Should be in IDLE, not ready
    assert dut.ready.value == 0, "Should not be ready when not armed"
    assert dut.busy.value == 0, "Should not be busy in idle"

    # Arm the probe
    dut.arm.value = 1
    await ClockCycles(dut.clk, 2)
    assert dut.ready.value == 1, "Should be ready after arming"
    assert dut.busy.value == 0, "Should not be busy when armed"

    # Trigger the probe
    dut.trigger_in.value = 1
    await RisingEdge(dut.clk)
    dut.trigger_in.value = 0

    # Should see probe_trigger pulse
    await RisingEdge(dut.clk)
    assert dut.probe_trigger.value == 1, "Probe trigger should pulse"
    assert dut.busy.value == 1, "Should be busy during pulse"
    assert dut.ready.value == 0, "Should not be ready during pulse"

    # Wait for pulse to complete (100 cycles)
    await ClockCycles(dut.clk, 101)
    assert dut.probe_pulse_ctrl.value == 0, "Pulse should be complete"

    # Wait for cooldown
    await ClockCycles(dut.clk, 260)  # Cooldown + margin
    assert dut.busy.value == 0, "Should not be busy after cooldown"
    assert dut.ready.value == 1, "Should be ready again after cooldown"


@cocotb.test()
async def test_disarm_during_pulse(dut):
    """Test that disarming during pulse is safe."""

    # Start clock
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.rst_n.value = 0
    dut.arm.value = 0
    dut.trigger_in.value = 0
    dut.pulse_width.value = 1000  # Long pulse
    dut.voltage_level.value = 0x1000
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

    # Arm and trigger
    dut.arm.value = 1
    await ClockCycles(dut.clk, 2)
    dut.trigger_in.value = 1
    await RisingEdge(dut.clk)
    dut.trigger_in.value = 0
    await ClockCycles(dut.clk, 10)

    # Should be in pulse
    assert dut.busy.value == 1, "Should be busy during pulse"

    # Disarm during pulse (this should be safe - pulse continues)
    dut.arm.value = 0
    await ClockCycles(dut.clk, 5)

    # Pulse should continue even though disarmed
    # (Design decision: pulse completes safely even if disarmed)


@cocotb.test()
async def test_no_trigger_when_not_armed(dut):
    """Test that trigger is ignored when not armed."""

    # Start clock
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.rst_n.value = 0
    dut.arm.value = 0
    dut.trigger_in.value = 0
    dut.pulse_width.value = 100
    dut.voltage_level.value = 0x1000
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

    # Try to trigger without arming
    dut.trigger_in.value = 1
    await RisingEdge(dut.clk)
    dut.trigger_in.value = 0
    await ClockCycles(dut.clk, 5)

    # Should not trigger
    assert dut.probe_trigger.value == 0, "Should not trigger when not armed"
    assert dut.busy.value == 0, "Should not be busy"


@cocotb.test()
async def test_voltage_update(dut):
    """Test that voltage level can be updated while armed."""

    # Start clock
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.rst_n.value = 0
    dut.arm.value = 0
    dut.trigger_in.value = 0
    dut.pulse_width.value = 100
    dut.voltage_level.value = 0x1000
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

    # Arm the probe
    dut.arm.value = 1
    await ClockCycles(dut.clk, 2)

    # Change voltage while armed
    dut.voltage_level.value = 0x2000
    await ClockCycles(dut.clk, 2)

    # Voltage output should update
    assert dut.probe_voltage.value == 0x2000, "Voltage should update while armed"
