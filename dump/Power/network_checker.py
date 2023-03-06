import subprocess
import time
from discordwebhook import Discord
import os
import logging
import socket
import datetime

'''Setup stuff for loggin'''
log_dir = "./logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")
log_path = os.path.join(log_dir, log_filename)

logging.basicConfig(filename=log_path, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')





class InternetChecker:
    def __init__(self, discord_webhook_url, ssid, psk):
        self.discord = Discord(url=discord_webhook_url)
        self.ssid = ssid
        self.psk = psk

    def check_internet(self):
        try:
            socket.getaddrinfo('www.google.com', 443, socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, socket.AI_ADDRCONFIG, ('8.8.8.8', 53))
            pring("Connected")
            return True
        except:
            return False


    def check_internet_connection(self):
        connected = False
        attempts = 0

        while not connected and attempts < 10:
            result = subprocess.run(['ping', '-c', '1', 'www.google.com'], stdout=subprocess.PIPE)

            if result.returncode == 0:
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
