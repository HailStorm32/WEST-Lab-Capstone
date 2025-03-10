'''
Contains the Analog class, which is used to validate analog signals.
The following signals are validated:
- 1.1V reference voltage
- 1.8V reference voltage
'''
import os
import sys
import ctypes     
import time
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../__VendorAPIs/Diligent')))
import WF_SDK
from Config import *

##################
# Stuff for interfacing with the Digilent WaveForms SDK
##################

# load the dynamic library, get constants path (the path is OS specific)
if sys.platform.startswith("win"):
    # on Windows
    dwf = ctypes.cdll.dwf
    constants_path = "C:" + os.sep + "Program Files (x86)" + os.sep + "Digilent" + os.sep + "WaveFormsSDK" + os.sep + "samples" + os.sep + "py"
elif sys.platform.startswith("darwin"):
    # on macOS
    lib_path = os.sep + "Library" + os.sep + "Frameworks" + os.sep + "dwf.framework" + os.sep + "dwf"
    dwf = ctypes.cdll.LoadLibrary(lib_path)
    constants_path = os.sep + "Applications" + os.sep + "WaveForms.app" + os.sep + "Contents" + os.sep + "Resources" + os.sep + "SDK" + os.sep + "samples" + os.sep + "py"
else:
    # on Linux
    dwf = ctypes.cdll.LoadLibrary("libdwf.so")
    constants_path = os.sep + "usr" + os.sep + "share" + os.sep + "digilent" + os.sep + "waveforms" + os.sep + "samples" + os.sep + "py"

# import constants
sys.path.append(constants_path)
import dwfconstants as constants
from WF_SDK.device import check_error
from WF_SDK.scope import data


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
        voltage = WF_SDK.scope.measure(device_data, MEASUREMENT_CHANNEL_1_1V)

        # Determine if the voltage is within the acceptable range
        if voltage >= ACCEPTABLE_VOLTAGE_RANGE_1_1V[0] and voltage <= ACCEPTABLE_VOLTAGE_RANGE_1_1V[1]:
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
        if voltage >= ACCEPTABLE_VOLTAGE_RANGE_1_8V[0] and voltage <= ACCEPTABLE_VOLTAGE_RANGE_1_8V[1]:
            pass_test = True
        else:
            pass_test = False

        # Close the scope
        WF_SDK.scope.close(device_data)

        return [voltage, pass_test]

    except Exception as e:
        print("Error: " + str(e))
        return None
    

def continuous_record(device_data, channel, record_length_ms):
    """
        Continually record an analog signal for the given time
        using ScanShift Acquisition

        parameters: 
            - device_data (object): The device data object
            - channel (int): The channel to record
            - record_length_ms (int): The length of time to record the signal in milliseconds

        returns:
            None
    """

    nSamples = device_data.analog.input.max_buffer_size
    sample_length_ms = record_length_ms / 1000

    buffer = (ctypes.c_double * nSamples)()   # create an empty buffer

    # Set up for acquisition
    dwf.FDwfAnalogInChannelEnableSet(device_data.handle, ctypes.c_int(channel), ctypes.c_bool(True))    # Enable the channel
    dwf.FDwfAnalogInChannelRangeSet(device_data.handle, ctypes.c_int(channel), ctypes.c_double(5))      # Set the range to 5V
    dwf.FDwfAnalogInAcquisitionModeSet(device_data.handle, ctypes.c_int(1))                             # Set to ScanShift AcquisitionMode
    dwf.FDwfAnalogInFrequencySet(device_data.handle, ctypes.c_double(nSamples/sample_length_ms))        # Set the frequency
    dwf.FDwfAnalogInBufferSizeSet(device_data.handle, ctypes.c_int(nSamples))                           # Set the buffer size   
    dwf.FDwfAnalogInConfigure(device_data.handle, ctypes.c_bool(True), ctypes.c_bool(False))            # Force configure the device

    time.sleep(1)

    # Begin acquisition
    if dwf.FDwfAnalogInConfigure(device_data.handle, ctypes.c_bool(False), ctypes.c_bool(True)) == 0:
        check_error()
    
    # Create a numpy array to store the buffered data
    buffer_np = np.array([])

    status = ctypes.c_byte()    # variable to store buffer status

    start_time = time.time()
    while (time.time() - start_time) * 1000 < sample_length_ms:

        # Wait for a full buffer
        sample_count = ctypes.c_int(0)
        while sample_count.value != nSamples:
            ret = dwf.FDwfAnalogInStatus(device_data.handle, ctypes.c_bool(True), ctypes.byref(status))
            ret &= dwf.FDwfAnalogInStatusSamplesValid(device_data.handle, ctypes.byref(sample_count))
            if ret == 0:
                check_error()
    
        # Copy buffer (takes channel number as 0-indexed)
        if dwf.FDwfAnalogInStatusData(device_data.handle, ctypes.c_int(channel - 1), buffer, ctypes.c_int(nSamples)) == 0:
            check_error()

        # Convert buffer to numpy array and append to it
        buffer_np = np.append(buffer_np, np.array(buffer))


    ## DEBUG

    # Save the numpy array to a CSV file
    np.savetxt("analog_signal.csv", buffer_np, delimiter=",")

    import matplotlib.pyplot as plt

    # generate buffer for time moments
    # time_1 = np.arange(len(buffer)) * 1e03 / WF_SDK.scope.data.sampling_frequency  # convert time to ms
    time_1 = np.arange(len(buffer)) * 1e03 / ( nSamples/sample_length_ms )  # convert time to ms

    # plot
    plt.plot(time_1, buffer), 
    plt.xlabel("time [ms]")
    plt.ylabel("voltage [V]")
    plt.show()

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