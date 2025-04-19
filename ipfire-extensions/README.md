# Extensions for IPFire (The Open Source Firewall)

This directory contains some scripts that can be used as extensions for IPFire. 

URL to IPFire: [ipfire.org](https://ipfire.org)

## openvpn-notifier
The main usecase for this script is to get a notification via email when an OpenVPN-cert will expire in the next 14 days (default setting, to change, view [Configuration](#configuration)). The script will run depending on the directory where this script gets installed.

**A working email configuration in IPFire's webinterface under ```System>Mail Service``` must be present.** The script will source it's mail configuration settings from there! If required a different mail receiver address than the one configured in IPFire's webinterface can be defined, therefore look at [Configuration](#configuration).

### Installation
Download the script to ```/etc/fcron.weekly/```:
```
cd /etc/fcron.weekly/
```
```
wget https://raw.githubusercontent.com/Zyzonix/attic/main/ipfire-extensions/<script>.py
```
Make it executeable:
```
chmod +x /etc/fcron.weekly/<script>.py
```

### Configuration (must be extended in the future)
There are two settings you can set:
  - Setting ```SHOWVALID``` in the head of the script from ```True``` to ```False``` will hide all valid certificates within the email.
  - ```VALIDITYDAYS``` defines the number of days left until expiring before sending a notification.
  - ```EMAILRECEIVER``` defines a different email receiver than the one configured in IPFire's webinterface (for example when this script should send it's notification to a ticket system) 
