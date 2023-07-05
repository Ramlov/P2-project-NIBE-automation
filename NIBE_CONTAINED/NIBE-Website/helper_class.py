from json import dump, load
from requests_oauthlib import OAuth2Session
from datetime import datetime, timedelta
import sqlite3
import csv, os
import pandas as pd

class helper:
    def __init__(self):
        with open('../config.json', 'r') as f:
            config = load(f)
        self.HTTP_STATUS_OK = config['api']['HTTP_STATUS_OK']
        self.client_id = config['api']['client_id']
        self.client_secret = config['api']['client_secret']
        self.system_id = config['api']['system_id']
        self.token_filename_get = config['api']['token_filename_get']
        self.token_filename_put = config['api']['token_filename_put']
        self.token_url = config['api']['token_url_oauth']
        self.extra_args = {'client_id': self.client_id, 'client_secret': self.client_secret}
        self.db_name = config["database"]["db_name"]

    def get_request(self, parameter_id,categoryId):

        def token_saver(token):
            with open(self.token_filename_get, 'w') as token_file:
                dump(token, token_file)


        with open(self.token_filename_get, 'r') as token_file:
            token = load(token_file)

        nibeuplink = OAuth2Session(client_id=self.client_id, token=token, auto_refresh_url=self.token_url, auto_refresh_kwargs=self.extra_args, token_updater=token_saver)

        response = nibeuplink.get('https://api.nibeuplink.com/api/v1/systems/'+str(self.system_id)+'/serviceinfo/categories/status?categoryId='+str(categoryId))
        if response.status_code == self.HTTP_STATUS_OK:
            objects = response.json()
            for item in objects:
                if item['parameterId'] == parameter_id:
                    return item['displayValue']
            return None
        else:
            value = 'API call not successful'
        return value


    def put_request(self, parameter_id, value):
        status = None
        print("Has been run")
        def token_saver(token):
            '''Token stuff, bruges til at opdatere token efter en request på api'''
            with open(self.token_filename_put, 'w') as token_file:
                dump(token, token_file)

        with open(self.token_filename_put, 'r') as token_file:
            token = load(token_file)


        nibeuplink = OAuth2Session(client_id=self.client_id, token=token, auto_refresh_url=self.token_url, auto_refresh_kwargs=self.extra_args, token_updater=token_saver)

        query = {
            'settings':{
            parameter_id:value
            }
        }
        url = 'https://api.nibeuplink.com/api/v1/systems/138372/parameters/'


        response = nibeuplink.put(url, json=query)

        if response.status_code == self.HTTP_STATUS_OK:
            status = "HTTP Status: OK", "\n200"
        else:
            status = 'HTTP Status: ' + str(response.status_code)
            status = response.text
        return status


    def usage(self, hours_back):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        now = datetime.now()
        start_time = now - timedelta(hours=hours_back)
        end_time = now

        query = f"SELECT value, price, value * price as value_price FROM pulse_data WHERE time BETWEEN '{start_time}' AND '{end_time}'"
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        sum_value = sum(row[0] for row in rows) / 1000
        avg_price = sum(row[1] for row in rows) / len(rows)
        try: value_price_total = (sum(row[2] for row in rows) / 1000) / sum_value 
        except: value_price_total = 0
        total = value_price_total * sum_value

        return sum_value, avg_price, total, value_price_total
    
    def savings(self, hours_back):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        now = datetime.now()
        start_time = now - timedelta(hours=hours_back)
        end_time = now

        query = f"SELECT value, price, value * price as value_price FROM pulse_data WHERE time BETWEEN '{start_time}' AND '{end_time}'"
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        sum_value = sum(row[0] for row in rows) / 1000
        avg_price = sum(row[1] for row in rows) / len(rows)
        try: value_price_total = (sum(row[2] for row in rows) / 1000) / sum_value 
        except: value_price_total = 0
        price_used = value_price_total * sum_value
        price_avg = avg_price * sum_value
        saved = price_avg-price_used

        return saved



    def updatesche(self):
        schedule_file_path = '../NIBE-Auto/schedule.csv'
        data_file_path = '../NIBE-Auto/data.csv'
        column_name = 'TurnOn'
        values_to_replace = []

        with open(schedule_file_path, 'r') as schedule_file:
            reader = csv.DictReader(schedule_file)
            for index, row in enumerate(reader):
                value = int(row['Value'])
                if value != 0:
                    values_to_replace.append((index, value))

        if not values_to_replace:
            return

        df = pd.read_csv(data_file_path)
        for index, value in values_to_replace:
            df.loc[index, column_name] = value
        df.to_csv(data_file_path, index=False)



    def delete_file(self, file_path):
        try:
            os.remove(file_path)
            print(f"File {file_path} deleted successfully.")
        except OSError as e:
            print(f"Error occurred while deleting file {file_path}: {e}")