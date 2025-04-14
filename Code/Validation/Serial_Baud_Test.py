import serial
import serial.tools.list_ports
import time

# List of common baud rates to test
COMMON_BAUD_RATES = [
   300, 9200, 19200, 38400, 57600, 115200, 230400, 460800, 921600
]

TEST_MESSAGE = b"Hello World!"  # Test message to send
PORT = "COM5"

def find_serial_port(port):
    """ Check if the given serial port is valid. """
    ports = [p.device for p in serial.tools.list_ports.comports()]
    if port in ports:
        return port
    print(f"Invalid port: {port}")
    print("Available COM ports:")
    for p in ports:
        print(f" - {p}")
    return None

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
            time.sleep(0.01)  # Give time for the data to be sent

            # Read response
            received = ser.read(len(TEST_MESSAGE))
            #print(received)

            # Check if received data matches sent data
            return received == TEST_MESSAGE
    except serial.SerialException as e:
        print(f"Error testing baud rate {baud_rate}: {e}")
        return False
    
def test_baud_rate_read_only(port, baud_rate):
    msg = b"Hello World!" #local serial msg
    try:
        with serial.Serial(port, baud_rate, timeout=1) as ser:
            time.sleep(0.1)  # Allow time for the port to settle
            
            # Flush input buffer
            ser.reset_input_buffer()

            # Attempt to read expected number of bytes
            received = ser.read(len(msg))
            return received == msg 
    except serial.SerialException as e:
        print(f"Error testing baud rate {baud_rate}: {e}")
        return None

def find_best_baud_rate(port):
    """ Scan through baud rates and find a working one. """
    port = find_serial_port(port)
    if not port:
        return

    print(f"Testing serial device on {port}...\n")

    test_results = []
    for baud in COMMON_BAUD_RATES:
        success = test_baud_rate(port, baud) #change this function original test or read only
        test_results.append({ 'test': f'{baud}', 'pass': success })
        print(f"{baud} {'True' if success else 'False'}")

    return test_results

if __name__ == "__main__":
    result = find_best_baud_rate(port=PORT)
