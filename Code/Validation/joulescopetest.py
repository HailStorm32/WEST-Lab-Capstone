'''
Alex Jain - April 18th, 2025

Records voltage/current values.
Calculates results & displays them.

DEFAULT_CSV_PATH NOTICE:
By default if main does:
statistics_callback_log(stats) &
stop_joulescope(), then default path is used.
Default in stop is delete_file=True, save_backup=True.

If specifying custom path, main needs to specify as:
statistics_callback_log(stats, file_path="custom_path.csv") &
stop_joulescope(file_path="custom_path.csv",delete_file=True/False, save_backup=True/False).

Added function: save_backup()
This function should save a backup of the file in the ResultBackups directory 
under the specified category.

Version: 1.6.2
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

# Default path for the Joulescope CSV file
DEFAULT_CSV_PATH = "joulescope_data.csv"

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
        with open(DEFAULT_CSV_PATH, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(values)
    except Exception as e:
        print(f"Error writing to file: {e}")
        return None # Return None to propagate error(s) to caller.

# Power Cycle Function - Yepkit
def power_cycle():
    ykushcmd_path = "C:\\Program Files (x86)\\YEPKIT LDA\\ykushcmd\\ykushcmd.exe"
    if not os.path.exists(ykushcmd_path):
        print(f"ykushcmd.exe not found: {ykushcmd_path}")
        return None # Return None to propagate error(s) to caller.
    
    try:
        # Power Cycle USB Downstream Port 1 (Nordic/SCuM).
        print("Turning off USB Port 1")
        subprocess.run([ykushcmd_path, "-d", "1"], shell=True)
        time.sleep(5) # Blocking call to ensure it properly power cycles.
        print("Turning on USB Port 1")
        subprocess.run([ykushcmd_path, "-u", "1"], shell=True)
    except Exception as e:
        print(f"Error during power cycle: {e}")
        return None # Return None to propagate error(s) to caller.
    
    return True # Return True to indicate power cycle success.
    
# Function to handle joulescope device operations.
def device_operations():
    global device
    # Get all Joulescope devices or fail if none are found
    devices = joulescope.scan(config='off')
    if not len(devices):
        print('No Joulescope device found')
        return None # Return None to propagate errors to caller.
    
    try:
        device = devices[0] # Hack from Joulescope example script.
        device.open()
        device.statistics_callback_register(statistics_callback_log, 'sensor')

        # Set default parameters
        device.parameter_set('reduction_frequency', 1)
        device.parameter_set('sampling_frequency', 2000000)
        device.parameter_set('i_range', 'auto')
        device.parameter_set('v_range', '15V')

        print("Joulescope set up and collecting data...")
        return True # Return True to indicate device operation success.
    except Exception as e:
        print(f"Error during device operations: {e}")
        return None # Return None to propagate error(s) to caller.

# Function to stop the device & process the results.
def stop_joulescope(file_path=DEFAULT_CSV_PATH, delete_file=True, save_backup_flag=True):
    """
    Stops the device and processes the results from the specified CSV file.
    Optionally saves a backup and deletes the original file.
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
                return None  # Return None if no valid data is found

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

            # Save a backup of the file if the flag is set
            if save_backup_flag:
                save_backup(file_path, category="joulescope")

            return results  # Return the results on success

    except Exception as e:
        print(f"Error reading file: {e}")
        return [
            {
                'Test': 'Joulescope Error',
                'Pass': False,
                'Value': str(e)
            }
        ]  # Return error structure on failure

    finally:
        # Delete the file if the delete_file flag is True
        if delete_file:
            try:
                os.remove(file_path)
                print(f"File {file_path} deleted.")
            except Exception as e:
                print(f"Error deleting file: {e}")
                return None # Return None to propagate error(s) to caller.

# Run (Main) Function that runs both power cycle and Joulescope functions.
def joulescope_start():
    print(f"Current working directory: {os.getcwd()}")

    if power_cycle() is None:
        return False # Return false if power cycle has failed.

    # Start the device operations in a separate thread
    global device_thread
    device_thread = threading.Thread(target=device_operations)
    device_thread.start()

    # Print that Joulescope started in another thread.
    print("Joulescope started...")
    return True # Return True to indicate success.

# Function to save backups in the ResultBackups directory
def save_backup(file_path, category="joulescope"):
    """
    Save a backup of the file in the ResultBackups directory under the specified category.
    """
    # Define the base ResultBackups directory
    base_dir = "ResultBackups"

    # Check if the ResultBackups directory exists
    if not os.path.exists(base_dir):
        print(f"Error: {base_dir} directory does not exist. Backup not saved.")
        return None  # Return None to propagate error(s) to caller.

    # Create the category subdirectory if it doesn't exist
    category_dir = os.path.join(base_dir, category)
    if not os.path.exists(category_dir):
        os.makedirs(category_dir)  # Allowed to create subdirectories
        print(f"Created category directory: {category_dir}")

    # Define the backup file path
    backup_file_path = os.path.join(category_dir, os.path.basename(file_path))

    try:
        # Copy the file to the backup location
        with open(file_path, "r") as original_file:
            with open(backup_file_path, "w") as backup_file:
                backup_file.write(original_file.read())
        print(f"Backup saved to: {backup_file_path}")
        return backup_file_path  # Return the backup file path on success
    except Exception as e:
        print(f"Error saving backup: {e}")
        return None  # Return None to propagate error(s) to caller.

if __name__ == '__main__':
    joulescope_start()
