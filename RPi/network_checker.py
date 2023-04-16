import subprocess
import time
from discordwebhook import Discord
import socket

class InternetChecker:
    def __init__(self, discord_webhook_url, ssid, psk):
        """
        Initializes an InternetChecker object with the provided Discord webhook URL, SSID, and PSK.

        Args:
            discord_webhook_url (str): The Discord webhook URL to post notifications.
            ssid (str): The SSID of the Wi-Fi network to check for internet connectivity.
            psk (str): The pre-shared key (PSK) of the Wi-Fi network.

        Returns:
            None
        """
        self.discord = Discord(url=discord_webhook_url)
        self.ssid = ssid
        self.psk = psk

    def check_internet(self):
        """
        Check if there is an active internet connection by connecting to a known IP and domain.

        Returns:
            bool: True if internet is connected, False otherwise.
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.settimeout(5)
            s.connect(('8.8.8.8', 53))
            s.close()

            socket.getaddrinfo('www.google.com', 443)
            self.discord.post(content="Internet Connected - STATUS: OK")
            return True
        except:
            return False


    def check_internet_connection(self):
        """
        Check if there is an active internet connection using the check_internet() method.

        Returns:
            bool: True if internet connection is established, False otherwise.
        """
        connected = False
        attempts = 0

        while not connected and attempts < 10:
            if self.check_internet():
                connected = True
            else:
                attempts += 1
                self.reconnect_wifi()
        return connected


    def reconnect_wifi(self):
        """
        Reconnect to the Wi-Fi network by terminating the existing connection, bringing down and up the network interface,
        updating the Wi-Fi configuration file, and obtaining a new IP address.

        Returns:
            None
        """
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
                return connected
        except:
            pass
        if not connected:
            time.sleep(1)

        subprocess.run(["sudo", "dhclient", "-v", "wlan0"])
