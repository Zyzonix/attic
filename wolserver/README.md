# wolserver 

Tries to wakeup servers via Wake on LAN. Additionally provides a webserver to manually wakeup servers, CLI is also possible.

We designed this script to be run on a Raspberry Pi. After a powerloss our UPS shut downs all our virtual hosts. Unfortunately it doesn't provide a feature to wake up devices when power is back. Our Raspberry Pi is not connected to the UPS so it shuts down on powerloss and reboots if power is back. When powered back on this script then tries to wake up our virtual hosts via Wake-on-LAN.


**Remind to configure WoL properly on all machines that should be waked up! (Wake-on-LAN: g)**
Those hosts must also be in the same network!
Additionally this scripts can only be executed on Linux!

## Installation
Install to:
```
/etc/wolserver
```

Copy executeable from ```/etc/wolserver/wolserver``` to ```/usr/bin/wolserver```, make it executeable and download the required ```wakeonlan``` package:
```
sudo cp /etc/wolserver/wolserver /usr/bin/wolserver
```
```
sudo chmod +x /usr/bin/wolserver 
```
```
sudo apt install wakeonlan python3-pip
```
Create log directories:
```
sudo mkdir -p /var/log/wolserver/wakeup/
```
```
sudo mkdir -p /var/log/wolserver/webclient/
```
As long as you're running this script as root there are no adjustments concerning permissions required otherwise adjust the permissions that this script can access the log directory.
Move system-services to it's correct directories them:
```
sudo mv /etc/wolserver/wolserver-http.service /etc/systemd/system
```
```
sudo mv /etc/wolserver/wolserver-wakeup.service /etc/systemd/system
```
Then install all required python packages:
```
sudo pip3 install uvicorn fastapi
```
And finally start the webserver:
```
sudo systemctl start wolserver-http.service
```
```
sudo systemctl enable wolserver*
```
From now on all servers (entries in server.ini) will be waked up after reboot/startup.

## Configuration
### wakeup.py
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

Both scripts will try to resolve the local hostname to provide URLs (Web/Email), be sure that your ```/etc/hosts``` is correct!

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

### webclient.py

The following values are hardcoded at the beginning of the main python file:
**General configuration:**
Key | Setting
---|---
```SERVERIP``` | Defines the IP of the server [e.g. ```10.0.100.2```] (default is loopback), change this, otherwise you won't be able to access the webserer via HTTP.
```BASEDIR``` | Directory where the main python file is
```SERVERSPATH``` | Path to ```servers.ini```, main config file for hosts to wakeup
```LOGFILEDIR``` | Directory where the log file should be saved to (Remind to create this directory!)

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

## To-Do
* Move all install instructions to an installation file





