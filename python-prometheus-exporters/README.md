# Python Prometheus Exporters

## Exporter for ShellyPM Plug

### Installation

This script was developed to be run on a Linux container, the following commands are prepared for ```systemd``-based distributions. 

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
