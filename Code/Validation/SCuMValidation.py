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
from Analog import validate_analog_signals
from Config import *
from Digital import run_logic_analysis
from Utilities import ReportGeneration
from scumProgram import scum_program

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
def stub_program_upload(arg1):
    return [{'sub-test': 'Program upload', 'pass': True, 'values': []}]  # Placeholder for actual program upload results

def stub_function_call():
    return [{'sub-test': 'Random test', 'pass': random.choice([True, False]), 'values': [{'name': 'random_value', 'value': random.randint(0, 100)}]}]

def stub_self_check():
    return [{'sub-test': 'Radio self test', 'pass': True, 'values': []}]  # Placeholder for actual self-check results

def stub_start_power_monitor():
    pass

def stub_stop_power_monitor():
    # Simulate random power monitoring data
    return [
        {'sub-test': 'Voltage', 'pass': random.choice([True, False]), 'values': [{'name': 'voltage', 'value': random.uniform(1.0, 3.3)}]},
        {'sub-test': 'Current', 'pass': random.choice([True, False]), 'values': [{'name': 'current', 'value': random.uniform(0.01, 0.1)}]},
        {'sub-test': 'Power', 'pass': random.choice([True, False]), 'values': [{'name': 'power', 'value': random.uniform(0.01, 0.33)}]}
    ]

binary_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'C-Source/Bin/SCuM_test.bin'))

# List of tests to be performed
# Independent tests are run outside the main loop
tests = {
    'Program upload':         { 'function': scum_program,            'independent': True},
    'Radio Self Test':        { 'function': stub_self_check,         'independent': True},
    'Radio communication':    { 'function': stub_function_call,      'independent': False}, 
    'Digital input/output':   { 'function': run_logic_analysis,      'independent': False}, 
    'Analog validation':      { 'function': validate_analog_signals, 'independent': False}, 
    'Serial communication':   { 'function': stub_function_call,      'independent': False}, 
    'Power Consumption':      { 'function': None,                    'independent': True}, 
}

# Create test results structure
test_results = {}  # List to store test results

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

        ReportGeneration.generate_html_report(test_results)
        sys.exit(1)
    else:
        print("Spectrum analyzer self test passed!\n")

    # Startup the joule scope monitoring thread
    stub_start_power_monitor() # TODO: Replace with actual function

    # Upload the test program to the SCuM chip
    print("Uploading test program to SCuM chip...")
    try:
        test_results[first_unit_test_name]['tests']['Program upload']['results'] = tests['Program upload']['function'](binary_path)
    
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
        
        ReportGeneration.generate_html_report(test_results)
        sys.exit(1)
        

    # Wait for power up sequence to complete
    print("Waiting for SCuM chip to power up...")
    sleep(2)

    # Run the tests
    for test_name, test_info in tests.items():

        # Skip independent tests as they are run elsewhere
        if test_info['independent']:
            continue

        '''
        Open Digital Discovery

        TODO: Instantiate all device handles at the beginning and pass them in as arguments
            This way we can avoid opening and closing the device for each test
        '''
        try:    
            dd_handle = WF_SDK.device.open(DIGITAL_DEVICE)
        except Exception as e:
            print("Error: " + str(e))
            sys.exit(1)

        print("Waiting for trigger pulse...")

        # Wait for trigger pulse
        WF_SDK.logic.trigger(dd_handle, enable=True, channel=TRIGGER_PIN_NUM, rising_edge=True)
        WF_SDK.logic.record(dd_handle, channel=TRIGGER_PIN_NUM)

        # Declare the test being run
        print(f"Running test: {test_name}")

        # Close our device handle
        WF_SDK.logic.close(dd_handle)
        WF_SDK.device.close(dd_handle) # TODO: Remove this line once we have a better way to handle device handles

        # Create handle to test's results structure
        results_handle = test_results[first_unit_test_name]['tests'][test_name]['results']

        # Handle the Digital input/output test differently 
        # since it requires we pass in the trigger_dio value
        if test_name == 'Digital input/output':
            # Run the test
            results_handle.extend(test_info['function'](TRIGGER_PIN_NUM))

        else:
            # Run the test
            results_handle.extend(test_info['function']())

        #TODO: remove delay 
        # sleep(1)

    # Stop the joule scope monitoring and get the results
    print("Getting joule scope monitoring results...")

    # Get handle to Power Consumption's results
    results_handle = test_results[first_unit_test_name]['tests']['Power Consumption']['results']
    
    results_handle.extend(stub_stop_power_monitor()) # TODO: Replace with actual function

    ReportGeneration.generate_html_report(test_results)

    # Temporary print results
    print("\nTest Results:")
    print("=" * 40)

    for unit_test, unit_data in test_results.items():
        print(f"Unit Test: {unit_test}")
        print("-" * 40)

        for test_name, test_data in unit_data['tests'].items():
            print(f"  Test Name: {test_name}")
            print("  Results:")
            
            if not test_data['results']:
                print("    No results available.")
            else:
                for result in test_data['results']:
                    print("    Sub-Test:")
                    print(f"      - Sub-Test Name: {result.get('sub-test', 'N/A')}")
                    print(f"      - Pass: {'Yes' if result.get('pass') else 'No'}")
                    print("      - Values:")
                    for value in result.get('values', []):
                        print(f"        * {value['name']}: {value['value']}")
            print("-" * 40)

    print("=" * 40)

