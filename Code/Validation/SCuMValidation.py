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

def stub_function_call_2(stop_event, return_queue):
    pass

# List of tests to be performed
# Program upload and Power Consumption must be the first and last tests respectively
tests = [
    { 'name': 'Program upload',         'function': stub_program_upload,    'handle': None, 'results': [] },
    { 'name': 'Radio communication',    'function': stub_function_call,     'handle': None, 'results': [] },
    { 'name': 'Digital input/output',   'function': run_logic_analysis,     'handle': None, 'results': [] },
    { 'name': 'Serial communication',   'function': stub_function_call,     'handle': None, 'results': [] },
    { 'name': 'Analog validation',      'function': validate_analog_signals,'handle': None, 'results': [] },
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
    user_input_valid = False

    # Get the Digital I/O pin to use for triggering the SCuM chip from the user
    while not user_input_valid:
        print("Please select an available DIO pin (1-16):")
        trigger_dio = input()
        
        try:
            trigger_dio = int(trigger_dio)
            
            if trigger_dio < 1 or trigger_dio > 16:
                raise

            user_input_valid = True
        except:
            clear_terminal()
            print("Invalid input. Please enter a number between 1 and 16")

    clear_terminal()
    
    # Setup and start joule scope monitoring thread
    stop_event = threading.Event()
    return_queue = queue.Queue()
    joule_scope_thread = threading.Thread(target=stub_function_call_2, args=(stop_event, return_queue))

    # Start the thread
    joule_scope_thread.start()


    # Upload the test program to the SCuM chip
    print("Uploading test program to SCuM chip...")
    tests[0]['results'] = tests[0]['function']()

    #TODO: Add delay for settle time??

    # Run the tests
    # Skip the first and last tests since they are handled differently
    for test in tests[1:len(tests)-1]:
        '''
        Open Digial Discovery

        TODO: Instantiate all device handles at the begining and pass them in as arguments
            This way we can avoid opening and closing the device for each test
        '''
        try:    
            dd_handle = WF_SDK.device.open("Digital Discovery")
        except Exception as e:
            print("Error: " + str(e))
            sys.exit(1)

        # Declare the test being ran
        print("Running test: " + test['name'])

        # Send trigger signal to SCuM chip
        # (Constant HIGH signal for .5 seconds, with inital state of LOW)
        run_time = 0.5
        WF_SDK.pattern.generate(dd_handle, channel=trigger_dio, idle=2, run_time=run_time, function=WF_SDK.pattern.function.pulse, frequency=1, duty_cycle=100)
        sleep(run_time)

        # Close our device handle
        WF_SDK.device.close(dd_handle) # TODO: Remove this line once we have a better way to handle device handles

        # Handle the Digital input/output test differently 
        # since it requires we pass in the trigger_dio value
        if test['name'] == 'Digital input/output':
            # Run the test
            test['results'] = test['function'](trigger_dio)

        else:
            # Run the test
            test['results'] = test['function']()

        #TODO: remove delay 
        sleep(1)

    # Stop the joule scope monitoring thread
    stop_event.set()
    joule_scope_thread.join()

    # Get the results from the joule scope monitoring thread
    tests[-1]["results"] = return_queue.get()

    #TODO: Generate report

