import sys
import os
from tkinter.dialog import DIALOG_ICON
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../__VendorAPIs/Diligent')))

from WF_SDK import logic, pattern
import testAPI.device_core as device_core
import matplotlib.pyplot as plt

class DigitalDiscovery(device_core.DiligentDevice):
    def __init__(self,DIO_I= 0,DIO_O= 24, buffer_size=4096,):
        super().__init__("Digital Discovery")
        self.DIO_I= DIO_I
        self.DIO_O= DIO_O
        self.buffer_size = buffer_size

    def log_analyzer(self):
        # initialize the logic analyzer with default settings
        logic.open(self.device,buffer_size=self.buffer_size)

        # set up triggering on DIO0 falling edge
        logic.trigger(self.device, enable=True, channel=self.DIO_I, rising_edge=True)

       # record a logic signal on a DIO channel
        buffer = logic.record(self.device, channel=self.DIO_I)

        # limit displayed data size
        length = len(buffer)
        if length > 10000:
            length = 10000
        self.buffer = buffer[0:length]

        # generate buffer for time moments
        self.time = []
        for index in range(length):
            self.time.append(index * 1e06 / logic.data.sampling_frequency)   # convert time to μs

    def pat_gen(self):
        # generate a 100KHz PWM signal with 30% duty cycle on a DIO channel
        pattern.generate(self.device, channel=self.DIO_O, function=pattern.function.pulse, frequency=100e03, duty_cycle=50)

    def plot(self):
        # plot
        plt.plot(self.time, self.buffer)
        plt.xlabel("time [μs]")
        plt.ylabel("logic value")
        plt.yticks([0, 1])
        plt.show()

    def close(self):
        logic.close(self.device)
        pattern.close(self.device)
        super().close()

