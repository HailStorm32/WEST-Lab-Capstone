import numpy as np
import adi 
import matplotlib.pyplot as plt

# Variable declarations
sr = 1e6 # Sample rate
cw = 2.405e9 # Center frequency
samples = 16000

# Setup Rx Pluto 
sdr_rx = adi.Pluto("ip:192.168.2.2")
#sdr_rx.gain_control_mode_chan0 = "fast_attack" for Automatic Gain Control
sdr_rx.gain_control_mode_chan0 = 'manual'
sdr_rx.rx_hardwaregain_chan0 = 70.0
sdr_rx.rx_lo = int(cw)
sdr_rx.sample_rate = int(sr)
sdr_rx.rx_rf_bandwidth = int(sr)
sdr_rx.rx_buffer_size = samples

# Setup Tx Pluto
sdr_tx = adi.Pluto("ip:192.168.2.3")
sdr_tx.sample_rate = int(sr)
sdr_tx.tx_rf_bandwidth = int(sr)
sdr_tx.tx_lo = int(cw)
sdr_tx.tx_hardwaregain_chan0 = 0

def RF_self_test():
    # Test Tx/Rx code
    # Create transmit waveform (QPSK, 16 samples per symbol)
    num_symbols = 1000
    x_int = np.random.randint(0, 4, num_symbols) # 0 to 3
    x_degrees = x_int*360/4.0 + 45 # 45, 135, 225, 315 degrees
    x_radians = x_degrees*np.pi/180.0 # sin() and cos() takes in radians
    x_symbols = np.cos(x_radians) + 1j*np.sin(x_radians) # this produces our QPSK complex symbols
    sample = np.repeat(x_symbols, 16) # 16 samples per symbol (rectangular pulses)
    sample *= 2**14 # The PlutoSDR expects samples to be between -2^14 and +2^14, not -1 and +1 like some SDRs
    
    # FFT of the transmitted signal and PSD calculated
    fft_sample = np.fft.fftshift(np.fft.fft(sample))
    psd = np.abs(fft_sample)**2
    
    # Transmitted peak frequency
    f_axis = np.linspace(-sr/2, sr/2, len(sample))  
    peak_index = np.argmax(psd)
    peak_freq_baseband = f_axis[peak_index]
    peak_freq_Tx = peak_freq_baseband + cw

    # Start the transmitter
    sdr_tx.tx_cyclic_buffer = True # Enable cyclic buffers
    sdr_tx.tx(sample) # start transmitting
    


    # Clear any existing buffer contents
    for i in range (0, 10):
        raw_data = sdr_rx.rx()

    # Receive samples
    rx_samples = sdr_rx.rx()
      
    # Stop transmitting
    sdr_tx.tx_destroy_buffer()
    
    # Calculate power spectral density (frequency domain version of signal)
    psd = np.abs(np.fft.fftshift(np.fft.fft(rx_samples)))**2
    psd_dB = 10*np.log10(psd)
    f = np.linspace(sr/-2, sr/2, len(psd))

    # Compute cross-correlation between rx_samples and sample
    corr = np.correlate(rx_samples, sample, mode='full')
    peak_idx = np.argmax(np.abs(corr))
    peak_value = corr[peak_idx]

    # Calculate the duration of the transmitted signal
    T = len(sample) / sr  # signal duration in seconds

    # Compute FFT of the received signal
    fft_rx = np.fft.fftshift(np.fft.fft(rx_samples))
    psd_rx = 10 * np.log10(np.abs(fft_rx)**2)
    
    # Create a frequency axis that covers the range based on the sample rate
    freq_axis = np.linspace(-sr/2, sr/2, len(psd_rx))
    
    # Find the index of the maximum power
    peak_index = np.argmax(psd_rx)
    peak_freq_Rx = freq_axis[peak_index] + cw

    # Tx/Rx Single Tone Offset
    offset = np.abs(peak_freq_Tx - peak_freq_Rx)
    
    #Power
    tx_power = np.mean(np.abs(sample)**2)
    tx_power = 10 * np.log10(tx_power)
    rx_power = np.mean(np.abs(rx_samples)**2)
    rx_power = 10 * np.log10(rx_power)
    abs_power = np.abs(tx_power - rx_power)
    
    # Print results
    set_freq = 2405000000
    '''print("")
    print("Set Transmission Frequency:  {:.2f} Hz".format(set_freq))
    print("Transmitted Peak Frequency:  {:.2f} Hz".format(peak_freq_Tx))
    print("Received Peak Frequency:     {:.2f} Hz".format(peak_freq_Rx))
    print("")
    print("Absolute Frequency Offset:   {:.2f} Hz".format(offset))
    print("")
    print("Set Tx Power Gain:           {:.2f} dBm".format(sdr_tx.tx_hardwaregain_chan0))
    print("Transmitted Power:           {:.2f} dBm".format(tx_power))
    print("Received Power:              {:.2f} dBm".format(rx_power))
    print("")
    print("Absolute Power Offset:       {:.2f} dBm".format(abs_power))
    '''
    
    results = {
        "Set Transmission Frequency:  {:.2f} Hz\n".format(set_freq),
        "Transmitted Peak Frequency:  {:.2f} Hz".format(peak_freq_Tx),
        "Received Peak Frequency:     {:.2f} Hz".format(peak_freq_Rx),
        "Absolute Frequency Offset:   {:.2f} Hz".format(offset),
        "Set Tx Power Gain:           {:.2f} dBm".format(sdr_tx.tx_hardwaregain_chan0),
        "Transmitted Power:           {:.2f} dBm".format(tx_power),
        "Received Power:              {:.2f} dBm".format(rx_power),
        "Absolute Power Offset:       {:.2f} dBm".format(abs_power),
        }
    
    return results




#TBD    
def RF_SCuM_test():
    print("TBD")

#Running the tests
results = RF_self_test()
print(results)
#RF_SCuM_test()

# Clean up/remove extraneous print statements
del sdr_rx
del sdr_tx 