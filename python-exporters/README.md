# Python Exporters

The exporters in this repository were developed to be run on a Linux container, the following commands are prepared for ```systemd```-based distributions. 

**Current exporters:**
Name | Type of use
---|---
[Watchdog - Prometheus](#exporter-for-watchdog-for-prometheus) | Monitor connection to any server with ping and save data to Prometheus
[Watchdog - MySQL](#exporter-for-watchdog-for-mysql) | Monitor connection to any server with ping and save data to MySQL
[Shelly - Prometheus](#exporter-for-shellypm-plug-for-prometheus) | Monitor ShellyPM, power usage ans Shelly system statistics and save data to Prometheus
[Shelly - MySQL](#exporter-for-shellypm-plug-for-mysql) | Monitor ShellyPM, power usage ans Shelly system statistics and save data to MySQL
[Weatherstation - Prometheus](#exporter-for-rpi-weatherstation) | Monitor [rpi-weatherstation](https://github.com/Zyzonix/rpi-weatherstation)
[Weatherstation - MySQL](#exporter-for-rpi-weatherstation) | Monitor [rpi-weatherstation](https://github.com/Zyzonix/rpi-weatherstation) and save data to MySQL
[Radiation - MySQL](#exporter-for-geiger-counter-sen0463-for-mysql) | Monitor DFRobot Geiger Counter SEN0463 and save data to MySQL

## Exporter for watchdog for Prometheus
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
 - Download ```watchdog2prometheus.py``` and ```watchdog-prometheus-exporter.service``` 
 - Move the service file to the correct directory
```
mv /root/python-exporters/watchdog-prometheus-exporter.service /etc/systemd/system
```  
 - Edit ```watchdog2prometheus.py```: Set ```SERVERIP``` to the IP on which the webbserver should bind on.
 - **And customize ```URLSTOPING``` for the servers that should be pinged**: It's recommended to add a ping to your firewall/router to verify the functionality of the script. This ping then should be more or less next to 1ms.
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

## Exporter for watchdog for MySQL
 - Internet connection monitor, checks ping to any webserver and provides the output in milliseconds
### Installation

The installation process is quite easy:

 - Create directories:
```
mkdir -p /root/python-exporters/
```
 - Download ```watchdog2mysql.py``` and ```watchdog-mysql-exporter.service``` 
 - Move the service file to the correct directory
```
mv /root/python-exporters/watchdog-mysql-exporter.service /etc/systemd/system
```  
 - Edit ```watchdog2mysql.py```: **customize ```URLSTOPING``` for the servers that should be pinged**: It's recommended to add a ping to your firewall/router to verify the functionality of the script. This ping then should be more or less next to 1ms.
 - Additionally check if the python-packages ```ping3``` and ```mysql.connector``` are installed, if not, a debian package of both is provided in ```packages/```.
 - Enable and start the service
```
systemctl enable watchdog-mysql-exporter.service
```
```
systemctl start watchdog-mysql-exporter.service
```
 - Check the current output with
```
journalctl -r -u watchdog-mysql-exporter.service
``` 

## Exporter for ShellyPM Plug for Prometheus

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

## Exporter for ShellyPM Plug for MySQL

### Installation

The installation process is quite easy:

 - Create directories:
```
mkdir -p /root/python-exporters/
```
 - Download ```shelly2mysql.py``` and ```shelly-mysql-exporter.service``` 
 - Move the service file to the correct directory
```
mv /root/python-exporters/shelly-mysql-exporter.service /etc/systemd/system
```
 - Install the ```python3-mysql-connector``` package from ```/packages/```  
 - Edit ```shelly2mysql.py```: Set ```SHELLYURL``` to the URL of the ShellyPlug that should be monitored.
 - Configure the MySQL server and paste the required data to the static variables in the header section of this script. Required are ```MYSQLHOST```, ```MYSQLDATABASENAME```, ```MYSQLTABLENAME```, ```MYSQLUSER``` and ```MYSQLPW```.
 - Enable and start the service
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

**Disclaimer: the services and scripts for rpi-weatherstation were developed to be run on a Raspberry Pi. Some scripts might contain the Pi's default user pi as user!**

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
## Exporter for Geiger Counter SEN0463 for MySQL

Script is designed to request data from DFRobots SEN0463 Geiger Counter: [wiki.dfrobot.com - SKU_SEN0463 Gravity Geiger Counter](https://wiki.dfrobot.com/SKU_SEN0463_Gravity_Geiger_Counter_Module)

### Installation

The installation process is quite easy:

 - Create directories:
```
mkdir -p /opt/python-exporters/
```
 - Download ```radiation2mysql.py``` and ```radiation-mysql-exporter.service``` 
 - Move the service file to the correct directory
```
mv /opt/python-exporters/radiation-mysql-exporter.service /etc/systemd/system
```
 - Install the ```python3-mysql-connector``` package from ```/packages/``` and install the package required for the GPIO communication: ```python3-rpi-lgpio```
 - Configure the MySQL server and paste the required data to the static variables in the header section of this script. Required are ```MYSQLHOST```, ```MYSQLDATABASENAME```, ```MYSQLTABLENAME```, ```MYSQLUSER``` and ```MYSQLPW```.
 - Enable and start the service
```
systemctl enable radiation-mysql-exporter.service
```
```
systemctl start radiation-mysql-exporter.service
```  
 - Check the current output with
```
journalctl -r -u radiation-mysql-exporter.service
```