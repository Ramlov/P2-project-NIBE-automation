import csv
import pymysql
import json
import requests

data = {
    "username": "NIBE Bot",
    "embeds": [
        {
            "title": "The Automator",
            "color": 3447003,
            "description": f'New heating schedule pushed to server! \nBot still going strong!',
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
        with open('config.json', 'r') as file:
            config = json.load(file)
        db_host = config['database']['host']
        db_name = config['database']['dbname']
        db_username = config['database']['username']
        db_password = config['database']['password']

        conn = pymysql.connect(host=db_host, user=db_username, password=db_password, db=db_name)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM heating")

        with open('data.csv', 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)
            for row in csv_reader:
                hour = row[0]
                spot_price_dkk = float(row[1])
                temperature = float(row[2])
                spot_price_relative = row[3]
                temperature_relative = row[4]
                turn_on = row[5]

                if turn_on == "True":
                    turn_on_value = 10
                elif turn_on == "Normal":
                    turn_on_value = 0
                else:
                    turn_on_value = -10

                cursor.execute("INSERT INTO heating (HourDK, SpotPriceDKK, Temperature, SpotPriceRelative, TemperatureRelative, TurnOn) VALUES (%s, %s, %s, %s, %s, %s)",
                            (hour, spot_price_dkk, temperature, spot_price_relative, temperature_relative, turn_on_value))
        conn.commit()
        break
    except:
        print("Error!")

conn.close()

payload = json.dumps(data)
requests.post("https://discord.com/api/webhooks/1092461466000576764/TZuzacO5VbowCLekKPDdESvZxK4UBmLVVcNWc9U5J4CuqYXarEVdLB-A02Vu4PRJMtjz", data=payload, headers={"Content-Type": "application/json"})
print("Data inserted successfully into MySQL database.")
