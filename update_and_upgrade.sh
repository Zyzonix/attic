echo ---------------
echo Starting update
echo ---------------
sudo apt-get update
echo ----------------
echo Starting upgrade
echo ----------------
sudo apt-get upgrade -y
echo ---------------------
echo Performing autoremove
echo ---------------------
sudo apt autoremove
