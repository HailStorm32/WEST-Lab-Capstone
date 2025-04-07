'''
Alex Jain - April 7th, 2025

Simple validation script to check if 
powertest1g.py operates correctly.

Version: 1.0
'''

## Import the file.
import time
import threading
from joulescopetest import run, stop_event

def set_stop_event_after_delay(delay):
    """
    Sets the stop_event after a delay.
    """
    time.sleep(delay)
    stop_event.set()
    print("Stop event set.")

def test_joulescope():
    # Run the test
    print("\nRun validation test? [Y/N]")
    userchoice = input("Enter choice: ")

    if userchoice == 'Y' or userchoice == 'y':
        # Start a thread to set stop_event after 15 seconds
        delay_thread = threading.Thread(target=set_stop_event_after_delay, args=(30,))
        delay_thread.start()

        # Call the run function
        run()

        # Wait for the delay thread to finish
        delay_thread.join()
    else:
        print("Not power cycling device...")
        sys.exit(1)

    print("Validation test completed successfully.")

# Call the test function
if __name__ == '__main__':
    test_joulescope()
