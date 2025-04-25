import sys
import os
from ctypes import *
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../__VendorAPIs/Diligent')))

from WF_SDK import device, logic, pattern, error  # Import instruments
from time import sleep  # Needed for delays

# load the dynamic library, get constants path (the path is OS specific)
if sys.platform.startswith("win"):
    # on Windows
    dwf = cdll.dwf
    constants_path = "C:" + os.sep + "Program Files (x86)" + os.sep + "Digilent" + os.sep + "WaveFormsSDK" + os.sep + "samples" + os.sep + "py"
elif sys.platform.startswith("darwin"):
    # on macOS
    lib_path = os.sep + "Library" + os.sep + "Frameworks" + os.sep + "dwf.framework" + os.sep + "dwf"
    dwf = cdll.LoadLibrary(lib_path)
    constants_path = os.sep + "Applications" + os.sep + "WaveForms.app" + os.sep + "Contents" + os.sep + "Resources" + os.sep + "SDK" + os.sep + "samples" + os.sep + "py"
else:
    # on Linux
    dwf = cdll.LoadLibrary("libdwf.so")
    constants_path = os.sep + "usr" + os.sep + "share" + os.sep + "digilent" + os.sep + "waveforms" + os.sep + "samples" + os.sep + "py"

# import constants
sys.path.append(constants_path)
from dwfconstants import *

# Configure VIO to support low logic threshold (~0.6V) for detecting 0.8V signals
def configure_vio_voltage(device_data, voltage_level=1.2):
    try:
        print(f"[VIO Config] Setting VIO to {voltage_level}V")
        hdwf = device_data.handle
        #dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

        if hdwf.value == 0:
            print("[VIO Config] Failed to open device for VIO configuration")
            return

        # Set analog channel 0, node 0 (power supply) to 1.2V
        dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(0), c_int(0), c_double(voltage_level))
        dwf.FDwfAnalogIOEnableSet(hdwf, c_int(True))
        dwf.FDwfAnalogIOConfigure(hdwf)
        print("[VIO Config] VIO output enabled successfully")
        #dwf.FDwfDeviceClose(hdwf)
    except Exception as e:
        print(f"[VIO Config] Warning: Could not set VIO voltage: {e}")


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


def run_logic_analysis(device_data, trigger_channel=0):
    """
    Runs the logic analysis process, setting up the logic analyzer, 
    triggering, recording, and analyzing the captured data.

    Parameters:
        device_data (object): The device data object for the logic analyzer.
        trigger_channel (int): The channel used for triggering, which will be excluded from analysis.

    Returns:
        tests (list): List of dictionaries containing test results for each non-trigger pin.
    """

    #configure_vio_voltage(device_data, voltage_level=1.2)
    print(device_data.name)
    # Initialize the logic analyzer with default settings
    logic.open(device_data, buffer_size=5000)

    sleep(0.3)

    # **Record data for each DIO channel separately**
    all_buffers = [logic.record(device_data, channel=i) for i in range(16)]

    # Create a list to store test results, ensuring the correct pin numbering
    tests = []
    # Scan each channel's buffer and check for passing condition
    for ch in range(16):
        if ch == trigger_channel:
            continue  # Skip the trigger channel (do not add it to tests)

        test_result = {
            'sub-test': f'pin {ch}',  # Ensure correct pin numbering
            'pass': has_consecutive_ones(all_buffers[ch], CONSECUTIVE_ONES_REQUIRED)
        }
        tests.append(test_result)

    # Print test results
    for test in tests:
        status = "Passed" if test["pass"] else "Failed"
        print(f"{test['sub-test']} {status}")

    # Reset the logic analyzer
    logic.close(device_data)

    return tests  # Return the test results
