import machine
import utime
import network
from mysql_type import connect, TIMESTAMP, INT

wifi_ssid = " "
wifi_password = " "
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(wifi_ssid, wifi_password)

while not wifi.isconnected():
    machine.idle()

print("Connected to WiFi! IP address: ", wifi.ifconfig()[0])

db = connect(
    host=" ",
    user=" ",
    password=" ",
    database=" "
)

cursor = db.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS pulse_data (time TIMESTAMP, value INT)")

pulse_pin = machine.Pin(2, machine.Pin.IN)

while True:
    pulse_detected = pulse_pin.wait_for_edge(machine.Pin.IRQ_RISING)
    current_time = utime.gmtime()
    query = "INSERT INTO pulse_data (time, value) VALUES (%s, %s)"
    values = (current_time, 1)
    cursor.execute(query, values, types=[TIMESTAMP, INT])
    db.commit()

    print("Pulse detected!")
