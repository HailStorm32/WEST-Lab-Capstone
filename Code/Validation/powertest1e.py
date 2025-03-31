'''
Alex Jain - March 29th, 2025

Records voltage/current values.
Calculates averages.

To do:
- Utilize threading.event for the requirements.
- Get min/max values and compare all values for the tests.

Version: 1.2
'''

# Import the necessary modules.
import sys
import os
import subprocess
import time
import joulescope
import csv # For CSV file writing

# From Joulescope example script.
global output_type

# Callback Statistics Log - From Joulescope example script.
# Logs the data to a text file.
def statistics_callback_log(stats):
    # t = stats['time']['range']['value'][0]
    i = stats['signals']['current']['µ']
    v = stats['signals']['voltage']['µ']

    # Extract/Format values
    values = [
        # t, # Time
        i['value'], # Current
        v['value'], # Voltage
        i['units'], # Current Units
        v['units'], # Voltage Units
    ]

    try:
        # Writing to CSV file
        with open("joulescope_data.csv", "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(values)
    except Exception as e:
        print(f"Error writing to file: {e}")

# Power Cycle Function - Yepkit
def power_cycle():
    ykushcmd_path = "C:\\Program Files (x86)\\YEPKIT LDA\\ykushcmd\\ykushcmd.exe"
    if not os.path.exists(ykushcmd_path):
        print(f"ykushcmd.exe not found: {ykushcmd_path}")
        return
    
    # Power Cycle USB Downstream Port 1 (Nordic/SCuM).
    print("Turning off USB Port 3")
    subprocess.run([ykushcmd_path, "-d", "3"], shell=True)
    time.sleep(5)
    print("Turning on USB Port 3")
    subprocess.run([ykushcmd_path, "-u", "3"], shell=True)

# Function to calculate averages from recorded values.
def calculate_average(file_path):
    try:
        with open(file_path, "r") as csvfile:
            reader = csv.reader(csvfile)
            current_sum = 0.0
            voltage_sum = 0.0
            count = 0

            for row in reader:
                try:
                    # Parse the numerical values from the CSV row
                    current = float(row[0])  # Current
                    voltage = float(row[1])  # Voltage
                except (ValueError, IndexError):
                    print(f"Skipping invalid row: {row}")
                    continue

                current_sum += current
                voltage_sum += voltage
                count += 1

            if count == 0:
                print("No valid data found in the file.")
                return

            # Calculate averages
            current_avg = current_sum / count
            voltage_avg = voltage_sum / count

            # Print averages
            print(f"Average Current: {current_avg:.9f} A")
            print(f"Average Voltage: {voltage_avg:.3f} V")

    except Exception as e:
        print(f"Error reading file: {e}")

# Run (Main) Function that runs both power cycle and Joulescope functions.
def run():
    # Print working directory (debugging purposes)
    print(f"Current working directory: {os.getcwd()}")

    # Default values for joulescope.
    timeout = 10
    reduction_frequency = 1
    sampling_frequency = 2000000
    i_range = 'auto'
    v_range = '15V'
    output_type = 0

    # Call Power cycle function - user input to determine Yes/No.
    print("\nPower Cycle? [Y/N]")
    userchoice = input("Enter choice: ")

    if userchoice == 'Y' or userchoice == 'y':
        print("Power cycling device...")
        power_cycle()
    else:
        print("Not power cycling device...")
        sys.exit(1)

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
    print(f"Timer set to: {timeout}")
    print(f"Reduction Frequency set to: {device.parameter_get('reduction_frequency')}")
    print(f"Sampling Frequency set to: {device.parameter_get('sampling_frequency')}")
    print(f"Current Range set to: {device.parameter_get('i_range')}")
    print(f"Voltage Range set to: {device.parameter_get('v_range')}")

    if output_type == 0:
        print(f"Voltage Range set to: {device.parameter_get('v_range')}")
    else:
        print(f"Voltage Range set to: {device.parameter_get('v_range')}")

    try:
        # No requirement to pull device.status() with the V1 backend. Set time to be 3 secs a value.
        time.sleep(timeout)
    finally:
        device.close()

    # Call to calculate averages
    calculate_average("joulescope_data.csv")

if __name__ == '__main__':
    run()
