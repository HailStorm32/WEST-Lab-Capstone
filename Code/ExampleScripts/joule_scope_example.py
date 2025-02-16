# Joule Scope example/demo script
#
# Accepts -flag value pairs as arguemnts. EX. -t 10
#   -t : Time out in seconds. The scipt will run for this long
#   -ot : Output type. Default prints to teminal. Value of 1 to save to log file
#   -rf : reduction_frequency. The rate that the device produces statistics, including multimeter values.
#   -sf : sampling_frequency. The rate that the device produces samples.
#   -ir : i_range. Select the current measurement range (shunt resistor)
#   -vr : v_range. Select the voltage measurement range (gain)
#
#   Acceptable input values can be found here: https://github.com/jetperch/pyjoulescope/blob/main/joulescope/parameters_v1.py#L275

import joulescope
import time
import sys
import datetime

global output_type

def statistics_callback(stats):
    t = stats['time']['range']['value'][0]
    i = stats['signals']['current']['µ']
    v = stats['signals']['voltage']['µ']
    p = stats['signals']['power']['µ']
    c = stats['accumulators']['charge']
    e = stats['accumulators']['energy']

    fmts = ['{x:.9f}', '{x:.3f}', '{x:.9f}', '{x:.9f}', '{x:.9f}']
    values = []
    for k, fmt in zip([i, v, p, c, e], fmts):
        value = fmt.format(x=k['value'])
        value = f'{value} {k["units"]}'
        values.append(value)
    line = ', '.join(values)
    print(f"{t:.1f}: " + ', '.join(values))

def statistics_callback_log(stats):
    t = stats['time']['range']['value'][0]
    i = stats['signals']['current']['µ']
    v = stats['signals']['voltage']['µ']
    p = stats['signals']['power']['µ']
    c = stats['accumulators']['charge']
    e = stats['accumulators']['energy']

    fmts = ['{x:.9f}', '{x:.3f}', '{x:.9f}', '{x:.9f}', '{x:.9f}']
    values = []
    for k, fmt in zip([i, v, p, c, e], fmts):
        value = fmt.format(x=k['value'])
        value = f'{value} {k["units"]}'
        values.append(value)
    line = ', '.join(values)
    
    try:
        with open("statistics_data.txt", "a") as outfile: 
            now = datetime.datetime.now() 
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S") 
            outfile.write(f"{timestamp}, {t:.1f}: {line}\n") 
    except Exception as e:
            print(f"Error writing to file: {e}") 


def parse_argument(arguments, devices):
    i = 0
    while i < len(arguments):
        arg = arguments[i]

        if arg.startswith("-"):  # Check if it's a flag
            if i + 1 < len(arguments):  # is there a value after the flag
                value = arguments[i + 1]
                process_argument(arg, value, devices)  # Process the flag and value
                i += 2  # Skip the value in the next iteration
            else:
                print(f"Error: Flag '{arg}' has no associated value.")
                sys.exit(1)
        else:
            print(f"Error: Argument '{arg}' does not start with '-'. Ignoring.")
            i += 1

def process_argument(flag, value, devices):
    if flag == "-rf":#reduction_frequency
        print(f"Processing reduction frequency({flag}) with value: {value}")
        devices.parameter_set('reduction_frequency', int(value))
    elif flag == "-t":#timer
        print(f"Processing timer({flag}) with value: {value}")
        timeout = int(value)
    elif flag == "-ir": # Current range (shunt resistor)
        print(f"Processing I range({flag}) with value: {value}")
        devices.parameter_set('i_range', value)
    elif flag == "-vr":  # Voltage range (gain)
        print(f"Processing V range({flag}) with value: {value}")
        devices.parameter_set('v_range', int(value))
    elif flag == "-sf":  # sampling_frequency
        print(f"Processing sampling frequency({flag}) with value: {value}")
        devices.parameter_set('sampling_frequency', int(value))
    elif flag == "-ot":  # output type 
        if int(value) == 1: 
            print(f"Processing output type({flag}) with value: {value}")
            devices.statistics_callback_unregister(statistics_callback, 'sensor')
            devices.statistics_callback_register(statistics_callback_log, 'sensor')
        else:
            print(f"Unknown output type({flag}) with value: {value} set to Default.")

    else:
        print(f"Unknown flag: {flag}")

def run():
    timeout = 10 # default timeout value
    output_type = 0
    arguments = sys.argv[1:] # get args


    # Get all joulescope devices or fail if none are found
    devices = joulescope.scan(config='off')
    if not len(devices):
        print('No Joulescope device found')
        sys.exit(1)
    # The jouleScope driver will return a list off all joulescope devices connected. Each will have a using serial number field.


    device = devices[0] # this is a hack to keep it to a single device not a list
    device.open()
    device.statistics_callback_register(statistics_callback, 'sensor')
    parse_argument(arguments, device)  # Call the function to process arguments     
    # Print all settings         
    print(f"Timer set to: {timeout}")
    print(f"reduction_frequency set to: {device.parameter_get('reduction_frequency')}")
    print(f"sampling_frequency set to: {device.parameter_get('sampling_frequency')}")
    print(f"sampling_frequency set to: {device.parameter_get('sampling_frequency')}")
    print(f"i_range set to: {device.parameter_get('i_range')}")
    print(f"v_range set to: {device.parameter_get('v_range')}")
    if output_type == 0:
        print(f"v_range set to: {device.parameter_get('v_range')}")
    else:
        print(f"v_range set to: {device.parameter_get('v_range')}")
     
    try:
        # no need to poll device.status() with the v1 backend
        time.sleep(timeout)
    finally:
        device.close()

if __name__ == '__main__':
    run()