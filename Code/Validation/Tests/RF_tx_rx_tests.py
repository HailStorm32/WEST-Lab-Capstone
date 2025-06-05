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

    global fs 
    sdr_rx.gain_control_mode_chan0 = "fast_attack"  # for Automatic Gain Control
    sdr_rx.rx_lo = int(2.3808e9)
    sdr_rx.sample_rate = int(5e6)
    sdr_rx.rx_rf_bandwidth = int(1.6e6)
    sdr_rx.rx_buffer_size = int(1.6e6)
    fs = sdr_rx.sample_rate

    # Raw data (rd) and LUT Values (lv) dictionaries
    rd_data = {}
    lv_data = {}


    # Clear any potential data in the buffer
    for i in range(0, 10):
        raw_data = sdr_rx.rx()

    # Course loop
    coarse = 23
    fine = 0
    for i in range(7):
        
        mid = 0       
        # Mid loop
        for i in range(18):
            print("SCuM Radio Setting: ", coarse, ", ", mid, ", ", fine)
            # Update of df header name to match triplet DAC values for RF sweep
            df_header = f"{coarse}, {mid}, {fine}"

            # Receive the data
            received_data = sdr_rx.rx()
            if received_data.size == 0:
                print("Warning: Received empty data from sdr_rx.rx() Channel 1")
                return False
            
            # Put raw data to rd dataframe
            #rd_df[df_header] = received_data
            rd_data[df_header] = received_data

            # FFT the data
            fft = np.fft.fft(received_data)
            freqs = np.fft.fftfreq(len(received_data), 1/fs)  # fs is the sampling rate
            max_index = np.argmax(np.abs(fft))                # use magnitude
            max_freq = freqs[max_index] + sdr_rx.rx_lo  # Add the LO frequency to get the actual frequency       

            # Put the max_freq data to lv dataframe
            lv_data[df_header] = max_freq

            # Increment values and wait for the next tone to transmit
            mid += 1
            sdr_rx.rx_lo += 800000
            wait_for_trigger(handle)

        coarse += 1
        sdr_rx.rx_lo + 600000 #Increment the LO to match the sweep values on SCuM

    """ rd_df = pd.DataFrame.from_dict(rd_data, orient='columns')
    lv_df = pd.DataFrame([lv_data])  # one row of LUT values

    # Create timestamped data folder
    global timestamped_path
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    timestamped_path = os.path.join(default_results_path, now)
    os.makedirs(timestamped_path, exist_ok=True)

    # Write data to timestamped data folder
    rd_csv_path = os.path.join(timestamped_path, "results.csv")
    lv_csv_path = os.path.join(timestamped_path, "lut_values.csv")
    rd_df.to_csv(rd_csv_path, index=False)
    lv_df.to_csv(lv_csv_path, index=False)   

    # Plot the LUT
    # Use DataFrame to create PSD .png file
    image_path = os.path.join(timestamped_path, "LUT.png")
    plt.figure(figsize=(8, 4))

    # Get data from LUT df
    x_labels = lv_df.columns.tolist()
    x_labels = [label.replace(', ', '\n') for label in lv_df.columns.tolist()]
    y_values = lv_df.iloc[0].values 
    y_values = y_values / 1e9

    # Plotting
    plt.scatter(x_labels, y_values)  
    plt.xlabel('SCuM RF Sweep Triplet DAC Values\nCoarse\nMid\nFine')
    plt.ylabel('Frequency (GHz)')
    plt.title('Look-up-table (LUT) of SCuM Radio Values')
    step = 9
    plt.xticks(
        ticks=range(0, len(x_labels), step),
        labels=[x_labels[i] for i in range(0, len(x_labels), step)],
        rotation=0
    )
    plt.tight_layout()
    plt.savefig(image_path)
    plt.close() """

    # Kill Pluto Rx
    del sdr_rx

    return True

    
def RF_end_test():
    # Use DataFrame to create PSD .png file
    #image_path = os.path.join(timestamped_path, "SCuM_LUT.png")
    image_path = "Users\19719\WEST-Lab-Capstone\Code\ResultBackups\PlutoResults\2025-06-04_08-43-43\LUT.png"

    # Return results
    return [{'sub-test': 'RF Test', 'pass': True, 'values': [{'name': 'PSD Image', 'value': image_path}]}]


