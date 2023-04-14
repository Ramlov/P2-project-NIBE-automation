from json import dump, load
from requests_oauthlib import OAuth2Session
from datetime import datetime, timedelta
import pymysql

class helper:
    def __init__(self):
        with open('config.json', 'r') as f:
            config = load(f)
        self.HTTP_STATUS_OK = HTTP_STATUS_OK = config['api']['HTTP_STATUS_OK']
        self.client_id = config['api']['client_id']
        self.client_secret = config['api']['client_secret']
        self.token_filename_get = config['api']['token_filename_get']
        self.token_filename_put = config['api']['token_filename_put']
        self.token_url = config['api']['token_url_oauth']
        self.extra_args = {'client_id': self.client_id, 'client_secret': self.client_secret}

    def get_request(self, parameter_id):

        def token_saver(token):
            with open(self.token_filename_get, 'w') as token_file:
                dump(token, token_file)


        with open(self.token_filename_get, 'r') as token_file:
            token = load(token_file)

        nibeuplink = OAuth2Session(client_id=self.client_id, token=token, auto_refresh_url=self.token_url, auto_refresh_kwargs=self.extra_args, token_updater=token_saver)

        response = nibeuplink.get('https://api.nibeuplink.com/api/v1/systems/138372/serviceinfo/categories/status?categoryId=STATUS')
        if response.status_code == self.HTTP_STATUS_OK:
            objects = response.json()
            #value = f'Udendørs temperatur {objects[1]["displayValue"]}'
            for item in objects:
                if item['parameterId'] == parameter_id:
                    return item['displayValue']
            return None
        else:
            value = 'API call not successful'
        return value


    def put_request(self, temp):
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
            '47011':temp
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
        with open('config.json', 'r') as file:
            config = load(file)
        db_host = config['database']['host']
        db_name = config['database']['dbname']
        db_username = config['database']['username']
        db_password = config['database']['password']

        db_connection = pymysql.connect(host=db_host, database=db_name, user=db_username, password=db_password)
        db_cursor = db_connection.cursor()

        now = datetime.now()
        start_time = now - timedelta(hours=hours_back)
        end_time = now

        query = f"SELECT value, price FROM pulse_data WHERE time BETWEEN '{start_time}' AND '{end_time}'"
        db_cursor.execute(query)
        rows = db_cursor.fetchall()
        db_cursor.close()
        db_connection.close()

        sum_value = sum(row[0] for row in rows) / 1000
        avg_price = sum(row[1] for row in rows) / len(rows)
        total = avg_price * sum_value
        return sum_value, avg_price, total