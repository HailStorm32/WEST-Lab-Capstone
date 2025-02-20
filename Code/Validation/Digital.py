import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../__VendorAPIs/Diligent')))

from WF_SDK import device, logic, pattern, error  # Import instruments
from time import sleep  # Needed for delays

CONSECUTIVE_ONES_REQUIRED = 10  # Minimum consecutive '1's required for passing

def has_consecutive_ones(buffer, required_count):
    """
    Check if the buffer contains at least `required_count` consecutive ones.

    Parameters:
        buffer (list): The recorded values for a channel.
        required_count (int): The minimum number of consecutive ones needed to pass.

    Returns:
        bool: True if the condition is met, False otherwise.
    """
    count = 0
    for value in buffer:
        if value == 1:
            count += 1
            if count >= required_count:
                return True  # Pass if we find enough consecutive 1s
        else:
            count = 0  # Reset count if a 0 is encountered
    return False  # Fail if no sequence meets the requirement


def run_logic_analysis(trigger_channel=0):
    """
    Runs the logic analysis process, setting up the logic analyzer, 
    triggering, recording, and analyzing the captured data.

    Parameters:
        trigger_channel (int): The channel used for triggering, which will be excluded from analysis.

    Returns:
        tests (list): List of dictionaries containing test results for each non-trigger pin.
    """
    # Connect to the device
    device_data = device.open()

    # Initialize the logic analyzer with default settings
    logic.open(device_data, buffer_size=4096)

    # Set up triggering on the specified channel
    logic.trigger(device_data, enable=True, channel=trigger_channel, rising_edge=True)

    sleep(1)  # Wait 1 second

    # **Record data for each DIO channel separately**
    all_buffers = [logic.record(device_data, channel=i) for i in range(16)]

    # Create a list to store test results, ensuring the correct pin numbering
    tests = []

    # Scan each channel's buffer and check for passing condition
    for ch in range(16):
        if ch == trigger_channel:
            continue  # Skip the trigger channel (do not add it to tests)

        test_result = {
            'test': f'pin {ch}',  # Ensure correct pin numbering
            'pass': has_consecutive_ones(all_buffers[ch], CONSECUTIVE_ONES_REQUIRED)
        }
        tests.append(test_result)

    # Print test results
    for test in tests:
        status = "Passed" if test["pass"] else "Failed"
        print(f"{test['test']} {status}")

    # Reset the logic analyzer
    logic.close(device_data)

    # Reset the pattern generator
    pattern.close(device_data)

    # Close the connection
    device.close(device_data)

    return tests  # Return the test results