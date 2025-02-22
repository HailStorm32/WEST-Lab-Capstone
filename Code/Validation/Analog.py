'''
Contains the Analog class, which is used to validate analog signals.
The following signals are validated:
- 1.1V reference voltage
- 1.8V reference voltage
'''
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../__VendorAPIs/Diligent')))

import WF_SDK

# Constants
MEAUSREMENT_CHANNEL_1_1V = 1
MEASUREMENT_CHANNEL_1_8V = 2

ACCEPATBLE_VOLTAGE_RANGE_1_1V = [1.0, 1.2]
ACCEPATBLE_VOLTAGE_RANGE_1_8V = [1.7, 1.9]


# Dont allow this file to be run directly
if __name__ == '__main__':
    print("\n\nThis file cannot be run directly. Please run the main script.\n\n")
    sys.exit(1)


def validate_1_1V_reference_voltage(device_data):
    '''
    Validate the 1.1V reference voltage

    Parameters: 
        device_data (object): The device data object

    Returns:
        [voltage, pass] (list): The measured voltage and the test result
    '''
    try:
        # Open the scope
        WF_SDK.scope.open(device_data)

        # Read the voltage
        voltage = WF_SDK.scope.measure(device_data, MEAUSREMENT_CHANNEL_1_1V)

        # Determine if the voltage is within the acceptable range
        if voltage >= ACCEPATBLE_VOLTAGE_RANGE_1_1V[0] and voltage <= ACCEPATBLE_VOLTAGE_RANGE_1_1V[1]:
            pass_test = True
        else:
            pass_test = False

        # Close the scope
        WF_SDK.scope.close(device_data)

        return [voltage, pass_test]
    
    except Exception as e:
        print("Error: " + str(e))
        return None

    
def validate_1_8V_reference_voltage(device_data):
    '''
    Validate the 1.8V reference voltage

    Parameters:
        device_data (object): The device data object
    
    Returns:
        [voltage, pass] (list): The measured voltage and the test result
    '''
    try:
        # Open the scope
        WF_SDK.scope.open(device_data)

        # Read the voltage
        voltage = WF_SDK.scope.measure(device_data, MEASUREMENT_CHANNEL_1_8V)

        # Determine if the voltage is within the acceptable range
        if voltage >= ACCEPATBLE_VOLTAGE_RANGE_1_8V[0] and voltage <= ACCEPATBLE_VOLTAGE_RANGE_1_8V[1]:
            pass_test = True
        else:
            pass_test = False

        # Close the scope
        WF_SDK.scope.close(device_data)

        return [voltage, pass_test]

    except Exception as e:
        print("Error: " + str(e))
        return None
    

def validate_analog_signals():
    '''
    Validate the analog signals
    '''
    # Create structure to store test results
    test_results = [
        { 'test': '1.1V reference voltage', 'pass': False },
        { 'test': '1.8V reference voltage', 'pass': False },
    ]

    # Open the device
    try:    
        device_data = WF_SDK.device.open("analogdiscovery2")
    except Exception as e:
        print("Error: " + str(e))
        return test_results # return the test results (all failed)

    # Validate the 1.1V reference voltage
    result = validate_1_1V_reference_voltage(device_data)

    if result:
        print(f"1.1V reference voltage test: {'PASS' if result[1] else 'FAIL'} at {result[0]}V")
        test_results[0]['pass'] = result[1]
    else:
        print("1.1V reference voltage: FAIL (unable to measure)")
        test_results[0]['pass'] = False
    
    # Validate the 1.8V reference voltage
    result = validate_1_8V_reference_voltage(device_data)

    if result:
        print(f"1.8V reference voltage test: {'PASS' if result[1] else 'FAIL'} at {result[0]}V")
        test_results[1]['pass'] = result[1]
    else:
        print("1.8V reference voltage: FAIL (unable to measure)")
        test_results[1]['pass'] = False

    #TODO: Add validation for clocks

    # close the device
    WF_SDK.device.close(device_data)

    return test_results