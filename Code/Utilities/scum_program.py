import serial
import random
import signal
import sys
import datetime

def get_current_time():
  """
  Prints the current time in a human-readable format.
  """
  now = datetime.datetime.now()
  formatted_time = now.strftime("%H:%M:%S")
  return formatted_time

# Serial connections
nRF_ser = None

boot_mode='3wb'
pad_random_payload=False

def signal_handler(signal, frame):
    nRF_ser.reset_input_buffer()
    nRF_ser.close()
    print("\rBye...")
    exit(0)

def scum_program(nrf_com_port, binary_image):

    nRF_port = nrf_com_port

    # Register the signal handler
    signal.signal(signal.SIGINT, signal_handler)

    # Open COM port to nRF
    nRF_ser = serial.Serial(
        port=nRF_port,
        baudrate=250000,
        #timeout = 3,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS)
        
    # Open binary file from Keil
    with open(binary_image, 'rb') as f:
        bindata = bytearray(f.read())
        
    # Need to know how long the binary payload to pad to 64kB
    code_length = len(bindata) - 1
    pad_length = 65536 - code_length - 1

    #print(code_length)

    # Optional: pad out payload with random data if desired
    # Otherwise pad out with zeros - uC must receive full 64kB
    if(pad_random_payload):
        for i in range(pad_length):
            bindata.append(random.randint(0,255))
        code_length = len(bindata) - 1 - 8
    else:
        for i in range(pad_length):
            bindata.append(0)
            
    nRF_ser.reset_input_buffer()       

    # Send the binary data over uart
    print("\rScuM nRF Serial Programmer.\r\n")
    print("\rPress (Ctrl + c) to Exit\r\n")
    nRF_ser.write(bindata)
    # and wait for response that writing is complete
    print(nRF_ser.read_until())
        
    # Display 3WB confirmation message from nRF
    print(nRF_ser.read_until())

    print("\r\nFinished programming.\r\n")

    if nRF_ser is not None:
        print("\rClosing serial port...")
        nRF_ser.reset_input_buffer()
        nRF_ser.close()
    print("\rBye...\n")

    return [{
        'sub-test': 'Program upload',
        'pass': True,
        'values': []
    }]



if __name__ == '__main__':
    scum_program()
    sys.exit(0)