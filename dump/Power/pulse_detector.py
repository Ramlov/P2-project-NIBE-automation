import RPi.GPIO as GPIO
import time
import mysql.connector
import pytz
import datetime
import datetime
from discordwebhook import Discord
import os
import logging

'''Setup stuff for loggin'''
log_dir = "./logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")
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
        self.local_tz = pytz.timezone('Europe/Copenhagen')
        self.pulse_detected = False

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

    def detect_pulse(self):
        GPIO.setmode(GPIO.BCM)
        pulse_pin = 24
        GPIO.setup(pulse_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        logging.info('Going into loop, waiting for rising edge on GPIO pin')
        while True:
            if not self.pulse_detected:
                self.pulse_detected = GPIO.input(pulse_pin) == 1
            else:
                if GPIO.input(pulse_pin) == 0:
                    self.pulse_detected = False
                else:
                    continue

                current_time = datetime.datetime.now(self.local_tz)
                query = "INSERT INTO pulse_data (time, value) VALUES (%s, %s)"
                values = (current_time, 1)
                while True:
                    logging.info('Loop to insert data to database')
                    try:
                        self.cursor.execute(query, values)
                        self.db.commit()
                        self.discord.post(content="Pulse detected!")
                        logging.info("Pulse detected at {}".format(current_time))
                        logging.info('Breaking loop, and waiting for pin input')
                        break
                    except:
                        logging.error("Lost connection to database, reconnecting...")
                        raise self.DatabaseConnectionError("Lost Connection")
                time.sleep(0.1)
