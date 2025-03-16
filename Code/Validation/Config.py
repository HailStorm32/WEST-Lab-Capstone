'''
This file contains the configuration settings for the validation tests.
'''

########################
# Master Script Configuration
########################

AD2_FOR_DIGITAL = False # Set to True if using Analog Discovery 2 in place of the Digital Discovery

TRIGGER_PIN_NUM = 0  # DIO pin on AD2/DD used for the trigger pin

########################
# SCuM Configuration
########################

SCUM_NRF_COM_PORT = "COM8"  # COM port for nRF board for SCuM "flashing"

########################
# Analog Test Configuration
########################

MEASUREMENT_CHANNEL_1_1V = 1  # AD2 scope channel for measuring the 1.1V reference voltage
MEASUREMENT_CHANNEL_1_8V = 2  # AD2 scope channel for measuring the 1.8V reference voltage

ACCEPTABLE_VOLTAGE_RANGE_1_1V = [1.0, 1.2]  # Acceptable range (in volts) for the 1.1V reference voltage
ACCEPTABLE_VOLTAGE_RANGE_1_8V = [1.7, 1.9]  # Acceptable range (in volts) for the 1.8V reference voltage

CLOCKS_TO_TEST = [          # List of clocks to test
    {'name': "HFCLK",   'exp_freq_hz': 16000000,    'tolerance_ppm': 5},
    {'name': "LFCLK",   'exp_freq_hz': 32768,       'tolerance_ppm': 5},
    {'name': "RC",      'exp_freq_hz': 10,          'tolerance_ppm': 5}
    ]

########################
# Git Validation
########################
GIT_DIRECTORY = "../WSN_Repo"  # Directory where the Git repository is located
GIT_REPO_URL = "" # URL of the Git repository for validation
GIT_BRANCH = ""  # Branch of the Git repository for validation

TIME_TO_RUN = "12:00"  # Time of day to run the validation in 24-hour format (e.g., 14:30 for 2:30 PM)
RUN_IN_DEV_MODE = True  # Set to True if running in development mode (bypasses time check)

########################
# Logic (DO NOT EDIT)
########################
if AD2_FOR_DIGITAL:
    DIGITAL_DEVICE = "analogdiscovery2"
else:
    DIGITAL_DEVICE = "Digital Discovery"