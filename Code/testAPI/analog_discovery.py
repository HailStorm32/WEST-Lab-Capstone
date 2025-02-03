import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../__VendorAPIs/Diligent')))

import WF_SDK
import testAPI.device_core as device_core

class AnalogDiscovery(device_core.DiligentDevice):
    def __init__(self):
        super().__init__("Analog Discovery 2")
        
    def set_waveform(self):
        #wavegen.generate(self.device, 1, wavegen.function.sine, 0, 1e03, 1, 50, 0, 0, 0)
        print("test print")