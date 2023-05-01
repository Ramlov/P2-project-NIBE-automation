import RPi.GPIO as GPIO
from time import sleep
import mysql.connector
from datetime import timezone, datetime, timedelta
import threading
import json
import requests
from price import ElectricityPricing

class PulseDetector:
    def __init__(self, db_host, db_user, db_password, db_name, discord_webhook_url):
        """
        Initialize PulseDetector instance.

        Args:
            db_host (str): Database host name or IP address.
            db_user (str): Database username.
            db_password (str): Database password.
            db_name (str): Database name.
            discord_webhook_url (str): Discord webhook URL for sending pulse count notifications.

        Returns:
            None.

        """
        with open('config.json', 'r') as f:
            config = json.load(f)
        rpi_config = config["raspberrypi"]
        self.pulse_pin = rpi_config["pulse_pin"]
        self.update_interval = rpi_config["update_interval"]

        self.db_host = db_host
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name
        self.discord = discord_webhook_url
        utc_offset = timedelta(hours=1)
        self.local_tz = timezone(utc_offset)
        self.pulse_count = 0
        self.lock = threading.Lock()
        self.pulse_detected = False
        self.Electricity_Pricing = ElectricityPricing()

    def connect_db(self):
        """
        Connect to the MySQL database.

        """
        self.db = mysql.connector.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_password,
            database=self.db_name
        )
        self.cursor = self.db.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS pulse_data (time TIMESTAMP, value INT, price FLOAT)")

    def collect_pulse(self):
       """
        Collect pulse data from sensor and update pulse count.

        This method runs in a separate thread and continuously collects pulse data from a sensor connected to a specific GPIO pin.
        It updates the pulse count attribute of the class instance with the number of pulses detected.

        Steps:
        1. Sets up GPIO mode and pin for pulse detection.
        2. Monitors the pulse pin for changes in state, and if a pulse is detected, updates the pulse count.
        3. Uses a lock to ensure thread-safe access to the pulse count attribute.
        4. Sleeps for a short duration (0.03 seconds) to avoid unnecessary CPU usage.

        Note:
        - The pulse count is incremented by 1 for each detected pulse.
        - The `self.lock` attribute is assumed to be an instance of `threading.Lock` used for thread synchronization.
        - The `self.pulse_count` attribute is assumed to be an integer representing the current pulse count.

        Raises:
        - None.

        Returns:
        - None.
       """
       GPIO.setmode(GPIO.BCM)
       prev_state = 0
       GPIO.setup(self.pulse_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
       while True:
            if GPIO.input(self.pulse_pin) == 1 and prev_state == 0:
                with self.lock:
                    self.pulse_count += 1
                    print(self.pulse_count)
            prev_state = GPIO.input(self.pulse_pin)
            sleep(0.03)

    def submit_pulse_count(self):
        """
        Submit the pulse count to the database and send a Discord webhook with the pulse count, total count in 15-minute period,
        and price in the period.

        This method runs in an infinite loop in a sepreate thread and executes the following steps:
        1. Checks the current minute, and if it's at the 15th, 30th, 45th, or 59th minute, it proceeds to the next steps.
        2. Acquires the current pulse count and time.
        3. Fetches the current electricity price using the ElectricityPricing class.
        4. Inserts the pulse count, time, and price into the 'pulse_data' table in the database.
        5. Sends a Discord webhook with the pulse count, total count in 15-minute period, and price in the period.
        6. Handles exceptions and ensures that the database connection is closed.

        Note:
        - The 'pulse_count' attribute is reset to 0 after submitting the data.
        - The Discord webhook is sent.

        Raises:
        - Exception: If there is an error in submitting the pulse count data to the database or sending the Discord webhook.
        """
        while True:
            now = datetime.now()
            minute = int(now.strftime("%M"))
            if minute in self.update_interval:
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
                            requests.post(self.discord, data=payload, headers={"Content-Type": "application/json"})
                            break
                        except Exception as e:
                            sleep(0.5)
                        finally:
                            if 'cursor' in locals():
                                cursor.close()
                            if 'db' in locals():
                                db.close()
                            break
                    sleep(0.1)
                    break
                sleep(10*60)
