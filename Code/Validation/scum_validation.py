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
from Validation.Tests.RF_tx_rx_tests import RF_SCuM_test, RF_end_test, RF_self_test


def clear_terminal():
    '''
    Clear the terminal screen
    '''
    
    if os.name == 'nt':  # For Windows
        os.system('cls')
    else:  # For Unix-based systems
        os.system('clear')

def wait_for_trigger(device_handle):
    '''
    Wait for a trigger pulse on the specified pin
    '''
    WF_SDK.logic.open(device_handle, buffer_size=10000)

    # Wait for trigger pulse
    WF_SDK.logic.trigger(device_handle, enable=True, channel=TRIGGER_PIN_NUM, rising_edge=True)
    WF_SDK.logic.record(device_handle, channel=TRIGGER_PIN_NUM, )

    # Close logic analyzer
    WF_SDK.logic.close(device_handle)

binary_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'C-Source/Bin/valScript.bin'))

# List of tests to be performed
# Independent tests are run outside the main loop
tests = {
    'Radio Self Test':        { 'function': RF_self_test,            'independent': True},
    'Program upload':         { 'function': scum_program,            'independent': True},
    'Radio communication':    { 'function': RF_SCuM_test,            'independent': False},
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
    
    results_handle.extend(tests['Radio Self Test']['function']())

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
        

    sleep(0.25)

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
            # Disable all MUX for digital testing
            send_command_to_pico(pico_serial, "0_32")
            send_command_to_pico(pico_serial, "1_32")
            send_command_to_pico(pico_serial, "2_32")
            # Run the test
            results_handle.extend(test_info['function'](dd_handle, TRIGGER_PIN_NUM))
            # Enable all MUX
            send_command_to_pico(pico_serial, "0_33")
            send_command_to_pico(pico_serial, "1_33")
            send_command_to_pico(pico_serial, "2_33")
        elif test_name == 'Analog validation':
            # Run the test
            results_handle.extend(test_info['function'](ad_handle, pico_serial))

        elif test_name == 'Radio communication':
            # Start the test
            success = test_info['function']()
            
            if success:
                # Wait for SCuM to finish
                print("Waiting for SCuM to finish sweep, this will take a few minutes...")
                wait_for_trigger(dd_handle)

                # End and get the results
                results_handle.extend(RF_end_test())
            
            else:
                print("Error: Radio communication test failed!")
                results_handle.append({
                    'sub-test': 'RF Test',
                    'pass': False,
                    'values': [
                        {'name': 'error', 'value': "Radio communication test failed!"}
                    ]
                })
            
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
