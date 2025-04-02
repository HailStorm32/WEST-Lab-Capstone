# Functionality: This script connects to a Raspberry Pi Pico via USB, uploads a script, and sends commands to it.
# pip install adafruit-ampy
import serial
import time
import subprocess
import os

def connect_to_pico(port, baudrate=115200, timeout=1):
    """
    Connect to the Raspberry Pi Pico via USB.

    Args:
        port (str): The COM port or device path (e.g., 'COM3' or '/dev/ttyUSB0').
        baudrate (int): The baud rate for the serial connection.
        timeout (int): Timeout for the serial connection in seconds.

    Returns:
        serial.Serial: The connected serial object.
    """
    try:
        pico_serial = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        time.sleep(2)  # Wait for the connection to initialize
        print(f"Connected to Pico on {port}")
        return pico_serial
    except serial.SerialException as e:
        print(f"Failed to connect to Pico: {e}")
        return None

def upload_script_to_pico_with_ampy(port, script_path):
    """
    Upload a Python script to the Raspberry Pi Pico using ampy.

    Args:
        port (str): The COM port or device path (e.g., 'COM3' or '/dev/ttyUSB0').
        script_path (str): The path to the Python script to upload.
    """
    try:
        # Get the absolute path of the script
        script_path = os.path.abspath(script_path)
        print(f"Uploading {script_path} to Pico on {port} as main.py...")
        result = subprocess.run(
            ["ampy", "--port", port, "put", script_path, "/main.py"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"Successfully uploaded {script_path} to Pico as main.py.")
        else:
            print(f"Failed to upload script: {result.stderr}")
    except FileNotFoundError:
        print("ampy is not installed or not found in PATH. Please install it using 'pip install adafruit-ampy'.")

def reset_pico_with_ampy(port):
    """
    Perform a soft reset on the Raspberry Pi Pico using ampy by running a soft reset command.

    Args:
        port (str): The COM port or device path (e.g., 'COM3' or '/dev/ttyUSB0').
    """
    try:
        print("Performing a soft reset on the Pico...")
        # Use 'ampy run' to execute a soft reset command
        result = subprocess.run(
            ["ampy", "--port", port, "run", "import machine; machine.soft_reset()"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("Soft reset successful.")
        else:
            print(f"Failed to perform soft reset: {result.stderr}")
    except FileNotFoundError:
        print("ampy is not installed or not found in PATH. Please install it using 'pip install adafruit-ampy'.")

def send_command_to_pico(pico_serial, command):
    """
    Send a command string to the connected Raspberry Pi Pico and read the response.

    Args:
        pico_serial (serial.Serial): The connected serial object.
        command (str): The command string to send.
    """
    if pico_serial and pico_serial.is_open:
        try:
            # Send command with carriage return and newline
            pico_serial.write(command.encode('ascii') + b'\r\n')
            pico_serial.flush()  # Ensure the command is sent immediately
            print(f"Command sent: {command}")

            # Read response (if any)
            response = pico_serial.readline().decode('utf-8').strip()
            print(f"Response: {response}")
        except serial.SerialException as e:
            print(f"Failed to send command: {e}")
    else:
        print("Serial connection is not open.")

# Example usage:
if __name__ == "__main__":
    # Replace 'COM3' with the appropriate port for your system
    pico_port = 'COM3'
    pico_script = 'main.py'  # Ensure this file exists in the same directory as this script

    # Upload the script to the Pico
    upload_script_to_pico_with_ampy(pico_port, pico_script)

    # Reset the Pico
    reset_pico_with_ampy(pico_port)

    time.sleep(3)  # Add a longer delay to ensure the script starts running

    # Connect to the Pico and send commands
    pico = connect_to_pico(port=pico_port)
    try:
        if pico:
            send_command_to_pico(pico, "scope1_11")
            time.sleep(0.5)  # Add delay
            send_command_to_pico(pico, "scope2_0")
            time.sleep(0.5)  # Add delay
            send_command_to_pico(pico, "wave1_1")
        else:
            print("Failed to establish a connection to the Pico.")
    finally:
        if pico and pico.is_open:
            pico.close()
            print("Serial connection closed.")