import numpy as np
import adi 
import matplotlib.pyplot as plt
import time
import pandas as pd
import datetime 
import os


# Global Variable declarations
sr = 1e6 # Sample rate
cw = 2.405e9 # Center frequency
samples = 100
num_symbols = 100
samples_per_symbol = 2

timestamped_path = []


# General overall test result storage folder
filepath = "C:/Users/19719/OneDrive/Desktop/scum_test_results/"


def RF_self_test():
    # Setup Rx Pluto 
    sdr_rx = adi.Pluto("ip:192.168.2.2")
    sdr_rx.gain_control_mode_chan0 = "fast_attack" #for Automatic Gain Control
    sdr_rx.rx_lo = int(cw)
    sdr_rx.sample_rate = int(sr)
    sdr_rx.rx_rf_bandwidth = int(sr)
    sdr_rx.rx_buffer_size = num_symbols * samples_per_symbol * 64

    # Setup Tx Pluto
    sdr_tx = adi.Pluto("ip:192.168.2.3")
    sdr_tx.sample_rate = int(sr)
    sdr_tx.tx_rf_bandwidth = int(sr)
    sdr_tx.tx_lo = int(cw)
    sdr_tx.tx_hardwaregain_chan0 = -20   
    pattern = np.array([0, 0, 1, 1]) # Control pattern to simplify determining the bit error rate
    bits = np.tile(pattern, num_symbols // len(pattern))

    # Binary FSK generation
    delta = 100e3
    freqs_per_symbol = np.where(bits == 0, -delta, delta)
    freqs = np.repeat(freqs_per_symbol, samples_per_symbol)
    phase = 2 * np.pi * np.cumsum(freqs) / sr
    sample = np.exp(1j * phase)
    sample *= 2**14

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
    
    # Bit error rate
    # The delay in samples is given by the peak index offset relative to no delay
    delay = peak_idx - (len(sample) - 1)
    if delay < 0:
        delay = 0  # In case of a negative delay, default to 0 for simplicity

    # Align the received signal to the start of the transmitted signal
    rx_aligned = rx_samples[delay:delay+len(sample)]
    
    # Demodulation: Process the received signal symbol by symbol
    estimated_bits = np.zeros(num_symbols)
    
    for i in range(num_symbols):
        block = rx_aligned[i*samples_per_symbol:(i+1)*samples_per_symbol]
        # Get the instantaneous phase of the symbol block
        phase_block = np.angle(block)
        # Unwrap the phase to avoid 2pi discontinuities
        phase_block = np.unwrap(phase_block)
        # Calculate the phase differences between successive samples
        phase_diff_block = np.diff(phase_block)
        # Average the phase difference over the symbol duration
        avg_phase_diff = np.mean(phase_diff_block)
        # Convert the average phase difference to an estimated frequency (Hz)
        f_est = avg_phase_diff * sr / (2 * np.pi)
        # Decision threshold: if the estimated frequency is greater than 0, decide '1'; otherwise, '0'
        
        if f_est > 0:
            estimated_bits[i] = 1
        else:
            estimated_bits[i] = 0


    # Calculate Bit Error Rate (BER)
    bit_errors = np.sum(estimated_bits != bits)
    ber = bit_errors / num_symbols * 100

    # Compute FFT of the received signal
    set_freq = 2405000000
    fft_rx = np.fft.fftshift(np.fft.fft(rx_samples))
    psd_rx = 10 * np.log10(np.abs(fft_rx)**2)
    freq_axis = np.linspace(-sr/2, sr/2, len(psd_rx))
    
    # Find the index of the maximum power
    peak_index = np.argmax(psd_rx)
    peak_freq_Rx = freq_axis[peak_index] + cw

    # Tx/Rx Single Tone Offset
    offset = np.abs(peak_freq_Tx - peak_freq_Rx)
    
    # Power
    tx_power = 10 * np.log10(np.mean(np.abs(sample)**2))
    rx_power = 10 * np.log10(np.mean(np.abs(rx_samples)**2)) + 30 + np.abs(sdr_tx.tx_hardwaregain_chan0)
    abs_power = np.abs(tx_power - rx_power)   
    
    if(ber != 0.00):
        value = {'name': 'Bit-Error-Rate', 'value': ber}
        results = {'sub-test': 'Radio(RF)', 'pass': False, 'values': value}
        #print(value)
        #return results
    
    else:
        values =[ {'name': 'Bit-Error-Rate (BER)', 'value': ber},
        {'name': 'Set Transmission Frequency', 'value': set_freq},
        {'name': 'Transmitted Peak Frequency', 'value': peak_freq_Tx},
        {'name': 'Received Peak Frequency', 'value': peak_freq_Rx},
        {'name': 'Absolute Frequency Offset', 'value': offset},
        {'name': 'Set Tx Power Gain', 'value': sdr_tx.tx_hardwaregain_chan0},
        {'name': 'Transmitted Power', 'value': tx_power},
        {'name': 'Received Power', 'value': rx_power},
        {'name': 'Absolute Power Offset', 'value': abs_power}]

        results = [{'sub-test': 'Radio(RF)', 'pass': True, 'values': values}]       
        #print(values)
        return results    
   
    # Demo code of print statements and plots
    '''
    # Create a figure and three subplots (stacked vertically)
    fig, axs = plt.subplots(2, 1, figsize=(10, 4), sharex=True)
    
    # Plot the sample waveform on the first subplot
    axs[0].plot(bits[0:100])
    axs[0].set_title('Transmitted Bits')
    axs[0].set_ylabel('Amplitude')
    
    # Plot the estimated bits on the third subplot
    axs[1].plot(estimated_bits[0:100])
    axs[1].set_title('Estimated Bits')
    axs[1].set_ylabel('Bit Value')
    axs[1].set_xlabel('Sample Index')

    # Adjust layout so titles and labels don't overlap
    plt.tight_layout()

    # Display the plot
    plt.show()
    
    print("")
    print("Set Transmission Frequency:  {:.2f} Hz".format(set_freq))
    print("Transmitted Peak Frequency:  {:.2f} Hz".format(peak_freq_Tx))
    print("Received Peak Frequency:     {:.2f} Hz".format(peak_freq_Rx))
    print("")
    print("Absolute Frequency Offset:   {:.2f} Hz".format(offset))
    print("")
    print("Set Tx Power:                {:.2f} dB".format(sdr_tx.tx_hardwaregain_chan0))
    print("Transmitted PSD:             {:.2f} dB/Hz".format(tx_power))
    print("Received PSD:                {:.2f} dB/Hz".format(rx_power))
    print("")
    print("Absolute Power Offset:       {:.2f} ".format(abs_power))
    print("")
    print("Bit-Error-Rate (BER):        {:.2f} %".format(ber)) 
    '''

    # Clean up/remove extraneous print statements
    del sdr_rx
    del sdr_tx    
    
    #return results

   
def RF_SCuM_test(path):
    # Setup Rx Pluto 
    sdr_rx = adi.Pluto("ip:192.168.2.2")
    sdr_rx.gain_control_mode_chan0 = "fast_attack"  # for Automatic Gain Control
    sdr_rx.rx_hardwaregain_chan0 = 70.0
    sdr_rx.rx_lo = int(cw)
    sdr_rx.sample_rate = int(2e6)
    sdr_rx.rx_rf_bandwidth = int(sr)
    sdr_rx.rx_buffer_size = int(2e6)

    # Clear any potential data in the buffer
    for i in range(0, 10):
        raw_data = sdr_rx.rx()

    # Receive data
    data = sdr_rx.rx()
    if data.size == 0:
        print("Warning: Received empty data from sdr_rx.rx()")
        return [{'sub-test': 'RF Test', 'pass': False, 'values': [{'name': 'Error', 'value': 'No data received'}]}]

    # Reshape data if necessary
    if len(data.shape) == 1:
        data = data.reshape(-1, 1)  # Convert to 2D array with one column

    # Create DataFrame
    df = pd.DataFrame(data)

    # Ensure the DataFrame has at least one column
    if df.shape[1] < 1:
        print("Warning: DataFrame has no columns")
        return [{'sub-test': 'RF Test', 'pass': False, 'values': [{'name': 'Error', 'value': 'Invalid data structure'}]}]

    # Access the first column of the DataFrame
    signal = df.iloc[:, 0].values

    # Create timestamped data folder
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    data_path = os.path.join(path, now)
    os.makedirs(data_path, exist_ok=True)

    # Write data to timestamped data folder
    csv_path = os.path.join(data_path, "results.csv")
    df.to_csv(csv_path, index=False)

    # Use DataFrame to create PSD .png file
    image_path = os.path.join(data_path, "PSD.png")
    fs = sdr_rx.sample_rate

    plt.figure(figsize=(8, 4))
    plt.psd(signal, NFFT=1024, Fs=fs)
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('PSD [dB/Hz]')
    plt.title('PSD of SCuM')
    plt.tight_layout()
    plt.savefig(image_path)
    plt.close()

    # Kill Pluto Rx
    del sdr_rx

    # Return results
    return [{'sub-test': 'RF Test', 'pass': True, 'values': [{'name': 'PSD Image', 'value': image_path}]}]


def end_test():
    # CSV path
    data_path = timestamped_path
    csv_path = data_path + "/results.csv"    
    
    # Image path
    image_path = data_path + "/PSD.png"

    # Create the df from the csv
    df = pd.read_csv(csv_path)
    
    signal = df.iloc[:, 1].values 
    fs = sr 
    
    plt.figure(figsize=(8,4))
    plt.psd(signal, NFFT=1024, Fs=fs)
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('PSD [dB/Hz]')
    plt.title('PSD of SCuM')
    plt.tight_layout()
    
    plt.savefig(image_path)
    plt.close()
    
    # Return filepath to .png file
    return image_path
    

# Running the tests
#results = RF_self_test()
#RF_self_test()
#image_path = RF_SCuM_test(filepath)
#print(results)