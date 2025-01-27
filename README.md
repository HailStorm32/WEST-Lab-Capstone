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
<br>

### Code Development Environment

> **NOTE:** Currently only supports Windows

<br>

#### Cloning The Repo
This repo uses submodules to pull in the APIs for the different test equipment used in the observatory. To clone the repo, while also setting up the submodules, use the following command:

    git clone --recurse-submodules <repository_url>

#### Python Environment Setup

 1. Install **Python 3.10.11** or greater
 2. Navigate to the `Code` directory in a terminal (powershell) and run `setup_env.bat`

After running the script you should now have a `env` directory. 


#### Running in The Virtual Environment
You can run Python scripts within the virtual environment one of three ways:

##### Entering the ENV
In a Command Prompt terminal, in the `Code` directory, run `env\Scripts\activate` to enter the virtual environment. Any commands ran here will be run using the virtual Python interpreter. 

To leave, run `deactivate`

##### Pointing to the ENV
To run scripts in the environment without entering it, you can use the path to virtual Python interpreter like as follows

    env\Scripts\python.exe --version

##### ENV in IDE
You can point your IDE to the virtual Python interpreter, enabling you to run the scripts from the IDE.
The interpreter is located at `Code\env\Scripts\python.exe`
