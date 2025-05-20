import numpy as np
import adi 
import matplotlib.pyplot as plt
import time
import pandas as pd
import datetime 
import os
from Validation.Tests.helpers import wait_for_trigger



# Global Variable declarations
sr = 1e6 # Sample rate
cw = 2.405e9 # Center frequency
samples = 100
num_symbols = 100
samples_per_symbol = 2

# General overall test result storage folder
default_results_path = os.path.join(os.path.dirname(__file__), '..\\..', 'ResultBackups\\PlutoResults')

def RF_self_test():
    # Setup Rx Pluto 
    try:
        sdr_rx = adi.Pluto("ip:192.168.2.2")
    except OSError as e:
        print(f"Error: {e}. Please ensure the Pluto SDR is connected and accessible.\n\nIf this is the first boot of the SDR, please wait a few minutes for it to initialize and try again.")
        return [{'sub-test': 'Radio(RF)', 'pass': False, 'values': [{'name': 'Error', 'value': str(e)}]}]
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return [{'sub-test': 'Radio(RF)', 'pass': False, 'values': [{'name': 'Error', 'value': str(e)}]}]

    sdr_rx.gain_control_mode_chan0 = "fast_attack" #for Automatic Gain Control
    sdr_rx.rx_lo = int(cw)
    sdr_rx.sample_rate = int(sr)
    sdr_rx.rx_rf_bandwidth = int(sr)
    sdr_rx.rx_buffer_size = num_symbols * samples_per_symbol * 64

    # Setup Tx Pluto
    try:
        sdr_tx = adi.Pluto("ip:192.168.2.3")
    except OSError as e:
        print(f"Error: {e}. Please ensure the Pluto SDR is connected and accessible.\n\nIf this is the first boot of the SDR, please wait a few minutes for it to initialize and try again.")
        return [{'sub-test': 'Radio(RF)', 'pass': False, 'values': [{'name': 'Error', 'value': str(e)}]}]
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return [{'sub-test': 'Radio(RF)', 'pass': False, 'values': [{'name': 'Error', 'value': str(e)}]}]
    
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

    #Clean up values for sig figs
    set_freq = set_freq / 1e9
    peak_freq_Tx = peak_freq_Tx / 1e9
    peak_freq_Rx = peak_freq_Rx / 1e9

       
    
    if(ber != 0.00):
        value = [{'name': 'Bit-Error-Rate', 'value': ber}]
        results = [{'sub-test': 'Radio(RF)', 'pass': False, 'values': value}]
        #print(value)
        return results
    
    else:
        values =[ {'name': 'Bit-Error-Rate (BER)', 'value': ber},
        {'name': 'Set Transmission Frequency (GHz)', 'value': np.round(set_freq, 4)},
        {'name': 'Transmitted Peak Frequency (GHz)', 'value': np.round(peak_freq_Tx, 4)},
        {'name': 'Received Peak Frequency (GHz)', 'value': np.round(peak_freq_Rx, 4)},
        {'name': 'Absolute Frequency Offset (Hz)', 'value': np.round(offset, 1)},
        {'name': 'Set Tx Power Gain (dB)', 'value': sdr_tx.tx_hardwaregain_chan0},
        {'name': 'Transmitted Power', 'value': np.round(tx_power, 3)},
        {'name': 'Received Power', 'value': np.round(rx_power, 3)},
        {'name': 'Absolute Power Offset', 'value': np.round(abs_power, 3)}]

        results = [{'sub-test': 'Radio(RF)', 'pass': True, 'values': values}]       
        #print(values)
        return results    
   
# Clean up/remove extraneous print statements
    del sdr_rx
    del sdr_tx 

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
    
    #return results

   
def RF_SCuM_test(handle):

    # Ensure the ResultsBackups directory exists
    if not os.path.exists(os.path.join(os.path.dirname(__file__), '..\\..', 'ResultBackups')):
        print("Error: The directory 'ResultBackups' does not exist. Please run the setup script to initialize the environment.")
        os.exit(1)

    # Create folder were all the timestamped data will be stored
    elif not os.path.exists(default_results_path):
        os.makedirs(default_results_path)

    # Setup Rx Pluto 
    try:
        sdr_rx = adi.Pluto("ip:192.168.2.2")
    except OSError as e:
        print(f"Error: {e}. Please ensure the Pluto SDR is connected and accessible.\n\nIf this is the first boot of the SDR, please wait a few minutes for it to initialize and try again.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
    
    # Pre-define array of size 10e6
    data = np.zeros(10000000, dtype=np.complex64)

    # Incremental counter for channel hopping
    channel = 1


    #Do-While to iterate through 5 channels
    while(channel < 6):
            #DEBUG print statement
        print(f"Listening to Channel {channel}. Will take a few minutes..")
        # Conditional case statement for adjusting the Pluto LO to accommodate various RF channels
        # and to increment the index of the df for storing the data
        match channel:
            case 1:
                sdr_rx.rx_lo = int(2.4125e9)
                index = 0
            case 2:
                sdr_rx.rx_lo = int(2.4275e9)
                index = 2000000
            case 3:
                sdr_rx.rx_lo = int(2.4425e9)
                index = 4000000
            case 4:
                sdr_rx.rx_lo = int(2.4575e9)
                index = 6000000
            case 5:
                sdr_rx.rx_lo = int(2.4725e9)
                index = 8000000

        sdr_rx.gain_control_mode_chan0 = "fast_attack"  # for Automatic Gain Control
        #sdr_rx.rx_lo = int(cw)
        sdr_rx.sample_rate = int(5e6)
        sdr_rx.rx_rf_bandwidth = int(15e6)
        sdr_rx.rx_buffer_size = int(2e6)
        
        global fs 
        fs = sdr_rx.sample_rate

        # Clear any potential data in the buffer
        for i in range(0, 10):
            raw_data = sdr_rx.rx()

        # Receive data, case statement for indexing data
        match channel:
            case 1:
                received_data = sdr_rx.rx()
                if received_data.size == 0:
                    print("Warning: Received empty data from sdr_rx.rx() Channel 1")
                    return False
                data[index:index + received_data.size] = received_data
            case 2:
                received_data = sdr_rx.rx()
                if received_data.size == 0:
                    print("Warning: Received empty data from sdr_rx.rx() Channel 2")
                    return False
                data[index:index + received_data.size] = received_data
            case 3:
                received_data = sdr_rx.rx()
                if received_data.size == 0:
                    print("Warning: Received empty data from sdr_rx.rx() Channel 3")
                    return False
                data[index:index + received_data.size] = received_data
            case 4:
                received_data = sdr_rx.rx()
                if received_data.size == 0:
                    print("Warning: Received empty data from sdr_rx.rx() Channel 4")
                    return False
                data[index:index + received_data.size] = received_data
            case 5:
                received_data = sdr_rx.rx()
                if received_data.size == 0:
                    print("Warning: Received empty data from sdr_rx.rx() Channel 5")
                    return False
                data[index:index + received_data.size] = received_data
                
        # Wait for trigger pulse
        print("Waiting on SCuM to finish sweep...")
        wait_for_trigger(handle)
        channel += 1


    # Reshape data if necessary
    if len(data.shape) == 1:
        data = data.reshape(-1, 1)  # Convert to 2D array with one column

    # Create DataFrame
    df = pd.DataFrame(data)

    # Ensure the DataFrame has at least one column
    if df.shape[1] < 1:
        print("Warning: DataFrame has no columns")
        return False

    # This is made global just to be able to access it in the RF_end_test function
    # This should be removed once you can read out the signal from the csv file in the RF_end_test function
    global signal
    # Access the first column of the DataFrame
    signal = df.iloc[:, 0].values

    # Create timestamped data folder
    global timestamped_path
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    timestamped_path = os.path.join(default_results_path, now)
    os.makedirs(timestamped_path, exist_ok=True)

    # Write data to timestamped data folder
    csv_path = os.path.join(timestamped_path, "results.csv")
    df.to_csv(csv_path, index=False)   

    # Kill Pluto Rx
    del sdr_rx

    print("Sweeps completed")

    return True

    
def RF_end_test():
    # Use DataFrame to create PSD .png file
    image_path = os.path.join(timestamped_path, "PSD.png")

    #TODO: Parse the CSV file to get the signal data

    plt.figure(figsize=(8, 4))
    plt.psd(signal, NFFT=1024, Fs=fs)
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('PSD [dB/Hz]')
    plt.title('PSD of SCuM')
    plt.tight_layout()
    plt.savefig(image_path)
    plt.close()

    # Return results
    return [{'sub-test': 'RF Test', 'pass': True, 'values': [{'name': 'PSD Image', 'value': image_path}]}]

# Running the tests
#results = RF_self_test()
#RF_self_test()
#image_path = RF_SCuM_test(filepath)
#print(results)
