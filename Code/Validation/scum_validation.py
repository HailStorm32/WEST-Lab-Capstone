'''
This script validates basic functionality of the SCuM chip
The following tests are performed:
- Program upload
- Digital input/output
- Serial communication
- Voltage validation
- Radio communication
'''
import os
import random  # For simulating power consumption data (remove once actual data is available)
import sys
from time import sleep
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../__VendorAPIs/Diligent')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 

import WF_SDK
from Validation.Tests.analog_test import validate_analog_signals
from config import *
from Validation.Tests.digital_test import run_logic_analysis
from Utilities import report_generation
from Utilities.PicoControl.pico_control import connect_to_pico, send_command_to_pico
from Utilities.scum_program import scum_program
from Validation.Tests.power_test import joulescope_start, stop_joulescope
from Validation.Tests.serial_baud_test import find_best_baud_rate
from Validation.Tests.RF_tx_rx_tests import RF_tx_rx_test, end_test, RF_self_test


def clear_terminal():
    '''
    Clear the terminal screen
    '''
    
    if os.name == 'nt':  # For Windows
        os.system('cls')
    else:  # For Unix-based systems
        os.system('clear')

###################
# Stub functions
# These functions are placeholders for the actual functions that will be implemented elsewhere
# Will be removed once the actual functions are implemented
###################
def stub_self_check():
    return [{'sub-test': 'Radio self test', 'pass': True, 'values': []}]  # Placeholder for actual self-check results

def stub_get_radio_results():
    # Simulate random radio communication results
    return [
        {'sub-test': 'Radio TX', 'pass': random.choice([True, False]), 'values': [{'name': 'tx_power', 'value': random.uniform(-30, 0)}]},
        {'sub-test': 'Radio RX', 'pass': random.choice([True, False]), 'values': [{'name': 'rx_signal_strength', 'value': random.uniform(-100, -30)}]},
        {   'sub-test': 'Signal Over Time', 
            'pass': True, 
            'values': [
                {'name': 'Signal', 'value': [[x, random.uniform(0.0, 5.0)] for x in range(100, 10100, 100)]}, 
                {'name': 'axis_labels', 'value': {'x-label': 'Time (s)', 'y-label': 'signal (dB)'}},  
                {'name': 'Avg dB (dB)', 'value': 42}
            ]
        }
    ]
######################################################################################


def wait_for_trigger(device_handle):
    '''
    Wait for a trigger pulse on the specified pin
    '''
    WF_SDK.logic.open(device_handle)

    # Wait for trigger pulse
    WF_SDK.logic.trigger(device_handle, enable=True, channel=TRIGGER_PIN_NUM, rising_edge=True)
    WF_SDK.logic.record(device_handle, channel=TRIGGER_PIN_NUM)

    # Close logic analyzer
    WF_SDK.logic.close(device_handle)

binary_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'C-Source/Bin/valScript_NOradio.bin'))

# List of tests to be performed
# Independent tests are run outside the main loop
tests = {
    'Program upload':         { 'function': scum_program,            'independent': True},
    'Radio Self Test':        { 'function': RF_self_test,            'independent': True},
    # 'Radio communication':    { 'function': stub_function_call,      'independent': False}, #commented out, radio scum code causing issues with triggers??
    'Digital input/output':   { 'function': run_logic_analysis,      'independent': False}, 
    'Analog validation':      { 'function': validate_analog_signals, 'independent': False}, 
    'Serial communication':   { 'function': find_best_baud_rate,     'independent': False}, 
    'Power Consumption':      { 'function': stop_joulescope,         'independent': True}, 
}

# Create test results structure
test_results = {}

# We only need one test unit for SCuM validation, so we will use 'SCuM-Validation' as the key
test_results['SCuM-Validation'] = {'tests': {}} 

for test in tests:
    test_results['SCuM-Validation']['tests'][test] = {'results': []}

'''
test_results format:
{
    'unit_test': {
        'tests': {
            'test_name':  {'results': []},
            'test_name2': {'results': []},
        }
    },
    # Add more unit tests as needed
}

results list is formatted as:
[
    { 'sub-test': 'pin 1', 'pass': False, values: [] },
    { 'sub-test': 'pin 2', 'pass': False, values: [] },
    # Add more sub tests as needed

]

value list is formatted as:
[   
    # Example of one off values
    {'name': 'value_name1', 'value': 0},
    {'name': 'value_name2', 'value': 55.3},

    # Example of a list value (to be used for graphs)
    {'name': 'value_name3', 'value': [1.2, 2.3, 3.4]},  # Example of a list value
    
    # Example of a 2D list value (to be used for graphs)
    # Must also contain a dictionary with x and y axis labels
    {'name': 'value_name4', 'value': [[1,3], [1,2]}]},  # Example of a 2D list value
    {'name': 'axis_labels', 'value': {'x-label': 'x axis name', 'y-label': 'y axis name'}},  # Example of a dictionary value

    # Example of a path to a graph image
    {'name': 'value_name5', 'value': "path/to/graph.png"},  # Example of path to a graph image
]
'''

#########################################################
# Main
#########################################################
if __name__ == '__main__':
    if not os.path.exists(os.path.join(os.path.dirname(__file__), '../ResultBackups')):
        print("Error: The directory 'ResultBackups' does not exist. Please run the setup script to initialize the environment.")
        os.exit(1)
    elif not os.path.exists(os.path.join(os.path.dirname(__file__), '../ResultBackups/SCuM-Validation')):
        os.makedirs(os.path.join(os.path.dirname(__file__), '../ResultBackups/SCuM-Validation'))

    results_location = os.path.join(os.path.dirname(__file__), '..', 'ResultBackups\\SCuM-Validation', 'SCuM-Validation_Results.html')
    
    clear_terminal()

    # Get the name of the first unit test
    first_unit_test_name = list(test_results.keys())[0]

    # Get handle to self test results
    results_handle = test_results[first_unit_test_name]['tests']['Radio Self Test']['results']

    # Run self test for spectrum analyzer
    print("Running self test for spectrum analyzer...")
    results_handle.extend(stub_self_check()) # TODO: Replace with spectrum analyzer self test function

    if len(results_handle) == 0 or not results_handle[0]['pass']:
        print("Spectrum analyzer self test failed!\n Exiting...")

        report_generation.generate_html_report(test_results, results_location)
        sys.exit(1)
    else:
        print("Spectrum analyzer self test passed!\n")

    # Connect to the PICO board
    print("Connecting to PICO board...")
    pico_serial = connect_to_pico(port=PICO_COM_PORT)

    if pico_serial is None:
        print("Error: Unable to connect to PICO board!\n Exiting...")
        report_generation.generate_html_report(test_results, results_location)
        sys.exit(1)

    # Connect to the Digital Discovery device
    if not AD2_FOR_DIGITAL:
        try:    
            dd_handle = WF_SDK.device.open("Digital Discovery")
        except Exception as e:
            print("Error: " + str(e))
            sys.exit(1)

    # Connect to Analog Discovery 2
    try:
        ad_handle = WF_SDK.device.open("analogdiscovery2")
    except Exception as e:
        print("Error: " + str(e))
        sys.exit(1)

    if AD2_FOR_DIGITAL:
        # Use AD2 for digital testing
        dd_handle = ad_handle

    # Startup the joule scope monitoring thread
    joulescope_start()

    # Upload the test program to the SCuM chip
    print("Uploading test program to SCuM chip...")
    try:
        test_results[first_unit_test_name]['tests']['Program upload']['results'] = tests['Program upload']['function'](SCUM_NRF_COM_PORT, binary_path)
    
    except Exception as e:
        print(f"Error flashing SCuM chip for {binary_path}:\n {e}")

        test_results['SCuM-Validation']['tests']['Program upload']['results'] = [{
                                    'sub-test': 'Program upload',
                                    'pass': False,
                                    'values': [
                                        {'name': 'binary name', 'value': binary_path},
                                        {'name': 'error', 'value': str(e)}
                                        ]
                                }]
        
        report_generation.generate_html_report(test_results, results_location)
        sys.exit(1)
        

    # Wait for power up sequence to complete
    # print("Waiting for SCuM chip to power up...")
    # #sleep(5)

    # Reset mux to set fix conflict with pin 13 for digital testing
    send_command_to_pico(pico_serial, "2_0")

    # Run the tests
    for test_name, test_info in tests.items():

        # Skip independent tests as they are run elsewhere
        if test_info['independent']:
            continue

        print("Waiting for trigger pulse...")
        wait_for_trigger(dd_handle)
        sleep(1)
        # Declare the test being run
        print(f"Running test: {test_name}")

        # Create handle to test's results structure
        results_handle = test_results[first_unit_test_name]['tests'][test_name]['results']

        if test_name == 'Digital input/output':
            # Run the test
            results_handle.extend(test_info['function'](dd_handle, TRIGGER_PIN_NUM))

        elif test_name == 'Analog validation':
            # Run the test
            results_handle.extend(test_info['function'](ad_handle, pico_serial))

        elif test_name == 'Radio communication':
            # Run the test
            test_info['function']()
            
            # Wait for SCuM to finish
            wait_for_trigger(dd_handle)

            results_handle.extend(stub_get_radio_results()) # TODO: Replace with actual function

        else:
            # Run the test
            results_handle.extend(test_info['function']())

    # Stop the joule scope monitoring and get the results
    print("Getting joule scope monitoring results...")

    # Get handle to Power Consumption's results
    results_handle = test_results[first_unit_test_name]['tests']['Power Consumption']['results']
    
    # Stop the joule scope monitoring and get the results
    results_handle.extend(tests['Power Consumption']['function']())

    # Generate the HTML report
    print("Generating HTML report...")
    report_generation.generate_html_report(test_results, results_location)

    # Disconnect from Digilent devices
    if AD2_FOR_DIGITAL:
        WF_SDK.device.close(dd_handle)
    else:
        WF_SDK.device.close(dd_handle)
        WF_SDK.device.close(ad_handle)

    print("\n\nTest Completed!\n")
