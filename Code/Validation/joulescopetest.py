'''
Alex Jain - April 14th, 2025

Records voltage/current values.
Calculates results & displays them.

Version: 1.5.4
'''

# Import the necessary modules.
import sys
import os
import subprocess
import time
import joulescope
import csv
import threading

# Global Variables
global output_type
device = None  # Store device instance
stop_event = threading.Event()  # Event to signal stopping the device

# Manages & Callback statistics - outputs into a CSV file
def statistics_callback_log(stats):
    i = stats['signals']['current']['µ']
    v = stats['signals']['voltage']['µ']

    # Extract/Format values
    values = [
        i['value'],  # Current
        v['value'],  # Voltage
        i['units'],  # Current Units
        v['units'],  # Voltage Units
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
    
    # Power Cycle USB Downstream Port 3 (Nordic/SCuM).
    print("Turning off USB Port 3")
    subprocess.run([ykushcmd_path, "-d", "3"], shell=True)
    time.sleep(5)
    print("Turning on USB Port 3")
    subprocess.run([ykushcmd_path, "-u", "3"], shell=True)

# Function to handle device operations
def device_operations():
    global device
    # Get all Joulescope devices or fail if none are found
    devices = joulescope.scan(config='off')
    if not len(devices):
        print('No Joulescope device found')
        return

    device = devices[0]  # Hack taken from Joulescope example script
    device.open()
    device.statistics_callback_register(statistics_callback_log, 'sensor')

    # Set default parameters
    device.parameter_set('reduction_frequency', 1)
    device.parameter_set('sampling_frequency', 2000000)
    device.parameter_set('i_range', 'auto')
    device.parameter_set('v_range', '15V')

    print("Joulescope is now collecting data...")

# Function to stop the device & process the results.
def stop_joulescope(file_path):
    """
    Stops the device and processes the results from the specified CSV file.
    """
    # Signal the stop event and wait for the thread to finish
    stop_event.set()
    device_thread.join()

    # Process the results
    try:
        with open(file_path, "r") as csvfile:
            reader = csv.reader(csvfile)
            current_sum = 0.0
            voltage_sum = 0.0
            count = 0

            # Initialize min and max values
            current_min = float('inf')
            current_max = float('-inf')
            voltage_min = float('inf')
            voltage_max = float('-inf')

            for row in reader:
                try:
                    # Parse the numerical values from the CSV row
                    current = float(row[0])  # Current
                    voltage = float(row[1])  # Voltage
                except (ValueError, IndexError):
                    print(f"Skipping invalid row: {row}")
                    continue

                # Update sums
                current_sum += current
                voltage_sum += voltage

                # Update min and max values
                current_min = min(current_min, current)
                current_max = max(current_max, current)
                voltage_min = min(voltage_min, voltage)
                voltage_max = max(voltage_max, voltage)

                count += 1

            if count == 0:
                print("No valid data found in the file.")
                return

            # Calculate averages
            current_avg = current_sum / count
            voltage_avg = voltage_sum / count

            # Define the voltage threshold
            voltage_threshold = 1.1

            # Format Results
            results = [
                {
                    'test': 'voltage_avg',
                    'pass': voltage_avg <= voltage_threshold,
                    'value': f"{voltage_avg:.3f} V"
                },
                {
                    'test': 'voltage_min',
                    'pass': voltage_min <= voltage_threshold,
                    'value': f"{voltage_min:.3f} V"
                },
                {
                    'test': 'voltage_max',
                    'pass': voltage_max <= voltage_threshold,
                    'value': f"{voltage_max:.3f} V"
                },
                {
                    'test': 'current_avg',
                    'pass': None,  # No threshold defined for current
                    'value': f"{current_avg:.9f} A"
                },
                {
                    'test': 'current_min',
                    'pass': None,  # No threshold defined for current
                    'value': f"{current_min:.9f} A"
                },
                {
                    'test': 'current_max',
                    'pass': None,  # No threshold defined for current
                    'value': f"{current_max:.9f} A"
                },
            ]

            # Print the results
            for result in results:
                print(result)

    except Exception as e:
        print(f"Error reading file: {e}")

# Run (Main) Function that runs both power cycle and Joulescope functions.
def joulescope_start():
    print(f"Current working directory: {os.getcwd()}")

    power_cycle()  # Power Cycle the Yepkit hub

    # Start the device operations in a separate thread
    global device_thread
    device_thread = threading.Thread(target=device_operations)
    device_thread.start()

    # Print that Joulescope started in another thread.
    print("Joulescope started...")

if __name__ == '__main__':
    joulescope_start()
