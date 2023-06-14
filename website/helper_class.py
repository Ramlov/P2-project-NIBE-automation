from json import dump, load
from requests_oauthlib import OAuth2Session
from datetime import datetime, timedelta
import pymysql
import csv

class helper:
    def __init__(self):
        """
        Initializes the helper class.

        Reads the configuration from the 'config.json' file.
        """
        with open('/root/NIBE-Website/config.json', 'r') as f:
            config = load(f)
        self.HTTP_STATUS_OK = config['api']['HTTP_STATUS_OK']
        self.client_id = config['api']['client_id']
        self.client_secret = config['api']['client_secret']
        self.system_id = config['api']['system_id']
        self.token_filename_get = config['api']['token_filename_get']
        self.token_filename_put = config['api']['token_filename_put']
        self.token_url = config['api']['token_url_oauth']
        self.extra_args = {'client_id': self.client_id, 'client_secret': self.client_secret}

    def get_request(self, parameter_id,categoryId):
        """
        Makes a GET request to retrieve information from the Nibe Uplink API.

        Args:
            parameter_id (int): The parameter ID.
            categoryId (int): The category ID.

        Returns:
            str: The display value of the requested parameter, or None if not found.
        """

        def token_saver(token):
            """
            Saves the token to a file after making a request to the API.

            Args:
                token (str): The updated token.
            """
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
        """
        Makes a PUT request to update a parameter value in the Nibe Uplink API.

        Args:
            parameter_id (int): The parameter ID.
            value: The value to be set for the parameter.

        Returns:
            str: The status of the HTTP request.
        """
        status = None
        print("Has been run")
        def token_saver(token):
            """
            Saves the token to a file after making a request to the API.

            Args:
                token (str): The updated token.
            """
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
        """
        Retrieves usage data from the database for a specified time period.

        Args:
            hours_back (int): The number of hours to go back in time.

        Returns:
            tuple: A tuple containing the sum value, average price, total cost, and bought price.
        """
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

        query = f"SELECT value, price, value * price as value_price FROM pulse_data WHERE time BETWEEN '{start_time}' AND '{end_time}'"
        db_cursor.execute(query)
        rows = db_cursor.fetchall()
        db_cursor.close()
        db_connection.close()

        sum_value = sum(row[0] for row in rows) / 1000
        avg_price = sum(row[1] for row in rows) / len(rows)
        value_price_total = ((sum(row[2] for row in rows)/1000)/sum_value)
        total = value_price_total * sum_value

        return sum_value, avg_price, total, value_price_total
    

    def updatesche(self):
        """
        Updates a schedule in the database based on the schedule CSV file.

        Reads the configuration from the 'config.json' file and updates the 'heating' table in the database.
        """
        with open('config.json', 'r') as file:
            config = load(file)
        db_host = config['database']['host']
        db_name = config['database']['dbname']
        db_username = config['database']['username']
        db_password = config['database']['password']

        conn = pymysql.connect(host=db_host, user=db_username, password=db_password, db=db_name)


        try:
            cursor = conn.cursor()
            with open('/root/NIBE/schedule.csv', 'r') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    hour = int(row['Hour'])
                    value = int(row['Value']) 
                    if value != 0:
                        timestamp = datetime.now().replace(hour=hour, minute=0, second=0).strftime("%Y-%m-%d %H:%M:%S")
                        sql = f"UPDATE heating SET TurnOn = {value} WHERE HourDK = %s"
                        cursor.execute(sql, (timestamp,))

            conn.commit()

        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")

        finally:
            cursor.close()
            conn.close()