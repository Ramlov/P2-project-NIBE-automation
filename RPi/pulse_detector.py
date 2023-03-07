import RPi.GPIO as GPIO
import time
import mysql.connector
import datetime
from discordwebhook import Discord
import os
import logging
import threading

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

class PulseDetector:
    class DatabaseConnectionError(Exception):
        pass

    def __init__(self, db_host, db_user, db_password, db_name, discord_webhook_url):
        self.db_host = db_host
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name
        self.discord = Discord(url=discord_webhook_url)
        utc_offset = datetime.timedelta(hours=1)  # Denmark is UTC+1
        self.local_tz = datetime.timezone(utc_offset)
        self.pulse_count = 0
        self.lock = threading.Lock()

    def connect_db(self):
        self.db = mysql.connector.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_password,
            database=self.db_name
        )
        self.cursor = self.db.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS pulse_data (time TIMESTAMP, value INT)")
        logging.info("Database ready! - Connection successful")
        self.discord.post(content="Database ready! - STATUS: CONNECTED")

    def collect_pulse(self):
        pulse_pin = 24
        GPIO.setup(pulse_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        logging.info('Going into loop, waiting for rising edge on GPIO pin')
        while True:
            if GPIO.input(pulse_pin) == 1:
                with self.lock:
                    self.pulse_count += 1
                    print(self.pulse_count)
            time.sleep(0.1)

    def submit_pulse_count(self):
        while True:
            time.sleep(15 * 60)
            with self.lock:
                current_pulse_count = self.pulse_count
                self.pulse_count = 0
            current_time = datetime.datetime.now(self.local_tz)
            query = "INSERT INTO pulse_data (time, value) VALUES (%s, %s)"
            values = (current_time, current_pulse_count)
            while True:
                logging.info('Loop to insert data to database')
                try:
                    db = mysql.connector.connect(
                        host=self.db_host,
                        user=self.db_user,
                        password=self.db_password,
                        database=self.db_name
                    )
                    cursor = db.cursor()
                    cursor.execute(query, values)
                    db.commit()
                    cursor.close()
                    db.close()
                    self.discord.post(content="Pulse count submitted!")
                    logging.info("Pulse count submitted at {}".format(current_time))
                    break
                except Exception as e:
                    logging.critical("{} {}".format(file_name, str(e)))
                    logging.error("Lost connection to database, reconnecting...")
                    time.sleep(0.2)
                finally:
                    if 'cursor' in locals():
                        cursor.close()
                        logging.debug("Closed Cursor")
                    if 'db' in locals():
                        db.close()
                        logging.debug("Closed DB")
            time.sleep(0.1)
