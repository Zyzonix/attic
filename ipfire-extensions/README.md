# Extensions for IPFire (The Open Source Firewall)

This directory contains some scripts that can be used as extensions for IPFire. It's recommended to place both scripts under ```/etc/fcron.weekly``` or ```/etc/fcron.monthly```. **A working email configuration in IPFire's webinterface under ```System>Mail Service``` must be present.** The scripts will source their mail configuration settings from there! If a different receiver mail address than IPFire's default is required, have look at [Configuration](#configuration).

URL to IPFire: [ipfire.org](https://ipfire.org)

## openvpn-expiring-notifier
This script sends an email if any OpenVPN certificate will expire in the next 14 days (time can be adjusted) [Configuration](#configuration). If there's no cert expiring, no email will be send. 

## openvpn-unused-notifier
This script sends an email if any OpenVPN certificate is unused for more than 90 days (time can be adjusted), therefore see [Configuration](#configuration). Also here: if there's no cert expiring, no email will be send. 


### Installation
Download the script either to ```/etc/fcron.weekly/``` or ```/etc/fcron.monthly```:
Then enter the directory and make it executeable:
```
chmod +x /etc/<path>/<script>.py
```

### Configuration (must be extended in the future)
The following settings can be adjusted in both scripts:
  - ```EMAILRECEIVER``` defines a different email receiver than the one configured in IPFire's webinterface (for example when this script should send it's notification to a ticket system) 

The following in ```openvpn-unused-notifier```:
  - Setting ```SHOWVALID``` in the head of the script from ```True``` to ```False``` will hide all valid certificates within the email.
  - ```VALIDITYDAYS``` defines the number of days left until expiring before sending a notification.

The following in ```openvpn-expiring-notifier```:
  - ```LASTUSED``` defines the number of days of unusage before sending a notification.
