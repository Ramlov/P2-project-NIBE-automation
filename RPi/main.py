import time
from network_checker import InternetChecker
from pulse_detector import PulseDetector
import os
import logging

'''Setup stuff for loggin'''
log_dir = "./logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")
log_path = os.path.join(log_dir, log_filename)

logging.basicConfig(filename=log_path, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')




checker = InternetChecker(discord_webhook_url="", ssid="", psk="")


def connect():
    connected = False

    while not connected:
        connected = checker.check_internet_connection()
        if not connected:
           logging.warning('Failed to connect to network - Retrying')
           time.sleep(10)


pd = PulseDetector(db_host="", db_user="", db_password="", db_name="", discord_webhook_url="")
connect()

while True:
    try:
        logging.info('Going into pulse detection loop')
        pd.connect_db()
        pd.detect_pulse()
    except PulseDetector.DatabaseConnectionError as e:
        logging.error(f'An error occured - Reconnicting network - Possible errorcode: {e}')
        connect()