'''
Contains functions to validate the analog signals of the device.
The following signals are validated:
- 1.1V reference voltage
- 1.8V reference voltage
- Clock signals
'''
import os
import sys
from ctypes import *   
import time
import numpy as np
import math
import matplotlib.pyplot as plt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../__VendorAPIs/Diligent')))
import WF_SDK
from Config import *

##################
# Stuff for interfacing with the Digilent WaveForms SDK
##################

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
from WF_SDK.device import check_error
from WF_SDK.scope import data
import csv


# Dont allow this file to be run directly
# if __name__ == '__main__':
#     print("\n\nThis file cannot be run directly. Please run the main script.\n\n")
#     sys.exit(1)


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
            signal_data (numpy pair array): The recorded signal data [[time, voltage],...]
    """

    nSamples = device_data.analog.input.max_buffer_size
    sample_length_s = record_length_ms / 1000
    frequency = nSamples / sample_length_s
    # frequency =  100e06#WF_SDK.scope.data.sampling_frequency 
    buffer = (ctypes.c_double * nSamples)()   # create an empty buffer

    # Set up for acquisition
    dwf.FDwfAnalogInChannelEnableSet(device_data.handle, ctypes.c_int(channel), ctypes.c_bool(True))    # Enable the channel
    dwf.FDwfAnalogInChannelRangeSet(device_data.handle, ctypes.c_int(channel), ctypes.c_double(5))      # Set the range to 5V
    dwf.FDwfAnalogInAcquisitionModeSet(device_data.handle, ctypes.c_int(1))                             # Set to ScanShift AcquisitionMode
    dwf.FDwfAnalogInFrequencySet(device_data.handle, ctypes.c_double(frequency))                        # Set the frequency
    dwf.FDwfAnalogInBufferSizeSet(device_data.handle, ctypes.c_int(nSamples))                           # Set the buffer size   
    dwf.FDwfAnalogInConfigure(device_data.handle, ctypes.c_bool(True), ctypes.c_bool(False))            # Force configure the device

    time.sleep(.3)

    # Create a numpy array to store the buffered data
    buffer_np = np.array([])

    # Variable to store buffer status
    status = ctypes.c_byte()    

    # Begin acquisition
    if dwf.FDwfAnalogInConfigure(device_data.handle, ctypes.c_bool(False), ctypes.c_bool(True)) == 0:
        check_error()

    start_time = time.time()
    while (time.time() - start_time) < sample_length_s:

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

    # Generate buffer for time moments
    time_1 = np.arange(len(buffer_np)) * 1e03 / (frequency)  # convert time to ms
    
    # Combine the time and data arrays into a paired array  [[time, voltage],...]
    signal_data = np.column_stack((time_1, buffer_np))

    ## DEBUG

    # Save the numpy array to a CSV file
    # np.savetxt("analog_signal.csv", buffer_np, delimiter=",")

    # # Save the paired array to a CSV file
    # np.savetxt("paired_signal_data.csv", signal_data, delimiter=",", header="time,voltage", comments='', fmt='%f')

    # plot
    plt.plot(signal_data[:, 0], signal_data[:, 1])
    plt.xlabel("time [ms]")
    plt.ylabel("voltage [V]")
    plt.show()

    #################################################
    # data = WF_SDK.scope.record(device_data, channel=1)

    # # # Generate buffer for time moments
    # time_1 = np.arange(len(data)) * 1e03 / (20e06)  # convert time to ms
    
    # # # Combine the time and data arrays into a paired array  [[time, voltage],...]
    # signal_data = np.column_stack((time_1, data))
    #################################################

    return signal_data

def determine_signal_frequency(device_data, channel=1, n_measurements=10, sample_rate_hz=100e6, v_range_min=0, v_range_max=2):
    '''
    Determine the frequency of a signal

    Parameters:
        device_data (object): The device data object
        channel (int): The channel to measure
        n_measurements (int): The number of measurements to average
        sample_rate_hz (float): The sample rate in Hz (max 100 MHz)
        v_range_min (float): The minimum voltage range
        v_range_max (float): The maximum voltage range

    Returns:
        frequency (float): The frequency of the signal
    '''
    # Validate input
    if n_measurements < 1:
        raise ValueError("n_measurements must be greater than 0")
    elif sample_rate_hz < 1:
        raise ValueError("sample_rate_hz must be greater than 0")
    elif sample_rate_hz > 100e6:
        raise ValueError("sample_rate_hz must be less than 100 MHz")

    # Setup to capture up to 32Ki of samples
    n_buff_max = c_int()
    dwf.FDwfAnalogInBufferSizeInfo(device_data.handle, 0, byref(n_buff_max))
    n_samples = min(32768, n_buff_max.value)
    n_samples = int(2**round(math.log2(n_samples)))

    # Set up acquisition
    dwf.FDwfAnalogInFrequencySet(device_data.handle, c_double(sample_rate_hz))
    dwf.FDwfAnalogInBufferSizeSet(device_data.handle, n_samples)
    dwf.FDwfAnalogInChannelEnableSet(device_data.handle, 0, channel) # enable channel 0 (C1)
    dwf.FDwfAnalogInChannelRangeSet(device_data.handle,  c_double(v_range_min), c_double(v_range_max)) # pk2pk

    # Begin acquisition
    if dwf.FDwfAnalogInConfigure(device_data.handle, c_bool(True), c_bool(True)) == 0 :
        check_error()

    # Convert the sample rate to a c_double
    sample_rate_hz = c_double(sample_rate_hz)
    # dwf.FDwfAnalogInFrequencyGet(device_data.handle, byref(sample_rate_hz))
    # print("Samples: "+str(nSamples)+"  Rate: "+str(hzRate.value/1e6)+"MHz") 

    # Create buffers for samples, window, and bins
    samples = (c_double*n_samples)()
    window = (c_double*n_samples)()
    n_bins = int(n_samples/2+1)
    bins = (c_double*n_bins)()
    maxFrequency = sample_rate_hz.value/2  # nyquist limit

    # Set up the window
    dwf.FDwfSpectrumWindow(byref(window), c_int(n_samples), DwfWindowFlatTop, c_double(1.0), None)
    # print("Range: DC to "+str(hzTop/1e0)+" Hz  Resolution: "+str(hzTop/(nBins-1)/1e3)+" kHz") 

    weighted_freq_sum = 0

    # Perform measurements
    for i in range(n_measurements):

        # Wait for a full buffer
        while True:
            sts = c_byte()
            # Fetch status and data from device
            if dwf.FDwfAnalogInStatus(device_data.handle, c_bool(True), byref(sts)) == 0 :
                check_error()
            if sts.value == DwfStateDone.value :
                break
        
        # Get the data
        dwf.FDwfAnalogInStatusData(device_data.handle, c_int(channel - 1), samples, n_samples) 
        
        # Apply the window
        for i in range(n_samples):
            samples[i] = samples[i]*window[i]

        # Perform the FFT
        dwf.FDwfSpectrumFFT(byref(samples), n_samples, byref(bins), None, n_bins)

        # Find the peak
        iPeak = 0
        vPeak = float('-inf')
        for i in range(5, n_bins): # skip DC lobe
            if bins[i] < vPeak: continue
            vPeak = bins[i]
            iPeak = i

        # print("C"+str(channel)+" peak: "+str(hzTop*iPeak/(nBins-1)/1e0)+" Hz  ")
        
        # Perform a weighted average
        if iPeak < n_bins-5: # weighted average
            s = 0
            m = 0
            for i in range(-4,5):
                t = bins[iPeak+i]
                s += (iPeak+i)*t
                m += t
            iPeak = s/m

        weighted_freq_sum += maxFrequency*iPeak/(n_bins-1)/1e0

    # print("C"+str(channel)+" weighted: "+str(weighted_freq)+" Hz")

    weighted_freq_avg = weighted_freq_sum / n_measurements

    return weighted_freq_avg


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

def test_frequency_measurement_accuracy(device_data):
    """
    Test the accuracy of the frequency measurement.

    Parameters:
        device_data (object): The device data object

    Returns:
        None
    """
    channel = 1
    min_freq = 1e3  # 1 kHz
    max_freq = 25e06  # 25 MHz
    step_freq = 50e3  # 1 kHz
    record_length_ms = 1  # 5 ms

    results = []

    for freq in np.arange(min_freq, max_freq + step_freq, step_freq):
        WF_SDK.scope.trigger(device_data, enable=True, source=WF_SDK.scope.trigger_source.analog, channel=1, level=0)
        print(f"Generating square wave with frequency {freq} Hz...")
        # Generate a square wave with the current frequency
        WF_SDK.wavegen.generate(device_data, channel=1, function=WF_SDK.wavegen.function.square, offset=0, frequency=freq, amplitude=2)
        
        time.sleep(.5)
        
        # print(f"Recording the analog signal for {record_length_ms} ms...")
        # # Record the analog signal
        # data = continuous_record(device_data, channel, record_length_ms)

        print("Determining the frequency of the recorded signal...")
        # Determine the frequency of the signal
        measured_freq = determine_signal_frequency(device_data)

        if measured_freq is None:
            print(f"Error: Could not determine frequency for {freq} Hz.")
            continue

        # Calculate the delta between the measured and expected frequency
        delta = abs(measured_freq - freq)

        # Store the result
        percent_difference = (delta / freq) * 100
        results.append({
            'expected_frequency': freq,
            'measured_frequency': measured_freq,
            'delta': delta,
            'percent_difference': percent_difference
        })

        # Print the result
        print(f"Expected: {freq} Hz, Measured: {measured_freq} Hz, Delta: {delta} Hz, Percent Difference: {percent_difference:.3f}%")

    # Save the results to a CSV file
    with open('frequency_measurement_accuracy_results.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Expected Frequency (Hz)', 'Measured Frequency (Hz)', 'Delta (Hz)'])
        for result in results:
            writer.writerow([result['expected_frequency'], result['measured_frequency'], result['delta']])

    print("Results have been saved to 'frequency_measurement_accuracy_results.csv'")

if __name__ == '__main__':
    # Open the device
    try:    
        device_data = WF_SDK.device.open("analogdiscovery2")
    except Exception as e:
        print("Error: " + str(e))
        sys.exit(1)

    WF_SDK.scope.open(device_data, sampling_frequency=100e6)

    # while True:
    #     WF_SDK.scope.trigger(device_data, enable=True, source=WF_SDK.scope.trigger_source.analog, channel=1, level=0)
        
    #     frequency = 20e06
    #     WF_SDK.wavegen.generate(device_data, channel=1, function=WF_SDK.wavegen.function.square, offset=0, frequency=frequency, amplitude=2) # 10e03

    #     time.sleep(2)

    #     # Record the analog signal for 5ms
    #     # data = continuous_record(device_data, 1, 5)

    #     # ##################################################
    #     # #raw scope record
    #     # data = WF_SDK.scope.record(device_data, channel=1)
    #     # # Convert the list to a numpy array
    #     # data_np = np.array(data)

    #     # # Generate buffer for time moments
    #     # time_1 = np.arange(len(data_np)) * 1e03 / (100e6)  # convert time to ms
        
    #     # # Combine the time and data arrays into a paired array  [[time, voltage],...]
    #     # signal_data = np.column_stack((time_1, data_np))

    #     # # Save the numpy array to a CSV file
    #     # np.savetxt("recorded_signal.csv", data_np, delimiter=",")

    #     # Determine the frequency of the signal
    #     freq = determine_signal_frequency(device_data)

    #     if abs(freq - frequency) > 1:
    #         print(f"Delta: {abs(freq - frequency)} Hz")
    #     else:
    #         print("Delta: 0.0 Hz")

    # ################################################
    # Test the frequency measurement accuracy
    
    test_frequency_measurement_accuracy(device_data)

    # Close the device
    WF_SDK.device.close(device_data)