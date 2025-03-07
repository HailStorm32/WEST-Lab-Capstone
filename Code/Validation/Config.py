'''
This file contains the configuration settings for the validation tests.
'''

AD2_FOR_DIGITAL = True # Set to True if using Analog Discovery 2 in place of the Digital Discovery

if AD2_FOR_DIGITAL:
    DIGITAL_DEVICE = "analogdiscovery2"
else:
    DIGITAL_DEVICE = "Digital Discovery"