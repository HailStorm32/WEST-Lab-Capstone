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


########################
# Logic (DO NOT EDIT)
########################
if AD2_FOR_DIGITAL:
    DIGITAL_DEVICE = "analogdiscovery2"
else:
    DIGITAL_DEVICE = "Digital Discovery"