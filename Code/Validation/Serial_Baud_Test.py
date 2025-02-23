import serial
import serial.tools.list_ports
import time

# List of common baud rates to test
COMMON_BAUD_RATES = [
    300, 1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200, 230400, 460800, 921600
]

TEST_MESSAGE = b"TEST12345"  # Test message to send

def find_serial_port():
    """ List available serial ports and let user choose one. """
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No serial ports found.")
        return None

    print("Available Serial Ports:")
    for i, port in enumerate(ports):
        print(f"{i}: {port.device} - {port.description}")

    choice = int(input("Select a serial port (number): "))
    return ports[choice].device if 0 <= choice < len(ports) else None

def test_baud_rate(port, baud_rate):
    """ Test a single baud rate for sending and receiving data correctly. """
    try:
        with serial.Serial(port, baud_rate, timeout=1) as ser:
            time.sleep(0.1)  # Allow time for the port to settle
            
            # Flush buffers
            ser.reset_input_buffer()
            ser.reset_output_buffer()

            # Send test message
            ser.write(TEST_MESSAGE)
            time.sleep(0.1)  # Give time for the data to be sent

            # Read response
            received = ser.read(len(TEST_MESSAGE))

            # Check if received data matches sent data
            return received == TEST_MESSAGE
    except serial.SerialException as e:
        print(f"Error testing baud rate {baud_rate}: {e}")
        return False

def find_best_baud_rate():
    """ Scan through baud rates and find a working one. """
    port = find_serial_port()
    if not port:
        return

    print(f"Testing serial device on {port}...\n")

    test_results = []
    for baud in COMMON_BAUD_RATES:
        success = test_baud_rate(port, baud)
        test_results.append({ 'test': f'{baud}', 'pass': success })
        print(f"{baud} {'True' if success else 'False'}")

    return test_results

if __name__ == "__main__":
    result = find_best_baud_rate()
