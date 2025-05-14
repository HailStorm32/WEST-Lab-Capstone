import WF_SDK
from config import TRIGGER_PIN_NUM

def wait_for_trigger(device_handle):
    '''
    Wait for a trigger pulse on the specified pin
    '''
    WF_SDK.logic.open(device_handle, buffer_size=10000)

    # Wait for trigger pulse
    WF_SDK.logic.trigger(device_handle, enable=True, channel=TRIGGER_PIN_NUM, rising_edge=True)
    WF_SDK.logic.record(device_handle, channel=TRIGGER_PIN_NUM, )

    # Close logic analyzer
    WF_SDK.logic.close(device_handle)