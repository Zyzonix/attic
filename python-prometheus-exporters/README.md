# Python Prometheus Exporters

The exporters in this repository were developed to be run on a Linux container, the following commands are prepared for ```systemd``-based distributions. 

**Current exporters:**
Name | Type of use
---|---
[Watchdog](exporter-for-watchdog-(internet-connection-monitor)) | Monitor connection to any server with ping
[Shelly](#exporter-for-shellypm-plug) | Monitor ShellyPM, power usage ans Shelly system statistics
[Weatherstation](#exporter-for-rpi-weatherstation) | Monitor [rpi-weatherstation](https://github.com/Zyzonix/rpi-weatherstation)

## Exporter for watchdog (Internet connection monitor)
### Installation

The installation process is quite easy:

 - Create directories:
```
mkdir -p /root/python-prometheus-exporters/
```
```
mkdir -p /var/log/python-prometheus-exporters/
```
 - Download ```watchdog.py``` and ```watchdog-prometheus-exporter.service``` 
 - Move the service file to the correct directory
```
mv /root/python-prometheus-exporters/watchdog-prometheus-exporter.service /etc/systemd/system
```  
 - Edit ```watchdog.py```: Set ```SERVERIP``` to the IP on which the webbserver should bind on. **And customize ```URLSTOPING``` for the servers that should be pinged.**
 - Install required Python packages: ```uvicorn``` and ```fastapi``` (either as ```python3-uvicorn``` and ```python3-fastapi``` or via ```pip3 install fastapi uvicorn```)
 - Additionally check if the python-package ```ping3``` is installed, if not, a debian package is provided in ```packages/```.
 - Enable and start the server
```
systemctl enable watchdog-prometheus-exporter.service
```
```
systemctl start watchdog-prometheus-exporter.service
```
 - Check the current output with
```
journalctl -r -u watchdog-prometheus-exporter.service
``` 

## Exporter for ShellyPM Plug

### Installation

The installation process is quite easy:

 - Create directories:
```
mkdir -p /root/python-prometheus-exporters/
```
```
mkdir -p /var/log/python-prometheus-exporters/
```
 - Download ```shelly.py``` and ```shelly-prometheus-exporter.service``` 
 - Move the service file to the correct directory
```
mv /root/python-prometheus-exporters/shelly-prometheus-exporter.service /etc/systemd/system
```  
 - Edit ```shelly.py```: Set ```SERVERIP``` to the IP on which the webbserver should bind on and ```SHELLYURL``` to the URL of the ShellyPlug that should be monitored.
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

## Exporter for rpi-weatherstation

### Installation

The installation process is quite easy:

 - Create directories:
```
mkdir -p /root/python-prometheus-exporters/
```
```
mkdir -p /var/log/python-prometheus-exporters/
```
 - Download ```weatherstation.py``` and ```weatherstation-prometheus-exporter.service``` 
 - Move the service file to the correct directory
```
mv /root/python-prometheus-exporters/weatherstation-prometheus-exporter.service /etc/systemd/system
```  
 - Edit ```weatherstation.py```: Set ```SERVERIP``` to the IP on which the webbserver should bind on.
 - Install required Python packages: ```uvicorn``` and ```fastapi``` (either as ```python3-uvicorn``` and ```python3-fastapi``` or via ```pip3 install fastapi uvicorn```)
 - Enable and start the server
```
systemctl enable weatherstation-prometheus-exporter.service
```
```
systemctl start weatherstation-prometheus-exporter.service
```
 - Check the current output with
```
journalctl -r -u weatherstation-prometheus-exporter.service
``` 
