# Repair MySQL Master/Slave Sync automatically

## Installation
- Download to ```/opt/mysql-addons/```
- Create crontab ```/etc/cron.hourly/repair-mysql-master-slave-sync```
- Make crontab executeable 
- Add Email settings and Master/Slave stations

On the client side (SQL-Master):
- Create user
- Allow user to run MySQL commands as root (via ```visudo```) e.g. ```autorepair ALL=(root) NOPASSWD: /usr/bin/mariadb```

On the server side (SQL-Slave)
- Generate keys and use ```ssd-copy-id``` for the created user to allow password-less connection