import time
from network_checker import InternetChecker
from pulse_detector import PulseDetector
import os
import logging
import datetime

'''Setup stuff for loggin'''
log_dir = "./logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")
log_path = os.path.join(log_dir, log_filename)

logging.basicConfig(filename=log_path, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


checker = InternetChecker(discord_webhook_url="https://discord.com/api/webhooks/1075749180552794143/bWkMo8ejqchEaK9qqsMDTj1rnb-jYi6pU8mQJf3zTs040vOrBeghaBF52zsBD-YH65RI", ssid="iPhone", psk="Wifi5502")


def connect():
    connected = False

    while not connected:
        connected = checker.check_internet_connection()
        if not connected:
           logging.warning('Failed to connect to network - Retrying')
           time.sleep(10)


pd = PulseDetector(db_host="mysql110.unoeuro.com", db_user="ramlov_org", db_password="a9hpyFH4cGdf", db_name="ramlov_org_db", discord_webhook_url="https://discord.com/api/webhooks/1075749180552794143/bWkMo8ejqchEaK9qqsMDTj1rnb-jYi6pU8mQJf3zTs040vOrBeghaBF52zsBD-YH65RI")
connect()

while True:
    try:
        logging.info('Going into pulse detection loop')
        pd.connect_db()
        pd.detect_pulse()
    except PulseDetector.DatabaseConnectionError as e:
        logging.error(f'An error occured - Reconnicting network - Possible errorcode: {e}')
        connect()
