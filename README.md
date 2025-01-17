# ProcurveParse

Python script used to connect to and parse configuration and statistics from procurve switches.
Code was written based on CLI commands and output structure of modern HP/Aruba ArubaOS switches(5400R, 2930F|M, etc).  Older models might not work properly.

## Getting Started

The script is pretty simple to run, and only requires a CSV called switches.csv in the same folder as the script.
The username and password is stored in the script under the netmiko connect section.  I typically edit the username and password and then remove once I'm done running the script.
Environment Variables, Input|Getpass, or some other method could be used if security is a concern.

### Prerequisites

The script utilizes the netmiko library to connect to and manipulate devices, as well as the ttp library to parse the running config

pip install -r requirements.txt
