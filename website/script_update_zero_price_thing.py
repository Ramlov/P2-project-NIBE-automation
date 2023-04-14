# Import the necessary libraries
import pymysql
import json

with open('config.json', 'r') as file:
    config = json.load(file)
db_host = config['database']['host']
db_name = config['database']['dbname']
db_username = config['database']['username']
db_password = config['database']['password']

conn = pymysql.connect(host=db_host, user=db_username, passwd=db_password, db=db_name)
cursor = conn.cursor()

cursor.execute("SELECT AVG(price) FROM pulse_data WHERE price > 0")
average_price = cursor.fetchone()[0]

cursor.execute("UPDATE pulse_data SET price = %s WHERE price = 0", (average_price,))
conn.commit()

cursor.close()
conn.close()
