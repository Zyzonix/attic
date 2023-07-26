# shelly-pm-python-provider

This script hosts a simple HTTP server with FastAPI/uvicorn.
It retrieves data from a shelly plug to make them requestable for Grafana/Prometheus.

## Installation
```
$ pip3 install uvicorn
```
```
$ pip3 install fastapi
```

And install this system service:
```
[Unit]
Description=FastAPI server for Shelly-PM plug 
Wants=network-online.target
After=network.target network-online.target
StartLimitIntervalSec=0
[Service]
Type=forking
Restart=always
RestartSec=1
User=root
ExecStart=/usr/bin/python3 /root/shelly-pm-python-provider/service.py
[Install]
WantedBy=multi-user.target
```
