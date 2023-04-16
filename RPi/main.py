import time
from network_checker import InternetChecker
from pulse_detector import PulseDetector
import threading
import json

with open("config.json") as config_file:
    config = json.load(config_file)

# Database configuration
db_config = config["database"]
db_host = db_config["db_host"]
db_user = db_config["db_user"]
db_password = db_config["db_password"]
db_name = db_config["db_name"]

# Network configuration
network_config = config["network"]
ssid = network_config["ssid"]
psk = network_config["psk"]
discord_webhook_url = network_config["discord_webhook_url"]



checker = InternetChecker(ssid=ssid, psk=psk, discord_webhook_url=discord_webhook_url)

def connect():
    """
    Connect to the internet using the InternetChecker class until a connection is established.

    Returns:
        None
    """
    connected = False

    while not connected:
        connected = checker.check_internet_connection()
        if not connected:
           time.sleep(10)


pd = PulseDetector(db_host=db_host, db_user=db_user, db_password=db_password,
                   db_name=db_name, discord_webhook_url=discord_webhook_url)

connect()

def run_pulse_threads():
    """
    Run pulse detection and submission threads concurrently using the PulseDetector class.

    Returns:
        None
    """
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

