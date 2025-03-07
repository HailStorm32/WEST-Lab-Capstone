'''
This file contains the configuration settings for the validation tests.
'''

########################
# Master Script Configuration
########################

AD2_FOR_DIGITAL = True # Set to True if using Analog Discovery 2 in place of the Digital Discovery

TRIGGER_PIN_NUM = 0  # DIO pin on AD2/DD used for the trigger pin

########################
# SCuM Configuration
########################

SCUM_NRF_COM_PORT = "COM8"  # COM port for nRF board for SCuM "flashing"


########################
# Logic (DO NOT EDIT)
########################
if AD2_FOR_DIGITAL:
    DIGITAL_DEVICE = "analogdiscovery2"
else:
    DIGITAL_DEVICE = "Digital Discovery"