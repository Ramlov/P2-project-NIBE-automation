import RPi.GPIO as GPIO
from time import sleep
import mysql.connector
from datetime import timezone, datetime, time, date, timedelta
import threading
import json
import requests
from price import ElectricityPricing

class PulseDetector:
    class DatabaseConnectionError(Exception):
        pass

    def __init__(self, db_host, db_user, db_password, db_name, discord_webhook_url):
        self.db_host = db_host
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name
        self.discord = discord_webhook_url
        utc_offset = timedelta(hours=1)  # Denmark is UTC+1
        self.local_tz = timezone(utc_offset)
        self.pulse_count = 0
        self.lock = threading.Lock()
        self.pulse_detected = False
        self.Electricity_Pricing = ElectricityPricing()

    def connect_db(self):
        self.db = mysql.connector.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_password,
            database=self.db_name
        )
        self.cursor = self.db.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS pulse_data (time TIMESTAMP, value INT, price FLOAT)")

    def collect_pulse(self):
       GPIO.setmode(GPIO.BCM)
       pulse_pin = 24
       prev_state = 0
       GPIO.setup(pulse_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
       while True:
            if GPIO.input(pulse_pin) == 1 and prev_state == 0:
                with self.lock:
                    self.pulse_count += 1
                    print(self.pulse_count)
            prev_state = GPIO.input(pulse_pin)
            sleep(0.03)

    def submit_pulse_count(self):
        while True:
            now = datetime.now()
            minute = int(now.strftime("%M"))
            if minute in [15, 30, 45, 59]:
                while True:
                    with self.lock:
                        current_pulse_count = self.pulse_count
                    current_time = datetime.now(self.local_tz)
                    current_price = self.Electricity_Pricing.get_current_price()
                    query = "INSERT INTO pulse_data (time, value, price) VALUES (%s, %s, %s)"
                    values = (current_time, current_pulse_count, current_price)
                    data = {
                        "username": "NIBE Bot",
                        "embeds": [
                            {
                                "title": "Pulse Data",
                                "color": 16774912,
                                "description": f'Pulse count submitted! \nTotal count in 15 minute period: {current_pulse_count}\nPrice in period: {round(current_price, 2)} DKK',
                                "footer": {
                                    "text": "Author: Ramlov",
                                    "icon_url": "https://avatars.githubusercontent.com/u/17428562?v=4",
                                    "url": "https://github.com/Ramlov"
                                }
                            }
                        ]
                    }
                    while True:
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
                            self.pulse_count = 0
                            payload = json.dumps(data)
                            response = requests.post(self.discord, data=payload, headers={"Content-Type": "application/json"})
                            break
                        except Exception as e:
                            sleep(0.5)
                        finally:
                            logging.info("Closing DB")
                            if 'cursor' in locals():
                                cursor.close()
                            if 'db' in locals():
                                db.close()
                            break
                    sleep(0.1)
                    break
                sleep(10*60)
