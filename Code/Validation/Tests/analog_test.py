'''
Contains functions to validate the analog signals of the device.
The following signals are validated:
- 1.1V reference voltage
- 1.8V reference voltage
- Clock signals

The following examples were uses as references:
C:\Program Files (x86)\Digilent\WaveFormsSDK\samples\py\AnalogIn_Record.py
C:\Program Files (x86)\Digilent\WaveFormsSDK\samples\py\AnalogIn_Frequency.py
'''
import csv
import math
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import time
from ctypes import *

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../__VendorAPIs/Diligent')))
import WF_SDK
from WF_SDK.device import check_error
from Utilities.PicoControl.pico_control import send_command_to_pico
from config import *

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

DEBUG = False

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
    

def timed_scope_capture(device_data, channel, record_length_ms=2000, sampling_frequency_hz=100000, v_range_min=0, v_range_max=2):
    """
    Continually record an analog signal for the given time

    parameters: 
        - device_data (object): The device data object
        - channel (int): The channel to record
        - record_length_ms (int): The length of time to record the signal in milliseconds
        - sampling_frequency_hz (int): The sampling frequency in Hz
        - v_range_min (float): The minimum voltage range
        - v_range_max (float): The maximum voltage range

    returns:
        signal_data (numpy pair array): The recorded signal data [[time, voltage],...]
        A CSV file named 'record.csv' containing the recorded signal data
    """

    '''
    TOTO:
    - Add a unique name to the CSV file that includes the date/time
    - Catch issues with record length and sampling frequency mismatch
    '''


    # Validate input
    if record_length_ms < 1:
        raise ValueError("record_length_ms must be greater than 0")
    elif sampling_frequency_hz < 1:
        raise ValueError("sampling_frequency_hz must be greater than 0")
    elif sampling_frequency_hz > 100e6:
        raise ValueError("sampling_frequency_hz must be less than or equal to 100 MHz")

    # Declare variables
    sts = c_byte()
    sampling_frequency_hz = c_double(sampling_frequency_hz)
    record_length_s = c_double(record_length_ms/1000)
    n_samples = sampling_frequency_hz.value * record_length_s.value
    sample_buf = (c_double*int(n_samples))()
    samples_avail = c_int()
    lost_sample_cnt = c_int()
    corrupted_sample_cnt = c_int()
    is_sample_lost = False
    is_signal_corrupted = False

    dwf.FDwfDeviceAutoConfigureSet(device_data.handle, c_bool(False)) # disable auto configure

    # Set up acquisition
    dwf.FDwfAnalogInChannelEnableSet(device_data.handle, c_int(channel - 1), c_bool(True)) # enable channel 0 (C1)
    dwf.FDwfAnalogInChannelRangeSet(device_data.handle, c_double(v_range_min), c_double(v_range_max)) # pk2pk
    dwf.FDwfAnalogInAcquisitionModeSet(device_data.handle, acqmodeRecord) # acquisition mode
    dwf.FDwfAnalogInFrequencySet(device_data.handle, sampling_frequency_hz)
    dwf.FDwfAnalogInRecordLengthSet(device_data.handle, record_length_s) # -1 infinite record length
    dwf.FDwfAnalogInConfigure(device_data.handle, c_int(1), c_int(0))

    # Wait at least 2 seconds for the offset to stabilize
    time.sleep(2)

    dwf.FDwfAnalogInConfigure(device_data.handle, c_bool(False), c_bool(True))

    sample_count = 0

    print("Starting Capture...")    
    while sample_count < n_samples:

        # Fetch status and data from device
        dwf.FDwfAnalogInStatus(device_data.handle, c_bool(True), byref(sts))
        if sample_count == 0 and (sts == DwfStateConfig or sts == DwfStatePrefill or sts == DwfStateArmed) :
            # Acquisition not yet started.
            continue
        
        # Get the status of the record
        dwf.FDwfAnalogInStatusRecord(device_data.handle, byref(samples_avail), byref(lost_sample_cnt), byref(corrupted_sample_cnt))

        # Update the sample count
        sample_count += lost_sample_cnt.value

        # Check if samples were lost or corrupted
        if lost_sample_cnt.value :
            is_sample_lost = True
        if corrupted_sample_cnt.value :
            is_signal_corrupted = True

        # If there are no samples available, go to the next iteration
        if samples_avail.value==0 :
            continue
            
        # If the sample count + available samples is greater than the total number of samples, only take the remaining samples
        if sample_count + samples_avail.value > n_samples :
            samples_avail = c_int(n_samples-sample_count)

        # Get the data
        dwf.FDwfAnalogInStatusData(device_data.handle, c_int(channel - 1), byref(sample_buf, sizeof(c_double)*sample_count), samples_avail)
        sample_count += samples_avail.value

    # Stop the acquisition and reset the device
    dwf.FDwfAnalogOutReset(device_data.handle, c_int(0))
    dwf.FDwfDeviceCloseAll()

    print("Recording done")
    if is_sample_lost:
        print("Samples were lost! Reduce frequency")
    if is_signal_corrupted:
        print("Samples could be corrupted! Reduce frequency")

    # Combine the time and data arrays into a paired array  [[time, voltage],...]
    timestamps = np.arange(len(sample_buf)) * 1e03 / (sampling_frequency_hz.value)  # Create matching timestamps
    signal_data = np.column_stack((timestamps, sample_buf))

    f = open("record.csv", "w") # TODO: Change this to a unique name that includes date/time
    f.write("Timestamp,Voltage\n")
    for i in range(len(sample_buf)):
        f.write(f"{timestamps[i]},{sample_buf[i]}\n")
    f.close()

    # plt.plot(np.fromiter(sample_buf, dtype=float))
    # plt.show()

    #plot the signal in debug mode
    if DEBUG:
        plt.plot(timestamps, sample_buf)
        plt.xlabel('Time (ms)')
        plt.ylabel('Voltage (V)')
        plt.title('Recorded Signal')
        plt.show()

    return signal_data


def determine_signal_frequency(device_data, channel=1, n_measurements=10, sample_rate_hz=100e6, v_range_min=0, v_range_max=2):
    '''
    Determine the frequency of a signal. 
    Accurate for frequencies between 60 Hz and 25 MHz (both inclusive)
    Outside this range, the accuracy drops off

    Parameters:
        device_data (object): The device data object
        channel (int): The channel to measure
        n_measurements (int): The number of measurements to average
        sample_rate_hz (float): The sample rate in Hz (max 100 MHz)
        v_range_min (float): The minimum voltage range
        v_range_max (float): The maximum voltage range

    Returns:
        frequency (float): The frequency of the signal in Hz
    '''
    # Validate input
    if n_measurements < 1:
        raise ValueError("n_measurements must be greater than 0")
    elif sample_rate_hz < 1:
        raise ValueError("sample_rate_hz must be greater than 0")
    elif sample_rate_hz > 100e6:
        raise ValueError("sample_rate_hz must be less than or equal to 100 MHz")

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

    # If the frequency is too low and the sample rate is too high, try again with a lower sample rate
    if (weighted_freq_avg >= 800e0 and weighted_freq_avg <= 60e3) and sample_rate_hz.value > 1e6:
        return determine_signal_frequency(device_data, channel, n_measurements, 1e6, v_range_min, v_range_max)
    elif weighted_freq_avg <= 800e0 and sample_rate_hz.value > 100e3:
        return determine_signal_frequency(device_data, channel, n_measurements, 100e3, v_range_min, v_range_max)
    
    # Else return the frequency as is
    else:
        return weighted_freq_avg

def convert_frequency_to_unit(freq):
    """
    Convert frequency to appropriate unit (Hz, kHz, MHz, GHz) with 4 significant figures.

    Parameters:
        freq (float): Frequency in Hz

    Returns:
        list: [str, float]: The appropriate unit and the frequency in Hz
    """
    if freq >= 1e9:
        return ["GHz", round(freq / 1e9, 4)]
    elif freq >= 1e6:
        return ["MHz", round(freq / 1e6, 4)]
    elif freq >= 1e3:
        return ["kHz", round(freq / 1e3, 4)]
    else:
        return ["Hz", round(freq, 4)]

def validate_analog_signals(device_data, pico_serial):
    '''
    Validate the analog signals
    This function validates the following signals:
    - 1.1V reference voltage
    - 1.8V reference voltage
    - Clock signals
    Parameters:
        device_data (obj): The device data object
        pico_serial (obj): The serial object for the pico device
    Returns:
        test_results (list): List of dictionaries containing test results for each signal
    '''
    # Create structure to store test results
    test_results = [
        { 'sub-test': '1.1V reference voltage', 'pass': False, 'values': [] },
        { 'sub-test': '1.8V reference voltage', 'pass': False, 'values': [] },
    ]

    # Switch scope channels to voltage references
    send_command_to_pico(pico_serial, "1_19") #Scope 1 to 1.1V reference voltage
    send_command_to_pico(pico_serial, "0_16") #Scope 2 to 1.8V reference voltage


    #############################
    # Voltage Validation
    #############################

    # Validate the 1.1V reference voltage
    result = validate_1_1V_reference_voltage(device_data)

    if result:
        print(f"1.1V reference voltage test: {'PASS' if result[1] else 'FAIL'} at {result[0]}V")
        test_results[0]['pass'] = result[1]
        test_results[0]['values'] = [
            {'name': 'measured_voltage (V)', 'value': round(result[0], 4)}
        ]
    else:
        print("1.1V reference voltage: FAIL (unable to measure)")
        test_results[0]['pass'] = False
        test_results[0]['values'] = [
            {'name': 'measured_voltage (V)', 'value': None}
        ]
    
    # Validate the 1.8V reference voltage
    result = validate_1_8V_reference_voltage(device_data)

    if result:
        print(f"1.8V reference voltage test: {'PASS' if result[1] else 'FAIL'} at {result[0]}V")
        test_results[1]['pass'] = result[1]
        test_results[1]['values'] = [
            {'name': 'measured_voltage (V)', 'value': round(result[0], 4)}
        ]
    else:
        print("1.8V reference voltage: FAIL (unable to measure)")
        test_results[1]['pass'] = False
        test_results[1]['values'] = [
            {'name': 'measured_voltage (V)', 'value': None}
        ]

    #############################
    # Clock Validation
    #############################

    for clock in CLOCKS_TO_TEST:
        # Switch mux to the clock signal
        send_command_to_pico(pico_serial, clock['mux-command']) 

        print(f"Validating {clock['name']} clock signal...")

        if DEBUG:
            WF_SDK.wavegen.generate(device_data, channel=1, function=WF_SDK.wavegen.function.square, offset=0, frequency=clock['exp_freq_hz'], amplitude=2)

        # Determine the frequency of the signal
        freq = determine_signal_frequency(device_data, channel=1)
        
        # Determine PPM
        ppm = ((freq - clock['exp_freq_hz']) / clock['exp_freq_hz']) * 1e6

        unit, freq = convert_frequency_to_unit(freq)

        # Validate PPM and store the result
        if abs(ppm) <= clock['tolerance_ppm']:
            print(f"{clock['name']} clock signal test: PASS at {freq} {unit} ({ppm:.3f} ppm)")

            test_results.append({
                'sub-test': f"{clock['name']} clock signal",
                'pass': True,
                'values': [
                    {'name': f'measured_frequency ({unit})', 'value': freq},
                    {'name': 'ppm', 'value': round(ppm, 4)}
                ]
            })
        else:
            print(f"{clock['name']} clock signal test: FAIL at {freq} {unit} ({ppm:.3f} ppm)")

            test_results.append({
                'sub-test': f"{clock['name']} clock signal",
                'pass': False,
                'values': [
                    {'name': f'measured_frequency ({unit})', 'value': freq},
                    {'name': 'ppm', 'value': round(ppm, 4)}
                ]
            })

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
    results = []

    # Define frequency ranges and steps
    # (min_freq, max_freq, step_freq)
    frequency_ranges = [
        (10, 800, 10),
        (800, 1000, 100),
        (1000, 60000, 1000),
        (60000, 49000000, 50000)
    ]

    for min_freq, max_freq, step_freq in frequency_ranges:
        for freq in np.arange(min_freq, max_freq + step_freq, step_freq):
            WF_SDK.scope.trigger(device_data, enable=True, source=WF_SDK.scope.trigger_source.analog, channel=1, level=0)
            print(f"Generating square wave with frequency {freq} Hz...")
            # Generate a square wave with the current frequency
            WF_SDK.wavegen.generate(device_data, channel=1, function=WF_SDK.wavegen.function.square, offset=0, frequency=freq, amplitude=2)
            
            time.sleep(.5)
            
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

            unit, freq = convert_frequency_to_unit(freq)
            unit2, measured_freq = convert_frequency_to_unit(measured_freq)
            unit3, delta = convert_frequency_to_unit(delta)

            # Print the result
            print(f"Expected: {freq} {unit}, Measured: {measured_freq} {unit2}, Delta: {delta} {unit3}, Percent Difference: {percent_difference:.3f}%")

    # Save the results to a CSV file
    with open('frequency_measurement_accuracy_results.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Expected Frequency (Hz)', 'Measured Frequency (Hz)', 'Delta (Hz)'])
        for result in results:
            writer.writerow([result['expected_frequency'], result['measured_frequency'], result['delta']])

    print("Results have been saved to 'frequency_measurement_accuracy_results.csv'")
