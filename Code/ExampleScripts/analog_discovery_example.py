'''
This script demonstrates some functionality of the Analog Discovery 2 to capture and plot a waveform.
'''
import numpy as np
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../__VendorAPIs/Diligent')))

import WF_SDK

def print_header(header):
    print("\n###############################################\n        " + header + "\n###############################################\n")

def plot_results(buffer, x_label, y_label):
    import matplotlib.pyplot as plt

    # generate buffer for time moments
    time = np.arange(len(buffer)) * 1e03 / WF_SDK.scope.data.sampling_frequency  # convert time to ms

    # plot
    plt.plot(time, buffer)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()

# def scope_time_capture(device, channel, run_time, downsample_factor=1, interval=0.1):
#     # Calculate the number of samples needed
#     sampling_frequency = WF_SDK.scope.data.sampling_frequency
#     total_samples_needed = int(sampling_frequency * run_time / downsample_factor)
    
#     # Create numpy array to store the data
#     data = np.empty(0, dtype=np.float64) 

#     while len(data) < total_samples_needed:
#         # Record data from the scope
#         new_data = np.array(WF_SDK.scope.record(device, channel=channel), dtype=np.float64) 
        
#         # Downsample the data if needed
#         if downsample_factor > 1:
#             new_data = new_data[::downsample_factor]
        
#         data = np.concatenate((data, new_data))
        
#         # Wait for the next data acquisition
#         time.sleep(interval)


#     return data

if __name__ == '__main__':
    
    # Open the device
    try:    
        device_data = WF_SDK.device.open("analogdiscovery2")
    except Exception as e:
        print("Error: " + str(e))
        sys.exit(1)

    
    #####################################################################################################
    # Device information (from __VendorAPIs/Diligent/test_device_info.py)
    #####################################################################################################

    print_header("Device information")

    # print device information
    print("WaveForms version: " + device_data.version + "\n")

    # print device name
    print("Device name: " + device_data.name + "\n")

    # print analog input information
    print("Analog input information:")
    print("\tchannels: " + str(device_data.analog.input.channel_count))
    print("\tmaximum buffer size: " + str(device_data.analog.input.max_buffer_size))
    print("\tADC resolution: " + str(device_data.analog.input.max_resolution) + " bits")
    print("\trange settable from " + str(device_data.analog.input.min_range) + "V to " +
                                    str(device_data.analog.input.max_range) + "V in " +
                                    str(device_data.analog.input.steps_range) + " steps")
    print("\toffset settable from " + str(device_data.analog.input.min_offset) + "V to " +
                                    str(device_data.analog.input.max_offset) + "V in " +
                                    str(device_data.analog.input.steps_offset) + " steps\n")

    # print analog output information
    print("Analog output information:")
    for channel_index in range(device_data.analog.output.channel_count):
        print("\tchannel " + str(channel_index) + ":")
        for node_index in range(device_data.analog.output.node_count[channel_index]):
            print("\t\tnode " + str(node_index) + ":")
            print("\t\t\tnode type: " + device_data.analog.output.node_type[channel_index][node_index])
            print("\t\t\tmaximum buffer size: " + str(device_data.analog.output.max_buffer_size[channel_index][node_index]))
            print("\t\t\tamplitude settable from: " + str(device_data.analog.output.min_amplitude[channel_index][node_index]) + "V to " +
                                                    str(device_data.analog.output.max_amplitude[channel_index][node_index]) + "V")
            print("\t\t\toffset settable from: " + str(device_data.analog.output.min_offset[channel_index][node_index]) + "V to " +
                                                str(device_data.analog.output.max_offset[channel_index][node_index]) + "V")
            print("\t\t\tfrequency settable from: " + str(device_data.analog.output.min_frequency[channel_index][node_index]) + "Hz to " +
                                                    str(device_data.analog.output.max_frequency[channel_index][node_index]) + "Hz\n")

    # print analog IO information
    print("Analog IO information:")
    for channel_index in range(device_data.analog.IO.channel_count):
        print("\tchannel " + str(channel_index) + ":")
        print("\t\tchannel name: " + device_data.analog.IO.channel_name[channel_index])
        print("\t\tchannel label: " + device_data.analog.IO.channel_label[channel_index])
        for node_index in range(device_data.analog.IO.node_count[channel_index]):
            print("\t\tnode " + str(node_index) + ":")
            print("\t\t\tnode name: " + device_data.analog.IO.node_name[channel_index][node_index])
            print("\t\t\tunit of measurement: " + device_data.analog.IO.node_unit[channel_index][node_index])
            print("\t\t\tsettable from: " + str(device_data.analog.IO.min_set_range[channel_index][node_index]) + " to " +
                                            str(device_data.analog.IO.max_set_range[channel_index][node_index]) + " in " +
                                            str(device_data.analog.IO.set_steps[channel_index][node_index]) + " steps")
            print("\t\t\treadable between: " + str(device_data.analog.IO.min_read_range[channel_index][node_index]) + " to " +
                                            str(device_data.analog.IO.max_read_range[channel_index][node_index]) + " in " +
                                            str(device_data.analog.IO.read_steps[channel_index][node_index]) + " steps\n")


    # print digital input information
    print("Digital input information:")
    print("\tchannels: " + str(device_data.digital.input.channel_count))
    print("\tmaximum buffer size: " + str(device_data.digital.input.max_buffer_size) + "\n")

    # print digital output information
    print("Digital output information:")
    print("\tchannels: " + str(device_data.digital.output.channel_count))
    print("\tmaximum buffer size: " + str(device_data.digital.output.max_buffer_size))


    #####################################################################################################
    # Scope and Wavegen example
    #####################################################################################################

    print_header("Scope and Wavegen example\n\n Please connect channel 1+ of the Analog Discovery 2 to Wavegen 1 and channel 1- to GND.\n Press Enter to continue...")
    
    # Wait for user input
    input()

    # Open the scope
    WF_SDK.scope.open(device_data)

    # Set up triggering on scope channel 1
    WF_SDK.scope.trigger(device_data, enable=True, source=WF_SDK.scope.trigger_source.analog, channel=1, level=0)

    # Generate a 10KHz sine power signal with 2V amplitude on channel 1
    WF_SDK.wavegen.generate(device_data, channel=1, function=WF_SDK.wavegen.function.sine_power, offset=0, frequency=10e03, amplitude=2)

    # Gather buffer from scope channel 1 (default configuration is 8192 samples)
    data = WF_SDK.scope.record(device_data, channel=1)
    
    plot_results(data, "time [ms]", "voltage [V]")

    # Close the wavegen
    WF_SDK.wavegen.close(device_data)

    # Close the scope
    WF_SDK.scope.close(device_data)


    #####################################################################################################
    # Pattern generator example
    #####################################################################################################

    WF_SDK.logic.open(device_data)

    # Set up triggering on DIO0 falling edge
    WF_SDK.logic.trigger(device_data, enable=True, channel=0, rising_edge=False)

    # Generate a 100KHz PWM signal with 30% duty cycle on a DIO channel
    WF_SDK.pattern.generate(device_data, channel=0, function=WF_SDK.pattern.function.pulse, frequency=100e03, duty_cycle=30)

    '''
    Note: DIO supports internal loopback, so you can generate a signal on DIO0 and record the signal on DIO0 
    without any external connections.
    '''

    # Record a logic signal on a DIO channel
    buffer = WF_SDK.logic.record(device_data, channel=0)

    plot_results(buffer, "time [ms]", "logic value")

    # Close the logic analyzer
    WF_SDK.logic.close(device_data)

    # Close the pattern generator
    WF_SDK.pattern.close(device_data)

    # Close the device
    WF_SDK.device.close(device_data)