'''
Alex Jain - March 1st, 2025

This script is a test script to see if after a 
yepkit power cycle the device will automatically
call the joulescope function and record voltage/current
and place into a text file.
'''

# Import the necessary modules.
import sys
import os
import subprocess
import time
import datetime
import joulescope

# From Joulescope example script.
global output_type

# Callback Statistics - From Joulescope example script.
# Reduced to only voltage and current.
def statistics_callback_log(stats):
    # Note for later: Add power, charge, energy??
    t = stats['time']['range']['value'][0]
    i = stats['signals']['current']['µ']
    v = stats['signals']['voltage']['µ']

    fmts = ['{x:.9f}', '{x:.3f}']
    values = []
    for k, fmt in zip([i, v], fmts):
        value = fmt.format(x=k['value'])
        value = f'{value} {k["unit"]}'
        values.append(value)
    line = ', '.join(values)

    try:
        with open('joulescope_data.txt', 'a') as outfile:
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
            outfile.write(f"{timestamp}, {t:.1f}: {line}\n")
    except Exception as e:
        print(f"Error writing to file: {e}")

# Power Cycle Function - Yepkit
def power_cycle():
    ykushcmd_path = "C:\\Program Files (x86)\\YEPKIT LDA\\ykushcmd\\ykushcmd.exe"
    if not os.path.exists(ykushcmd_path):
        print(f"ykushcmd.exe not found: {ykushcmd_path}")
        return
    
    # Power Cycle USB Downstream Port 1 (Nordic/SCuM).
    print("Turning off USB Port 1")
    subprocess.run([ykushcmd_path, "-d", "1"], shell=True)
    time.sleep(5)
    print("Turning on USB Port 1")
    subprocess.run([ykushcmd_path, "-u", "1"], shell=True)

# Run (Main) Function that runs both power cycle and Joulescope functions.
def run():
    # Default values.
    timeout = 10
    reduction_frequency = 1
    sampling_frequency = 2000000
    i_range = 'auto'
    v_range = '15V'
    output_type = 0

    # Call Power Cycle function.
    power_cycle()

    # Get all joulescope devices or fail if none are found.
    devices = joulescope.scan(config='off')
    if not len(devices):
        print('No Joulescope device found')
        sys.exit(1)

    device = devices[0] # Hack taken from joulescope example script.
    device.open()
    device.statistics_callback_register(statistics_callback_log, 'sensor')

    # Set default parameters.
    device.parameter_set('reduction_frequency', reduction_frequency)
    device.parameter_set('sampling_frequency', sampling_frequency)
    device.parameter_set('i_range', i_range)
    device.parameter_set('v_range', v_range)

    # Print all settings to console.
    print(f"Timer set to: {timeout}"
    print(f"Reduction Frequency set to: {device.parameter_get('reduction_frequency')}")
    print(f"Sampling Frequency set to: {device.parameter_get('sampling_frequency')}")
    print(f"Current Range set to: {device.parameter_get('i_range')}")
    print(f"Voltage Range set to: {device.parameter_get('v_range')}")

    try:
        # No requirement to pull device.status() with the V1 backend
        for _ in range(timeout // 3):
            time.sleep(3)
            stats = device.statistics_get()
            statistics_callback_log(stats)
    finally:
        device.close()

if __name__ == '__main__':
    run()