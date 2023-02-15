import RPi.GPIO as GPIO
import time
import mysql.connector
import pytz
from datetime import datetime

# Set up the database connection
db = mysql.connector.connect(
    host=" ",
    user=" ",
    password=" ",
    database=" "
)
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS pulse_data (time TIMESTAMP, value INT)")
print("Database ready!")

# Set up the GPIO pin
GPIO.setmode(GPIO.BCM)
pulse_pin = 24
GPIO.setup(pulse_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

pulse_detected = False

# Set the time zone to your local time zone
local_tz = pytz.timezone('Europe/Copenhagen')

while True:
    if not pulse_detected:
        pulse_detected = GPIO.input(pulse_pin) == 1
    else:
        if GPIO.input(pulse_pin) == 0:
            pulse_detected = False
        else:
            continue

        # Get the current time in your local time zone
        current_time = datetime.now(local_tz)

        # Insert the data into the database
        query = "INSERT INTO pulse_data (time, value) VALUES (%s, %s)"
        values = (current_time, 1)
        cursor.execute(query, values)
        db.commit()

        print("Pulse detected at {}".format(current_time))
        time.sleep(0.1) # Wait for the voltage to drop to 0 before detecting another pulse
