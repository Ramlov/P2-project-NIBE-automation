import time
from network_checker import InternetChecker
from pulse_detector import PulseDetector
import os
import logging
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

checker = InternetChecker(discord_webhook_url="", ssid="", psk="")

def connect():
    connected = False

    while not connected:
        connected = checker.check_internet_connection()
        if not connected:
           logging.warning(file_name + 'Failed to connect to network - Retrying')
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
