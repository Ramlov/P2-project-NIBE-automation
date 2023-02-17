import subprocess
import time
from discordwebhook import Discord

class InternetChecker:
    def __init__(self, discord_webhook_url, ssid, psk):
        self.discord = Discord(url=discord_webhook_url)
        self.ssid = ssid
        self.psk = psk

    def check_internet_connection(self):
        connected = False
        attempts = 0

        while not connected and attempts < 10:
            result = subprocess.run(['ping', '-c', '1', 'www.google.com'], stdout=subprocess.PIPE)

            if result.returncode == 0:
                self.discord.post(content="Internet Connected - STATUS: OK")
                print("OK - Internet connected")
                connected = True
            else:
                attempts += 1
                print("Connection attempt {} failed".format(attempts))
                self.reconnect_wifi()

        if not connected:
            print("Didn't connect - Retrying")

        return connected


    def reconnect_wifi(self):
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
                print("Connected")
                return connected
        except:
            pass
        if not connected:
            print("Connection unsuccessful - Sleeping and trying again")
            time.sleep(1)

        subprocess.run(["sudo", "dhclient", "-v", "wlan0"])