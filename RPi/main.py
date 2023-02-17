import time
from network_checker import InternetChecker
from pulse_detector import PulseDetector

checker = InternetChecker(discord_webhook_url="", ssid="", psk="")


def connect():
    connected = False

    while not connected:
        connected = checker.check_internet_connection()
        if not connected:
           print("Failed to connect")
           time.sleep(10)


pd = PulseDetector(db_host="", db_user="", db_password="", db_name="", discord_webhook_url="")
connect()

while True:
    try:
        print("Detecting pulse")
        pd.connect_db()
        pd.detect_pulse()
    except PulseDetector.DatabaseConnectionError as e:
        print("An error occured - Reconnicting network")
        connect()