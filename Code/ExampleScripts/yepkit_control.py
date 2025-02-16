'''
Alex Jain - February 10th, 2025

This script provides functionality
to control the Yepkit USB
Switchable Hub. The user can power
cycle individual ports, turn off all
ports, turn on all ports, turn off
individual ports, and turn on individual
ports. The user can also get the serial
number of the Yepkit device.

The script uses the ykushcmd.exe
command line tool provided by Yepkit
to control the USB hub. The ykushcmd.exe
tool must be installed on the system
and accessible in the system PATH.

Note: Used autopep8 tool to keep it
in conjunction with pep8 standards.

Version: 1.1.6
'''

import os
import subprocess
import time


def yepkitcontrol():
    # Function to control Yepkit hub.

    # Path to ykushcmd.exe
    ykushcmd_path = "C:\\Program Files (x86)\\YEPKIT LDA\\ykushcmd\\ykushcmd.exe"

    # Check if ykushcmd.exe exists
    if not os.path.exists(ykushcmd_path):
        print(f"ykushcmd.exe not found: {ykushcmd_path}")
        return

    # Print the current working directory for debugging
    print(f"Current working directory: {os.getcwd()}")

    # User menu to input commands for Yepkit hub.
    menu_options = [
        "1. Power Cycle USB Port 1",
        "2. Power Cycle USB Port 2",
        "3. Power Cycle USB Port 3",
        "4. Turn off all USB ports",
        "5. Turn on all USB ports",
        "6. Turn off USB Port 1",
        "7. Turn off USB Port 2",
        "8. Turn off USB Port 3",
        "9. Turn on USB Port 1",
        "10. Turn on USB Port 2",
        "11. Turn on USB Port 3",
        "12. Get YEPKIT Device Serial Number",
        "13. Exit"
    ]

    while True:
        print("\nYepkit Control Menu")
        print("\n".join(menu_options))

        # Get user input
        userchoice = input("Enter command number: ")

        # Power Cycle USB Port 1
        if userchoice == '1':
            print("Turning off USB Port 1")
            subprocess.run([ykushcmd_path, '-d', '1'], shell=True)
            time.sleep(2)
            print("Turning on USB Port 1")
            subprocess.run([ykushcmd_path, '-u', '1'], shell=True)

        # Power Cycle USB Port 2
        elif userchoice == '2':
            print("Turning off USB Port 2")
            subprocess.run([ykushcmd_path, '-d', '2'], shell=True)
            time.sleep(2)
            print("Turning on USB Port 2")
            subprocess.run([ykushcmd_path, '-u', '2'], shell=True)

        # Power Cycle USB Port 3
        elif userchoice == '3':
            print("Turning off USB Port 3")
            subprocess.run([ykushcmd_path, '-d', '3'], shell=True)
            time.sleep(2)
            print("Turning on USB Port 3")
            subprocess.run([ykushcmd_path, '-u', '3'], shell=True)

        # Turn off all USB ports
        elif userchoice == '4':
            print("Turning off all USB Ports")
            subprocess.run([ykushcmd_path, '-d', 'a'], shell=True)

        # Turn on all USB ports
        elif userchoice == '5':
            print("Turning on all USB Ports")
            subprocess.run([ykushcmd_path, '-u', 'a'], shell=True)

        # Turn off USB Port 1
        elif userchoice == '6':
            print("Turning off USB Port 1")
            subprocess.run([ykushcmd_path, '-d', '1'], shell=True)

        # Turn off USB Port 2
        elif userchoice == '7':
            print("Turning off USB Port 2")
            subprocess.run([ykushcmd_path, '-d', '2'], shell=True)

        # Turn off USB Port 3
        elif userchoice == '8':
            print("Turning off USB Port 3")
            subprocess.run([ykushcmd_path, '-d', '3'], shell=True)

        # Turn on USB Port 1
        elif userchoice == '9':
            print("Turning on USB Port 1")
            subprocess.run([ykushcmd_path, '-u', '1'], shell=True)

        # Turn on USB Port 2
        elif userchoice == '10':
            print("Turning on USB Port 2")
            subprocess.run([ykushcmd_path, '-u', '2'], shell=True)

        # Turn on USB Port 3
        elif userchoice == '11':
            print("Turning on USB Port 3")
            subprocess.run([ykushcmd_path, '-u', '3'], shell=True)

        # Get YEPKIT Device Serial Number
        elif userchoice == '12':
            subprocess.run([ykushcmd_path, '-l'], shell=True)

        # Exit
        elif userchoice == '13':
            print("Exiting Yepkit Control Menu")
            break
        else:
            print("Invalid command.")


# Call the function
yepkitcontrol()
