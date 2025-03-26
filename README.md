## About

### Summary
This repo houses the code, board files, CAD files and documents for the SCuM observatory.

The SCuM observatory is designed as a portable platform that accommodates a SCuM breakout board alongside various measurement devices. These devices provide direct access to the SCuM’s I/O, enabling power control and monitoring, digital and analog pin stimulation/measurement, RF stimulation/measurement, and programming. All communication with the observatory, including control of its measurement devices, occurs through a single USB cable. A Python scripting interface is used for high-level interactions with the observatory and its hardware.


### Contributors
| Name                  |
|-----------------------|
| [Alex Jain](https://github.com/ajainPSU)   |
| [Demetri Van Sickle](https://github.com/HailStorm32) |
| [John Yang](https://github.com/yan7-psu)  |
| [Mitch Montee](https://github.com/mmontee)  |
|[Nate Sjullie](https://github.com/nsjullie) |


<br>

<br>

## Setup

### Pre-Setup
You will need to install the following programs

 - [Git](https://git-scm.com/downloads/win)
 - Python 3.10.11 or greater
 - [Embedded Studio for ARM (legacy)](https://www.segger.com/downloads/embedded-studio/#ESforARM) **version 5.70a**
	 > Needed for the nRF driver
 -   [WaveForms](https://digilent.com/reference/software/waveforms/waveforms-3/start) 
	 > NOTE: Needs to be installed to `C:\Program Files (x86)\Digilent`
 - [Windows Driver for Adalm-Pluto SDR](https://wiki.analog.com/university/tools/pluto/drivers/windows)
   	 > The observatory is currently setup to operate under Windows OS. Future work may be done to adapt to other operatings systems.
- [insert other programs]

### Code Environment

> **NOTE:** Currently only supports Windows

#### 1. Cloning The Repo
This repo uses submodules to pull in the APIs for the different test equipment used in the observatory. To clone the repo, while also setting up the submodules, use the following command:

    git clone --recurse-submodules https://github.com/HailStorm32/WEST-Lab-Capstone.git

#### 2. Run Setup Script
Navigate to the `Code` directory in a terminal (powershell) and run `setup_env.bat`

This script will setup the python virtual environment and directories

After running the script you should now have a `env` directory. 

#### 3.  Running in The Virtual Environment
You can run Python scripts within the virtual environment one of three ways:

##### Entering the ENV
In a Command Prompt terminal, in the `Code` directory, run `env\Scripts\activate` to enter the virtual environment. Any commands ran here will be run using the virtual Python interpreter. 

To leave, run `deactivate`

##### Pointing to the ENV
To run scripts in the environment without entering it, you can use the path to virtual Python interpreter like as follows

    env\Scripts\python.exe path/to/script.py

##### ENV in IDE
You can point your IDE to the virtual Python interpreter, enabling you to run the scripts from the IDE.
The interpreter is located at `Code\env\Scripts\python.exe`
