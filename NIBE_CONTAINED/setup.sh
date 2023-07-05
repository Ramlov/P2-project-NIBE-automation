#!/bin/bash

# Update system packages
sudo apt update
sudo apt upgrade -y

# Install Python and pip
sudo apt install -y python3 python3-pip

# Update crontab
(crontab -l ; echo "@reboot cd /home/pi/NIBE/NIBE-Website && sudo python3 app.py") | crontab -
(crontab -l ; echo "@reboot cd /home/pi/NIBE/NIBE-Pulse && sudo python3 main.py") | crontab -
(crontab -l ; echo "15 23 * * * cd /home/pi/NIBE/NIBE-Auto/ && sudo python3 rename_file.py") | crontab -
(crontab -l ; echo "15 17 * * * cd /home/pi/NIBE/NIBE-Auto/ && sudo python3 energy_price.py") | crontab -
(crontab -l ; echo "1 * * * * cd /home/pi/NIBE/NIBE-Auto/ && sudo python3 main.py") | crontab -
(crontab -l ; echo "0 0 * * * cd /home/pi/NIBE/NIBE-Auto/ && sudo python3 push_data.py") | crontab -


cd /home/pi/NIBE
sudo pip3 install -r requirements.txt

sudo reboot
