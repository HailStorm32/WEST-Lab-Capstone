'''
This file contains the configuration settings for the validation tests.
'''
import os

########################
# SCuM Serial Configuration
# (COM ports used by SCuM for flashing and serial communication)
########################

SCUM_NRF_COM_PORT = "COM8"  # COM port for nRF board for SCuM "flashing"

SCUM_SERIAL_COM_PORT = "COM11"  # COM port that the SCuM board is connected to for serial communication

PICO_COM_PORT = "COM10"  # COM port for the PICO board for flashing and testing

########################
# SCuM Validation Configuration
# (Configuration settings for scum_validation.py)
########################

AD2_FOR_DIGITAL = False # Set to True if using Analog Discovery 2 in place of the Digital Discovery

TRIGGER_PIN_NUM = 1  # DIO pin on AD2/DD used for the trigger pin (KEEP AT 1, IT IS HARD-CODED IN THE SCUM BINARY)

########################
# Analog Test Configuration
# (Configuration settings for analog_test.py)
########################

MEASUREMENT_CHANNEL_1_1V = 1  # AD2 scope channel for measuring the 1.1V reference voltage
MEASUREMENT_CHANNEL_1_8V = 2  # AD2 scope channel for measuring the 1.8V reference voltage

ACCEPTABLE_VOLTAGE_RANGE_1_1V = [1.0, 1.2]  # Acceptable range (in volts) for the 1.1V reference voltage
ACCEPTABLE_VOLTAGE_RANGE_1_8V = [1.7, 1.9]  # Acceptable range (in volts) for the 1.8V reference voltage

CLOCKS_TO_TEST = [    # List of clocks to test     
    {'name': "HFCLK",   'exp_freq_hz': 20000000,    'tolerance_ppm': 40, 'mux-command': '1_5'},
    {'name': "LFCLK",   'exp_freq_hz': 20000000,    'tolerance_ppm': 40, 'mux-command': '1_15'}
    ]
'''
PPM = ((exp_freq_hz - measured_freq_hz) / exp_freq_hz) * 1_000_000
''' 

#########################
# Joulescope Configuration
# (Used by power_test.py)
#########################
                                    # [min,max]
PWR_USE_ACCEPTABLE_VOLTAGE_RANGE_V = [1.0, 1.3]  # Acceptable range (in volts) for the power supply voltage (inclusive)
PWR_USE_ACCEPTABLE_CURRENT_RANGE_A = [0.00001, 0.1]  # Acceptable range (in Amps) for the power supply current (inclusive)

########################
# Nightly Validation Configuration
# (Configuration settings for nightly_validation.py)
########################
SEND_EMAIL_ON_COMPLETION = False  # Set to True to send email notifications upon completion of the validation tests

# SMTP configuration for sending email notifications (ONLY IF SEND_EMAIL_ON_COMPLETION IS TRUE)
SMTP_SERVER = "smtp.gmail.com"  # SMTP server for sending email notifications
SMTP_PORT = 465  # SMTP port for sending email notifications
SMTP_USERNAME = "email@example.com"  # Username for the SMTP email account
SMTP_PASSWORD = "password_here"  # Password for the SMTP email account
SMTP_SENDER_EMAIL = "email@example.com"  # Sender email address for email notifications

WKHTMLTOPDF_PATH = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"  # Path to the wkhtmltopdf executable for PDF generation

USERS_TO_EMAIL = [  # List of email addresses to send result reports to
    "user@example.com"
]

GIT_DIRECTORY = os.path.join(os.path.dirname(__file__), '../GitTestingRepos/repo_folder/')  # Directory where the Git repository is located

TIME_TO_RUN = "12:00"  # Time of day to run the validation in 24-hour format (e.g., 14:30 for 2:30 PM)
RUN_IN_DEV_MODE = True  # Set to True if running in development mode (bypasses time check)

GIT_BINARY_PATHS = [
    { 'path': os.path.join(GIT_DIRECTORY, "path/to/repo/scum_binary.bin"), 'branch': "branch_name_here", 'lastHash': None },  # Path to the binary file (LEAVE 'lastHash' AS NONE)
]

########################
# Logic (DO NOT EDIT)
########################
#nothing here for now