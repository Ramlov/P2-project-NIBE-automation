from os import path
from json import dump, load
from requests_oauthlib import OAuth2Session
import time


HTTP_STATUS_OK = 200
client_id = '59682261e9f04ab9a867eb7cfa93e840' # (32 hex digits)
client_secret = '/xADpEzVVYraWKnP6lZvcbT2RX51N4TDSM34Lry+w7w=' # (44 characters)
token_filename= '.NIBE_Uplink_API_Token_GET.json'

def token_saver(token):
    with open(token_filename, 'w') as token_file:
        dump(token, token_file)


token_url = 'https://api.nibeuplink.com/oauth/token'

with open(token_filename, 'r') as token_file:
    token = load(token_file)

extra_args = {'client_id': client_id, 'client_secret': client_secret}

start_time = time.time()
nibeuplink = OAuth2Session(client_id=client_id, token=token, auto_refresh_url=token_url, auto_refresh_kwargs=extra_args, token_updater=token_saver)

response = nibeuplink.get('https://api.nibeuplink.com/api/v1/systems/138372/serviceinfo/categories/status?categoryId=STATUS')
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Latency API GET request: {elapsed_time} seconds \nCall was made to https://api.nibeuplink.com ")

if response.status_code == HTTP_STATUS_OK:
    objects = response.json()
    #print(f'Udendørs temperatur {objects[1]["displayValue"]}')
    print("Works")
else:
    print('HTTP Status: ' + str(response.status_code))
    print(response.text)
    raise SystemExit('API call not successful')



def get_data_by_parameter_id(data, parameter_id):
    for item in data:
        if item['parameterId'] == parameter_id:
            return item
    return None


selected_data = get_data_by_parameter_id(objects, "hot_water_temperature")
print(selected_data)