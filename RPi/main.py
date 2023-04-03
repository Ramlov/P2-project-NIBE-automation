import time
from datetime import datetime
from network_checker import InternetChecker
from pulse_detector import PulseDetector
import threading
from discordwebhook import Discord

checker = InternetChecker(ssid="Telenor4443odd", psk="HpQCTN3TL",discord_webhook_url="")

def connect():
    connected = False

    while not connected:
        connected = checker.check_internet_connection()
        if not connected:
           time.sleep(10)


pd = PulseDetector(db_host="", db_user="", db_password="", db_name="", discord_webhook_url="")
connect()

def run_pulse_threads():
    pulse_detection_thread = threading.Thread(target=pd.collect_pulse)
    pulse_detection_thread.start()

    pulse_submission_thread = threading.Thread(target=pd.submit_pulse_count)
    pulse_submission_thread.start()

    pulse_detection_thread.join()
    pulse_submission_thread.join()

while True:
    try:
        run_pulse_threads()
    except:
        pulse_detection_thread.cancel()
        pulse_submission_thread.cancel()
        connect()

