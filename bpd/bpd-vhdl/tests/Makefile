# CocoTB Makefile for Basic Probe Driver FSM
# Progressive testing: P1 (sanity) → P2 (behavior) → P3 (integration)

# VHDL files to compile (in dependency order)
VHDL_SOURCES = $(PWD)/../src/basic_app_types_pkg.vhd \
               $(PWD)/../src/basic_app_voltage_pkg.vhd \
               $(PWD)/../src/basic_app_time_pkg.vhd \
               $(PWD)/../src/basic_probe_driver_custom_inst_main.vhd

# DUT (top-level entity)
TOPLEVEL = basic_probe_driver_custom_inst_main

# Test module
MODULE = test_basic_probe_fsm

# Simulator
SIM = ghdl

# GHDL flags
GHDL_ARGS = --std=08 --ieee=synopsys

# GHDL executable path (if not in PATH)
# Uncomment if needed:
# GHDL_BIN = /usr/local/bin/ghdl

# CocoTB settings
COCOTB_REDUCED_LOG_FMT = True
COCOTB_LOG_LEVEL = INFO

# Include CocoTB makefile
include $(shell cocotb-config --makefiles)/Makefile.sim

# Custom targets
.PHONY: clean_all test_p1 test_p2 test_p3 compile_only

# Clean everything including GHDL work files
clean_all: clean
	rm -rf *.cf *.vcd *.ghw work-obj*.cf

# Run only P1 tests (basic sanity)
test_p1:
	pytest test_basic_probe_fsm.py::test_p1_reset_behavior \
	       test_basic_probe_fsm.py::test_p1_clock_toggles \
	       test_basic_probe_fsm.py::test_p1_global_enable \
	       -v

# Run P2 tests (will show BLOCKED status)
test_p2:
	pytest test_basic_probe_fsm.py -k p2 -v

# Run P3 tests (will show BLOCKED status)
test_p3:
	pytest test_basic_probe_fsm.py -k p3 -v

# Just compile VHDL without running tests
compile_only:
	ghdl -a $(GHDL_ARGS) $(VHDL_SOURCES)
	ghdl -e $(GHDL_ARGS) $(TOPLEVEL)
	@echo "✅ Compilation successful!"

# Help target
help:
	@echo "CocoTB Test Makefile for Basic Probe Driver FSM"
	@echo ""
	@echo "Targets:"
	@echo "  make              - Run all CocoTB tests"
	@echo "  make test_p1      - Run P1 (sanity) tests only"
	@echo "  make test_p2      - Run P2 (behavior) tests (currently BLOCKED)"
	@echo "  make test_p3      - Run P3 (integration) tests (currently BLOCKED)"
	@echo "  make compile_only - Compile VHDL without running tests"
	@echo "  make clean        - Remove CocoTB build artifacts"
	@echo "  make clean_all    - Remove all build artifacts including GHDL files"
	@echo "  make help         - Show this help message"
	@echo ""
	@echo "Test Status:"
	@echo "  P1: ✅ PASS - Basic reset, clock, and register tests"
	@echo "  P2: ⚠️  BLOCKED - Missing arm_enable and ext_trigger_in ports"
	@echo "  P3: ⚠️  BLOCKED - Missing arm_enable and ext_trigger_in ports"
	@echo ""
	@echo "Next Steps:"
	@echo "  1. Add arm_enable input port to FSM entity"
	@echo "  2. Add ext_trigger_in input port to FSM entity"
	@echo "  3. Update IDLE → ARMED transition logic"
	@echo "  4. Update ARMED → FIRING transition logic"
	@echo "  5. Re-run tests with 'make' to verify P2 and P3"
