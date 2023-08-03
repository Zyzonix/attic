# wolserver 

Tries to wakeup servers via Wake on LAN. Additionally provides a webserver to manually wakeup servers, CLI is also possible.

We designed this script to be run on a Raspberry Pi. After a powerloss our UPS shut downs all our virtual hosts. Unfortunately it doesn't provide a feature to wake up devices when power is back. Our Raspberry Pi is not connected to the UPS so it shuts down on powerloss and reboots if power is back. When powered back on this script then tries to wake up our virtual hosts via Wake-on-LAN.


**Remind to configure WoL properly on all machines that should be waked up! (Wake-on-LAN: g)**
Those hosts must also be in the same network!
Additionally this scripts can only be executed on Linux!

## Installation
Install to:
```
/opt/wolserver
```

Copy executeable from ```/opt/wolserver/wolserver``` to ```/usr/bin/wolserver``` and download the required package:
```
sudo cp /opt/wolserver/wolserver /usr/bin/wolserver
```
```
sudo apt install wakeonlan
```
Create log directories:
```
sudo mkdir -p /var/log/wolserver/wakeup/
```
```
sudo mkdir -p /var/log/wolserver/webclient/
```
As long as you're running this script as root there are no adjustments concerning permissions required otherwise adjust the permissions that this script can access the log directory.
Move system-services to it's correct directories and enable/start them:
```
sudo mv /opt/wolserver/wolserver-http.service /etc/systemd/system
```
```
sudo mv /opt/wolserver/wolserver-wakeup.service /etc/systemd/system
```
```
sudo systemctl start wolserver-http.service
```
```
sudo systemctl enable wolserver*
```
From now on all servers (entries in server.ini) will be waked up after reboot/startup.

## Configuration
There are two main config files: config.ini and server.ini
Within the last one all servers that should be waked up are defined along this scheme:
**Server entries format:**
```
[HOSTNAME]
mac = MACADDRESS 
autowakeup = True/False
ip = IPADDRESS
```
```mac``` and ```autowakeup``` are required, ```ip``` is optional.
```HOSTNAME``` must be uppercase!

The following values are hardcoded at the beginning of the main python file:
**General configuration:**
Key | Setting
---|---
```WAKEUPINTERVAL``` | Defines the wakeup interval in seconds
```BASEDIR``` | Directory where the main python file is
```SERVERSPATH``` | Path to ```servers.ini```, main config file for hosts to wakeup
```LOGFILEDIR``` | Directory where the log file should be saved to (Remind to create this directory!)

**Mail configuration:**
Key | Setting
---|---
```AUTH``` | (```True```/```False```) En- or disable authentication
```EMAILRECEIVER``` | If not empty: Email address where a confirmation mail will be send to
```EMAILSENDER``` | Address that should be displayed as sender, scheme can be ```Name <email@domain.com>```
```MAILSERVER``` | Hostname of your mail server
```MAILSERVERPORT``` | Port of your mail server (```25```/```465```/```587```)
```MAILUSER``` | Username for user that should send the email
```MAILPASSWORD``` | Password for the configured user

If you do not want to use authentication only ```MAILSERVER```, ```MAILSERVERPORT```, ```EMAILSENDER``` and ```EMAILRECEIVER``` are required. 
If you wish to disable mailing, just leave all values empty (replace with ```""```).

**A wrong/malformed config file can end up in errors!**

## Usage
You can either wakeup registered servers via the webinterface or via CLI:
```
wolserver wakeup <servername>
```
To wakeup all enabled (autowakeup = ```True```) severs run:
```
wolserver wakeup all
```

List registered servers with:
```
wolserver wakeup list
```






