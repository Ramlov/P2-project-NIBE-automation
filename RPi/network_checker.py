import subprocess
import time
from discordwebhook import Discord
import os
import logging
import socket
import datetime

'''Setup stuff for logging'''
log_dir = "./logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Get the name of the file from which the log is created
file_name = os.path.splitext(os.path.basename(__file__))[0]

# Create log file name with current datetime and the file name
log_filename = file_name + datetime.datetime.now().strftime("_%Y-%m-%d_%H-%M-%S") + ".log"
log_path = os.path.join(log_dir, log_filename)

logging.basicConfig(filename=log_path, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class InternetChecker:
    def __init__(self, discord_webhook_url, ssid, psk):
        self.discord = Discord(url=discord_webhook_url)
        self.ssid = ssid
        self.psk = psk

    def check_internet(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.settimeout(5)
            s.connect(('8.8.8.8', 53))
            s.close()

            socket.getaddrinfo('www.google.com', 443)
            print("Connected")
            return True
        except:
            return False


    def check_internet_connection(self):
        connected = False
        attempts = 0

        while not connected and attempts < 10:
            if self.check_internet():
                self.discord.post(content="Internet Connected - STATUS: OK")
                logging.info(f'OK - Internet connected')
                connected = True
            else:
                attempts += 1
                logging.warning("Connection attempt {} failed".format(attempts))
                self.reconnect_wifi()

        if not connected:
            logging.error("Didn't connect - Retrying")

        return connected


    def reconnect_wifi(self):
        logging.info('Trying to reconnect wifi')
        subprocess.run(["sudo", "wpa_cli", "-i", "wlan0", "terminate"])
        subprocess.run(["sudo", "ip", "link", "set", "wlan0", "down"])
        subprocess.run(["sudo", "ip", "link", "set", "wlan0", "up"])
        subprocess.run(["sudo", "wpa_passphrase", self.ssid, self.psk, "-o", "/etc/wpa_supplicant/wpa_supplicant.conf"])
        subprocess.run(["sudo", "wpa_supplicant", "-B", "-i", "wlan0", "-c", "/etc/wpa_supplicant/wpa_supplicant.conf"])
        connected = False
        try:
            output = subprocess.check_output(["sudo", "iwgetid", "wlan0"])
            if self.ssid in str(output):
                connected = True
                logging.info("Connected")
                return connected
        except:
            pass
        if not connected:
            logging.error("Connection unsuccessful - Sleeping and trying again")
            time.sleep(1)

        subprocess.run(["sudo", "dhclient", "-v", "wlan0"])
