import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../__VendorAPIs/Diligent')))
from WF_SDK import device as diligent_device

class DiligentDevice():
    """
    @brief A class to represent a Diligent device.
    
    This class provides basic operations for a Diligent device.
    """

    def __init__(self, device_name):
        """
        @brief Initializes the DiligentDevice with the given device name.
        
        @param device_name The name of the device to open.
        """
        self.device = diligent_device.open(device_name)

    def close(self):
        """
        @brief Closes the connection to the device.
        
        This method closes the connection to the device using the `diligent_device.close` method.
        
        @return None
        """
        diligent_device.close(self.device)

    def get_device_temperature(self):
        """
        @brief Gets the temperature of the device.
        
        @return The temperature of the device.
        """
        return diligent_device.get_temperature(self.device)
