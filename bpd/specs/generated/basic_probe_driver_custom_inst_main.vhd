--------------------------------------------------------------------------------
-- File: basic_probe_driver_custom_inst_main.vhd
-- Generated: 2025-11-05 06:54:32
-- Generator: tools/generate_custom_inst_v2.py
-- Template Version: 2.0 (BasicAppDataTypes)
--
-- ⚠️  GENERATED TEMPLATE - CUSTOMIZE FOR YOUR APPLICATION ⚠️
-- This is a starting point template. Implement your application logic here.
--
-- Description:
--   Main application logic for basic_probe_driver.
--   Receives typed signals from shim, implements application behavior.
--
-- Platform: Moku:Go
-- Clock Frequency: 125 MHz
--
-- Application Signals (from register mapping):
--   trigger_wait_timeout: unsigned(15 downto 0) - Maximum time to wait in ARMED before timing out.
--   trig_out_voltage: signed(15 downto 0) - Output voltage level for the digital trigger line (mV).
--   trig_out_duration: unsigned(15 downto 0) - Duration of the trigger_out pulse.
--   intensity_voltage: signed(15 downto 0) - Analog intensity/power control voltage delivered to the probe (mV).
--   intensity_duration: unsigned(15 downto 0) - Duration of the intensity drive window.
--   cooldown_interval: unsigned(23 downto 0) - Cooldown dwell enforced between pulses.
--   auto_rearm_enable: std_logic - When true, FSM re-enters ARMED after cooldown instead of idling.
--   fault_clear: std_logic - Write 1 to clear fault state and re-arm eligibility.
--   probe_monitor_feedback: signed(15 downto 0) - Signed probe current monitor (mV); negative indicates rising current draw.
--   monitor_enable: std_logic - Enable probe monitor threshold evaluation.
--   monitor_threshold_voltage: signed(15 downto 0) - Threshold (mV) the monitor must cross within the observation window.
--   monitor_expect_negative: std_logic - True when a negative-going crossing counts as “probe fired”.
--   monitor_window_start: unsigned(31 downto 0) - Delay after trigger before monitoring window opens.
--   monitor_window_duration: unsigned(31 downto 0) - Length of monitoring window starting at monitor_window_start.
--
-- References:
--   - basic_probe_driver.yaml
--   - basic_probe_driver_custom_inst_shim.vhd (auto-generated register mapping)
--------------------------------------------------------------------------------

library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

library WORK;
use WORK.basic_app_types_pkg.all;
use WORK.basic_app_voltage_pkg.all;
use WORK.basic_app_time_pkg.all;
entity basic_probe_driver_custom_inst_main is
    generic (
        CLK_FREQ_HZ : integer := 125000000  -- Moku:Go clock frequency
    );
    port (
        ------------------------------------------------------------------------
        -- Clock and Reset
        ------------------------------------------------------------------------
        Clk                : in  std_logic;
        Reset              : in  std_logic;  -- Active-high reset
        global_enable      : in  std_logic;  -- Combined VOLO ready signals
        ready_for_updates  : out std_logic;  -- Handshake to shim

        ------------------------------------------------------------------------
        -- Application Signals (Typed - from BasicAppDataTypes)
        ------------------------------------------------------------------------
        trigger_wait_timeout : in unsigned(15 downto 0);        trig_out_voltage : in signed(15 downto 0);        trig_out_duration : in unsigned(15 downto 0);        intensity_voltage : in signed(15 downto 0);        intensity_duration : in unsigned(15 downto 0);        cooldown_interval : in unsigned(23 downto 0);        auto_rearm_enable : in std_logic;        fault_clear : in std_logic;        probe_monitor_feedback : in signed(15 downto 0);        monitor_enable : in std_logic;        monitor_threshold_voltage : in signed(15 downto 0);        monitor_expect_negative : in std_logic;        monitor_window_start : in unsigned(31 downto 0);        monitor_window_duration : in unsigned(31 downto 0)    );
end entity basic_probe_driver_custom_inst_main;

architecture rtl of basic_probe_driver_custom_inst_main is

    ----------------------------------------------------------------------------
    -- Internal Signals
    ----------------------------------------------------------------------------
    -- TODO: Add your application-specific signals here

    -- Example state machine (customize for your application)
    type state_t is (IDLE, ACTIVE, DONE);
    signal state : state_t;

    ----------------------------------------------------------------------------
    -- Time Conversion Signals (if needed for time-based datatypes)
    ----------------------------------------------------------------------------
    signal trigger_wait_timeout_cycles : unsigned(31 downto 0);  -- trigger_wait_timeout converted to clock cycles
    signal trig_out_duration_cycles : unsigned(31 downto 0);  -- trig_out_duration converted to clock cycles
    signal intensity_duration_cycles : unsigned(31 downto 0);  -- intensity_duration converted to clock cycles
    signal cooldown_interval_cycles : unsigned(31 downto 0);  -- cooldown_interval converted to clock cycles
    signal monitor_window_start_cycles : unsigned(31 downto 0);  -- monitor_window_start converted to clock cycles
    signal monitor_window_duration_cycles : unsigned(31 downto 0);  -- monitor_window_duration converted to clock cycles

begin

    ------------------------------------------------------------------------
    -- Ready for Updates
    --
    -- Drive this signal based on your application's update policy:
    --   '1' = Safe to update registers (typical: always ready)
    --   '0' = Hold current values (use during critical operations)
    ------------------------------------------------------------------------
    ready_for_updates <= '1';  -- TODO: Customize based on your application

    ------------------------------------------------------------------------
    -- Time to Cycles Conversions
    --
    -- Convert time durations to clock cycles using platform-aware functions
    ------------------------------------------------------------------------
    -- Convert trigger_wait_timeout (s) to clock cycles
    trigger_wait_timeout_cycles <= s_to_cycles(trigger_wait_timeout, CLK_FREQ_HZ);
    -- Convert trig_out_duration (ns) to clock cycles
    trig_out_duration_cycles <= ns_to_cycles(trig_out_duration, CLK_FREQ_HZ);
    -- Convert intensity_duration (ns) to clock cycles
    intensity_duration_cycles <= ns_to_cycles(intensity_duration, CLK_FREQ_HZ);
    -- Convert cooldown_interval (us) to clock cycles
    cooldown_interval_cycles <= us_to_cycles(cooldown_interval, CLK_FREQ_HZ);
    -- Convert monitor_window_start (ns) to clock cycles
    monitor_window_start_cycles <= ns_to_cycles(monitor_window_start, CLK_FREQ_HZ);
    -- Convert monitor_window_duration (ns) to clock cycles
    monitor_window_duration_cycles <= ns_to_cycles(monitor_window_duration, CLK_FREQ_HZ);

    ------------------------------------------------------------------------
    -- Main Application Logic
    --
    -- TODO: Implement your application behavior here
    --
    -- Available inputs:
    --   - trigger_wait_timeout: unsigned(15 downto 0) - Maximum time to wait in ARMED before timing out.
    --     (trigger_wait_timeout_cycles contains clock-cycle equivalent)
    --   - trig_out_voltage: signed(15 downto 0) - Output voltage level for the digital trigger line (mV).
    --   - trig_out_duration: unsigned(15 downto 0) - Duration of the trigger_out pulse.
    --     (trig_out_duration_cycles contains clock-cycle equivalent)
    --   - intensity_voltage: signed(15 downto 0) - Analog intensity/power control voltage delivered to the probe (mV).
    --   - intensity_duration: unsigned(15 downto 0) - Duration of the intensity drive window.
    --     (intensity_duration_cycles contains clock-cycle equivalent)
    --   - cooldown_interval: unsigned(23 downto 0) - Cooldown dwell enforced between pulses.
    --     (cooldown_interval_cycles contains clock-cycle equivalent)
    --   - auto_rearm_enable: std_logic - When true, FSM re-enters ARMED after cooldown instead of idling.
    --   - fault_clear: std_logic - Write 1 to clear fault state and re-arm eligibility.
    --   - probe_monitor_feedback: signed(15 downto 0) - Signed probe current monitor (mV); negative indicates rising current draw.
    --   - monitor_enable: std_logic - Enable probe monitor threshold evaluation.
    --   - monitor_threshold_voltage: signed(15 downto 0) - Threshold (mV) the monitor must cross within the observation window.
    --   - monitor_expect_negative: std_logic - True when a negative-going crossing counts as “probe fired”.
    --   - monitor_window_start: unsigned(31 downto 0) - Delay after trigger before monitoring window opens.
    --     (monitor_window_start_cycles contains clock-cycle equivalent)
    --   - monitor_window_duration: unsigned(31 downto 0) - Length of monitoring window starting at monitor_window_start.
    --     (monitor_window_duration_cycles contains clock-cycle equivalent)
    --
    -- Outputs to drive:
    ------------------------------------------------------------------------
    MAIN_PROC: process(Clk)
    begin
        if rising_edge(Clk) then
            if Reset = '1' then
                state <= IDLE;
                -- TODO: Initialize output signals
            elsif global_enable = '1' then
                -- TODO: Implement your state machine / application logic
                case state is
                    when IDLE =>
                        -- Example: Wait for trigger condition
                        state <= IDLE;

                    when ACTIVE =>
                        -- Example: Perform main operation
                        state <= DONE;

                    when DONE =>
                        -- Example: Return to idle
                        state <= IDLE;

                    when others =>
                        state <= IDLE;
                end case;
            end if;
        end if;
    end process MAIN_PROC;

end architecture rtl;