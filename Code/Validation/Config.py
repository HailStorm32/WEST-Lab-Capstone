'''
This file contains the configuration settings for the validation tests.
'''
import sys
import os

########################
# Master Script Configuration
########################

AD2_FOR_DIGITAL = False # Set to True if using Analog Discovery 2 in place of the Digital Discovery

TRIGGER_PIN_NUM = 1  # DIO pin on AD2/DD used for the trigger pin

PICO_COM_PORT = "COM10"  # COM port for the PICO board for flashing and testing

########################
# SCuM Configuration
########################

SCUM_NRF_COM_PORT = "COM8"  # COM port for nRF board for SCuM "flashing"

SCUM_SERIAL_COM_PORT = "COM11"  # COM port that the SCuM board is connected to for serial communication

########################
# Analog Test Configuration
########################

MEASUREMENT_CHANNEL_1_1V = 1  # AD2 scope channel for measuring the 1.1V reference voltage
MEASUREMENT_CHANNEL_1_8V = 2  # AD2 scope channel for measuring the 1.8V reference voltage

ACCEPTABLE_VOLTAGE_RANGE_1_1V = [1.0, 1.2]  # Acceptable range (in volts) for the 1.1V reference voltage
ACCEPTABLE_VOLTAGE_RANGE_1_8V = [1.7, 1.9]  # Acceptable range (in volts) for the 1.8V reference voltage

CLOCKS_TO_TEST = [    # List of clocks to test     
    {'name': "HFCLK",   'exp_freq_hz': 20000000,    'tolerance_ppm': 1000, 'mux-command': '1_5'},
    {'name': "LFCLK",   'exp_freq_hz': 20000000,    'tolerance_ppm': 1000, 'mux-command': '1_15'}
    # {'name': "RC",      'exp_freq_hz': 10,          'tolerance_ppm': 5}
    ]
'''
PPM = ((exp_freq_hz - measured_freq_hz) / exp_freq_hz) * 1_000_000
''' 

#########################
# Joulescope Configuration
#########################

PWR_USE_ACCEPTABLE_VOLTAGE_RANGE_V = [1.0, 1.2]  # Acceptable range (in volts) for the power supply voltage (inclusive)
PWR_USE_ACCEPTABLE_CURRENT_RANGE_A = [0.0001, 0.1]  # Acceptable range (in Amps) for the power supply current (inclusive)

########################
# Git Validation
########################

GIT_DIRECTORY = os.path.join(os.path.dirname(__file__), '../GitTestingRepos/openwsn-fw/')  # Directory where the Git repository is located

TIME_TO_RUN = "12:00"  # Time of day to run the validation in 24-hour format (e.g., 14:30 for 2:30 PM)
RUN_IN_DEV_MODE = True  # Set to True if running in development mode (bypasses time check)

GIT_BINARY_PATHS = [
    { 'path': os.path.join(GIT_DIRECTORY, "projects/scum/01bsp_sctimer_gpio/test_bin.bin"), 'branch': "wip_testing", 'lastHash': None },  # Path to the binary file
]

########################
# Logic (DO NOT EDIT)
########################
#nothing here for now