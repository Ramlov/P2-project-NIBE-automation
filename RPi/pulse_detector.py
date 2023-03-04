import RPi.GPIO as GPIO
import time
import mysql.connector
import pytz
import logging
from datetime import datetime
from discordwebhook import Discord


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
        print("Database ready!")
        self.discord.post(content="Database ready! - STATUS: CONNECTED")

    def detect_pulse(self):
        GPIO.setmode(GPIO.BCM)
        pulse_pin = 24
        GPIO.setup(pulse_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        while True:
            if not self.pulse_detected:
                self.pulse_detected = GPIO.input(pulse_pin) == 1
            else:
                if GPIO.input(pulse_pin) == 0:
                    self.pulse_detected = False
                else:
                    continue

                current_time = datetime.now(self.local_tz)
                query = "INSERT INTO pulse_data (time, value) VALUES (%s, %s)"
                values = (current_time, 1)

                try:
                    self.cursor.execute(query, values)
                    self.db.commit()
                    self.discord.post(content="Pulse detected!")
                    print("Pulse detected at {}".format(current_time))
                except KeyboardInterrupt as e:
                    print("[{}] KeyboardInterrupt catched: {}".format(datetime.now(self.local_tz), e))
                    raise e
                except BaseException as e:
                    logging.exception(e)  # print the traceback of the exception
                    print("Lost connection to database, reconnecting...")
                    print("[{}] BaseException catched: {}".format(datetime.now(self.local_tz), e))
                    raise self.DatabaseConnectionError("Lost Connection, error: {}".format(e))
                time.sleep(0.1)