'''
This script demonstrates some functionality of the Analog Discovery 2 to capture and plot a waveform.
'''
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../__VendorAPIs/Diligent')))

import WF_SDK

def print_header(header):
    print("\n###############################################\n        " + header + "\n###############################################\n")

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

    

    # Close the device
    WF_SDK.device.close(device_data)