# Python Exporters

The exporters in this repository were developed to be run on a Linux container, the following commands are prepared for ```systemd```-based distributions. 

**Current exporters:**
Name | Type of use
---|---
[Watchdog - Prometheus](#exporter-for-watchdog) | Monitor connection to any server with ping
[Shelly - Prometheus](#exporter-for-shellypm-plug) | Monitor ShellyPM, power usage ans Shelly system statistics
[Shelly - MySQL](#exporter-for-shellypm-plug-mysql) | Monitor ShellyPM, power usage ans Shelly system statistics and save data to MySQL
[Weatherstation - Prometheus](#exporter-for-rpi-weatherstation) | Monitor [rpi-weatherstation](https://github.com/Zyzonix/rpi-weatherstation)

## Exporter for watchdog 
 - Internet connection monitor, checks ping to any webserver and provides the output in milliseconds
### Installation

The installation process is quite easy:

 - Create directories:
```
mkdir -p /root/python-exporters/
```
```
mkdir -p /var/log/python-exporters/
```
 - Download ```watchdog.py``` and ```watchdo-exporter.service``` 
 - Move the service file to the correct directory
```
mv /root/python-exporters/watchdog-exporter.service /etc/systemd/system
```  
 - Edit ```watchdog.py```: Set ```SERVERIP``` to the IP on which the webbserver should bind on.
 - **And customize ```URLSTOPING``` for the servers that should be pinged**: It's recommended to add a ping to your firewall/router to verify the functionality of the script. This ping then should be more or less next to 1ms.
 - Install required Python packages: ```uvicorn``` and ```fastapi``` (either as ```python3-uvicorn``` and ```python3-fastapi``` or via ```pip3 install fastapi uvicorn```)
 - Additionally check if the python-package ```ping3``` is installed, if not, a debian package is provided in ```packages/```.
 - Enable and start the server
```
systemctl enable watchdog-exporter.service
```
```
systemctl start watchdog-exporter.service
```
 - Check the current output with
```
journalctl -r -u watchdog-exporter.service
``` 

## Exporter for ShellyPM Plug

### Installation

The installation process is quite easy:

 - Create directories:
```
mkdir -p /root/python-exporters/
```
```
mkdir -p /var/log/python-exporters/
```
 - Download ```shelly2prometheus.py``` and ```shelly-prometheus-exporter.service``` 
 - Move the service file to the correct directory
```
mv /root/python-exporters/shelly-prometheus-exporter.service /etc/systemd/system
```  
 - Edit ```shelly2prometheus.py```: Set ```SERVERIP``` to the IP on which the webbserver should bind on and ```SHELLYURL``` to the URL of the ShellyPlug that should be monitored.
 - Install required Python packages: ```uvicorn``` and ```fastapi``` (either as ```python3-uvicorn``` and ```python3-fastapi``` or via ```pip3 install fastapi uvicorn```)
 - Enable and start the server
```
systemctl enable shelly-prometheus-exporter.service
```
```
systemctl start shelly-prometheus-exporter.service
```  
 - Check the current output with
```
journalctl -r -u shelly-prometheus-exporter.service
```

## Exporter for ShellyPM Plug MySQL

### Installation

The installation process is quite easy:

 - Create directories:
```
mkdir -p /root/python-exporters/
```
```
mkdir -p /var/log/python-exporters/
```
 - Download ```shelly2mysql.py``` and ```shelly-mysql-exporter.service``` 
 - Move the service file to the correct directory
```
mv /root/python-exporters/shelly-mysql-exporter.service /etc/systemd/system
```  
 - Edit ```shelly2mysql.py```: Set ```SERVERIP``` to the IP on which the webbserver should bind on and ```SHELLYURL``` to the URL of the ShellyPlug that should be monitored.
 - Install required Python packages: ```uvicorn``` and ```fastapi``` (either as ```python3-uvicorn``` and ```python3-fastapi``` or via ```pip3 install fastapi uvicorn```)
 - Enable and start the server
```
systemctl enable shelly-mysql-exporter.service
```
```
systemctl start shelly-mysql-exporter.service
```  
 - Check the current output with
```
journalctl -r -u shelly-exporter.service
```

## Exporter for rpi-weatherstation

### Installation

The installation process is quite easy:

 - Create directories:
```
mkdir -p /root/python-exporters/
```
```
mkdir -p /var/log/python-exporters/
```
 - Download ```weatherstation.py``` and ```weatherstation-exporter.service``` 
 - Move the service file to the correct directory
```
mv /root/python--exporters/weatherstation-exporter.service /etc/systemd/system
```  
 - Edit ```weatherstation.py```: Set ```SERVERIP``` to the IP on which the webbserver should bind on.
 - Install required Python packages: ```uvicorn``` and ```fastapi``` (either as ```python3-uvicorn``` and ```python3-fastapi``` or via ```pip3 install fastapi uvicorn```)
 - Enable and start the server
```
systemctl enable weatherstation-exporter.service
```
```
systemctl start weatherstation-exporter.service
```
 - Check the current output with
```
journalctl -r -u weatherstation-exporter.service
``` 
