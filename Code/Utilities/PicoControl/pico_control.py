# This script is designed to connect to a Raspberry Pi Pico via USB and send commands to it.
# Information about the dev environment: https://www.raspberrypi.com/documentation/microcontrollers/c_sdk.html
import serial
import time
import os  # Added for OS detection


def connect_to_pico(port=None, baudrate=115200, timeout=1):
    """
    Connect to the Raspberry Pi Pico via USB.

    Args:
        port (str): The COM port or device path (e.g., 'COM3' or '/dev/ttyUSB0').
        baudrate (int): The baud rate for the serial connection.
        timeout (int): Timeout for the serial connection in seconds.

    Returns:
        serial.Serial: The connected serial object.
    """
    if port is None:
        # Detect the default port based on the operating system
        if os.name == 'nt':  # Windows
            port = 'COM12'  # Replace with the default COM port for Windows
        elif os.name == 'posix':  # Linux/Unix
            port = '/dev/ttyACM1'  # Replace with the default device path for Linux
        else:
            raise EnvironmentError("Unsupported operating system")

    try:
        pico_serial = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        time.sleep(2)  # Wait for the connection to initialize
        print(f"Connected to Pico on {port}")
        return pico_serial
    except serial.SerialException as e:
        print(f"Failed to connect to Pico: {e}")
        return None


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
            pico_serial.write(command.encode('ascii') + b'\n')
            pico_serial.flush()  # Ensure the command is sent immediately
            print(f"Command sent: {command}")
            time.sleep(0.1)  # Wait for the command to be processed

            # Read response (if any)
            response = pico_serial.readline().decode('ascii').strip()
            #print(f"Response: {response}")
        except serial.SerialException as e:
            print(f"Failed to send command: {e}")
    else:
        print("Serial connection is not open.")

# The following functions are used only for development and testing purposes
def send_all_commands(pico_serial):
    """
    Send a long series of commands to the Raspberry Pi Pico in the specified order.
    The wavegen is changed then the two scopes change to the same channel as the wavegen.

    Args:
        pico_serial (serial.Serial): The connected serial object.
    """
    for i in range(32):  # Loop from 0 to 31
        for prefix in [2,1,0]:  # Iterate over the prefixes in the specified order
            command = f"{prefix}_{i}"
            send_command_to_pico(pico_serial, command)
            time.sleep(0.1)  # Add a small delay between commands to avoid overwhelming the Pico

def send_search(pico_serial):
    """
    Send a long series of commands to the Raspberry Pi Pico in the specified order.
    The wavegen is changed then the two scopes change to the same channel as the wavegen.

    Args:
        pico_serial (serial.Serial): The connected serial object.
    """
    for i in range(31):  # Loop from 0 to 31
        command1 = f"{2}_{i}"
        send_command_to_pico(pico_serial, command1)
        for prefix in [1, 0]:  # Iterate over the prefixes in the specified order
            for i in range(16):  # Loop from 0 to 31
                input("Press Enter to execute the next set of commands...")  # Wait for user key press
                command = f"{prefix}_{i}"
                send_command_to_pico(pico_serial, command)





# Example usage:
if __name__ == "__main__":
    # Replace 'COM3' with the appropriate port for your system
    pico_port = None  # Automatically detect the port based on the OS

    # Connect to the Pico and send commands
    pico = connect_to_pico(port=pico_port)
    try:
        if pico:
            while True:
                
                user_command = input("Enter a command to send to the Pico (or type 'exit' to quit): ")
                if user_command.lower() == 'exit':
                    print("Exiting command loop.")
                    break
                send_command_to_pico(pico, user_command)
            print("Failed to establish a connection to the Pico.")
    finally:
        if pico and pico.is_open:
            pico.close()
            print("Serial connection closed.")