import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../__VendorAPIs/Diligent')))

from WF_SDK import device, logic, pattern, error   # import instruments

import matplotlib.pyplot as plt   # needed for plotting
from time import sleep            # needed for delays

"""-----------------------------------------------------------------------"""

DIO_O = 24
DIO_I = 0

try:
    # connect to the device
    device_data = device.open()

    """-----------------------------------"""

    # initialize the logic analyzer with default settings
    logic.open(device_data,buffer_size=4096)

    # set up triggering on DIO0 falling edge
    logic.trigger(device_data, enable=True, channel=DIO_I, rising_edge=True)

    # generate a 100KHz PWM signal with 30% duty cycle on a DIO channel
    pattern.generate(device_data, channel=DIO_O, function=pattern.function.pulse, frequency=100e03, duty_cycle=50)

    sleep(1)    # wait 1 second

    # record a logic signal on a DIO channel
    buffer = logic.record(device_data, channel=DIO_I)

    # limit displayed data size
    length = len(buffer)
    if length > 10000:
        length = 10000
    buffer = buffer[0:length]

    # generate buffer for time moments
    time = []
    for index in range(length):
        time.append(index * 1e06 / logic.data.sampling_frequency)   # convert time to μs

    # plot
    plt.plot(time, buffer)
    plt.xlabel("time [μs]")
    plt.ylabel("logic value")
    plt.yticks([0, 1])
    plt.show()

    # reset the logic analyzer
    logic.close(device_data)

    # reset the pattern generator
    pattern.close(device_data)

    """-----------------------------------"""

    # close the connection
    device.close(device_data)

except error as e:
    print(e)
    # close the connection
    device.close(device.data)