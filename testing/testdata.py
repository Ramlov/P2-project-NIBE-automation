import pymysql
import json
from datetime import datetime, timedelta
import csv
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def usage():
    """
    Calculate usage statistics based on data from a database.

    Returns:
        str: Usage statistics formatted as a string.
    """
    with open('config.json', 'r') as file:
        config = json.load(file)
    db_host = config['database']['host']
    db_name = config['database']['dbname']
    db_username = config['database']['username']
    db_password = config['database']['password']

    db_connection = pymysql.connect(host=db_host, database=db_name, user=db_username, password=db_password)
    db_cursor = db_connection.cursor()

    System = input("What system are you collecting data from? ")
    start_time_str = input("Enter a start time (YYYY-MM-DD): ")
    end_time_str = input("Enter an end time (YYYY-MM-DD): ")

    start_time_str += " 00:00:00"   
    end_time_str += " 00:00:00"

    start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')

    query = f"SELECT value, price, value * price as value_price FROM pulse_data WHERE time BETWEEN '{start_time}' AND '{end_time}'"
    db_cursor.execute(query)
    rows = db_cursor.fetchall()
    db_cursor.close()
    db_connection.close()

    sum_value = sum(row[0] for row in rows) / 1000
    avg_price = sum(row[1] for row in rows) / len(rows)
    value_price_total = ((sum(row[2] for row in rows)/1000)/sum_value)
    total = value_price_total * sum_value

    output = f'{System}\nThe total KwH usage in period: {round(sum_value,2)}. \nThe average price in period: {round(avg_price,2)} DKK. \nThe bought price of electricity in period: {round(value_price_total,2)} DKK \nThe total cost in period: {round(total,2)} DKK'

    file_exists = os.path.isfile('usage.csv')
    if file_exists:
        os.remove('usage.csv')
    with open('usage.csv', 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        #header = ['System', 'Start time', 'End time', 'Average price', 'Bought price', 'Total usage DKK', 'Total usage kwh',]
        #csvwriter.writerow(header)
        row = [System, start_time_str, end_time_str, round(avg_price,2), round(value_price_total,2), round(total,2), round(sum_value,2)]
        csvwriter.writerow(row)

    return output



def pushdata():
    """
    Push the usage data to a Google Sheet.

    Raises:
        gspread.exceptions.APIError: If there is an error communicating with the Google Sheets API.
    """
    creds_path = 'exalted-iridium-384920-584d2921d9a2.json'
    doc_id = '1ArcpUMjb5Tu5EK5GQlwZehQ2oUJnGYjcET4OzTKqhGM'
    worksheet_name = 'Data'
    csv_path = 'usage.csv'
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)

    doc = client.open_by_key(doc_id)
    worksheet = doc.worksheet(worksheet_name)

    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
        worksheet.append_rows(data)
        print('Data inserted successfully.')
#print(usage())
pushdata()