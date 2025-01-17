# ProcurveParse

Python script used to connect to and parse configuration and statistics from procurve switches.
Code was written based on CLI commands and output structure of modern HP/Aruba ArubaOS switches(5400R, 2930F|M, etc).  Older models might not work properly.

## Getting Started

The script is pretty simple to run, and only requires a CSV called switches.csv in the same folder as the script.\
The username and password is stored in the script under the netmiko connect section.  I typically edit the username and password and then remove once I'm done running the script.\
Environment Variables, Input|Getpass, or some other method could be used if security is a concern.

### Prerequisites

The script utilizes the netmiko library to connect to and manipulate devices, as well as the ttp library to parse the running config.

pip install -r requirements.txt


### Usage

Edit the switches.csv file with switch IP(mandatory) and Hostname(optional) fields.
Run script via CLI.  No arguments are necessary.

Script will connect to all devices listed in CSV using concurrency.  I've tested around 50 switches at a time and it completes in about 15 seconds or so.

### Output

The script will generate several files in the folder in which it is run.

DeviceName-IP.csv - This is the ouput CSV file that contains the port configs and statistics\
DeviceName.txt - Text copy of "show run structured"\
DeviceName-module.txt - Output of the show module command\
DeviceName-poe.txt - Output of the poe statistics

