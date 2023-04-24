
import pymysql
import json
from datetime import datetime, timedelta

def usage():
    with open('config.json', 'r') as file:
        config = json.load(file)
    db_host = config['database']['host']
    db_name = config['database']['dbname']
    db_username = config['database']['username']
    db_password = config['database']['password']

    db_connection = pymysql.connect(host=db_host, database=db_name, user=db_username, password=db_password)
    db_cursor = db_connection.cursor()

    start_time_str = input("Enter a start time (YYYY-MM-DD): ")
    end_time_str = input("Enter an end time (YYYY-MM-DD): ")

    start_time_str += " 00:00:00"   
    end_time_str += " 00:00:00"

    start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')

    query = f"SELECT value, price FROM pulse_data WHERE time BETWEEN '{start_time}' AND '{end_time}'"
    db_cursor.execute(query)
    rows = db_cursor.fetchall()
    db_cursor.close()
    db_connection.close()

    sum_value = sum(row[0] for row in rows) / 1000
    avg_price = sum(row[1] for row in rows) / len(rows)
    total = avg_price * sum_value
    return f'The total KwH usage in periode: {round(sum_value,2)}. \nThe average price in periode: {round(avg_price,2)} DKK. \nThe total cost in periode: {round(total,2)} DKK'



print(usage())

