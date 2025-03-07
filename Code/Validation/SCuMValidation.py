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
import threading
import queue
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../__VendorAPIs/Diligent')))

import WF_SDK
from Digital import run_logic_analysis
from Analog import validate_analog_signals
from scumProgram import scumProgram
from Config import *

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
def stub_program_upload():
    pass

def stub_function_call():
    pass

def stub_self_check():
    return True

def stub_function_call_2(stop_event, return_queue):
    pass

# List of tests to be performed
# Program upload and Power Consumption must be the first and last tests respectively
tests = [
    { 'name': 'Program upload',         'function': scumProgram,            'handle': None, 'results': [] },
    { 'name': 'Radio communication',    'function': stub_function_call,     'handle': None, 'results': [] },
    { 'name': 'Digital input/output',   'function': run_logic_analysis,     'handle': None, 'results': [] },
    { 'name': 'Analog validation',      'function': validate_analog_signals,'handle': None, 'results': [] },
    { 'name': 'Serial communication',   'function': stub_function_call,     'handle': None, 'results': [] },
    { 'name': 'Power Consumption',      'function': stub_function_call_2,   'handle': None, 'results': [] },
]


# test = [
#     { 'test': 'pin 1', 'pass': False },
#     { 'test': 'pin 2', 'pass': False },
#     { 'test': 'pin 3', 'pass': True },
#     { 'test': 'pin 4', 'pass': False },
# ]

#########################################################
# Main
#########################################################
if __name__ == '__main__':
    clear_terminal()

    # Run self test for spectrum analyzer
    print("Running self test for spectrum analyzer...")
    self_test_result = stub_self_check() # TODO: Replace with spectrum analyzer self test function

    if not self_test_result:
        print("Spectrum analyzer self test failed!\n Exiting...")

        # Fail the tests
        for test in tests:
            test['results'] = None

        #TODO: Generate report

        sys.exit(1)
    else:
        print("Spectrum analyzer self test passed!\n")

    # Setup and start joule scope monitoring thread
    stop_event = threading.Event()
    return_queue = queue.Queue()
    joule_scope_thread = threading.Thread(target=stub_function_call_2, args=(stop_event, return_queue))

    # Start the thread
    joule_scope_thread.start()


    # Upload the test program to the SCuM chip
    print("Uploading test program to SCuM chip...")
    tests[0]['results'] = tests[0]['function']()

    # Wait for power up sequence to complete
    print("Waiting for SCuM chip to power up...")
    sleep(2)

    # Run the tests
    # Skip the first and last tests since they are handled differently
    for test in tests[1:len(tests)-1]:
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

        # Declare the test being ran
        print("Running test: " + test['name'])

        # Close our device handle
        WF_SDK.logic.close(dd_handle)
        WF_SDK.device.close(dd_handle) # TODO: Remove this line once we have a better way to handle device handles

        # Handle the Digital input/output test differently 
        # since it requires we pass in the trigger_dio value
        if test['name'] == 'Digital input/output':
            # Run the test
            test['results'] = test['function'](TRIGGER_PIN_NUM)

        else:
            # Run the test
            test['results'] = test['function']()

        #TODO: remove delay 
        # sleep(1)

    # Stop the joule scope monitoring thread
    print("Stopping joule scope monitoring thread...")
    stop_event.set()
    joule_scope_thread.join()

    # Get the results from the joule scope monitoring thread
    print("Getting joule scope monitoring results...")
    tests[-1]["results"] = return_queue.get()

    #TODO: Generate report

    # Temporary print results
    print("\n\nResults:")
    for test in tests:
        print(f"Test Name: {test['name']}")
        if test['results']:
            print("Results:")
            for result in test['results']:
                print(f"  - {result}")
        else:
            print("No results available.")
        print("-" * 40)

