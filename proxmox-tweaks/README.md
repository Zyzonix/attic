# Proxmox Tweaks

This installer will install a script that will automatically remove the subscription badge from ProxmoxVE and ProxmoxBS. Therefore a crontab under ```/etc/cron.daily``` named ```proxmox-tweaks``` will be installed to run the script daily.

Download installer on PBS/PVE:
```
$ wget https://raw.githubusercontent.com/Zyzonix/attic/main/proxmox-tweaks/install-proxmox-tweaks.sh
```

Run the install script:
```
$ bash install-proxmox-tweaks.sh
```

You will be asked for PVE/PBS, just enter it.
Finally remove the installer:
```
$ rm install-proxmox-tweaks.sh
```

Usually there is no update required.

For any related updates checkout our public Wiki under [FIXES@Brecht](https://fixes.brecht-schule.hamburg/).