import pandas as pd
from datetime import datetime
from time import sleep
from json import dump, load, dumps
from requests_oauthlib import OAuth2Session
import requests
from energy_price import ElectricityPricing

price_collector = ElectricityPricing() 

HTTP_STATUS_OK = 200 #En statuskode returneret af API
client_id = '59682261e9f04ab9a867eb7cfa93e840' # (32 hex digits)
client_secret = '/xADpEzVVYraWKnP6lZvcbT2RX51N4TDSM34Lry+w7w=' # (44 characters)
token_filename= '.NIBE_Uplink_API_Token_PUT.json'
token_url = 'https://api.nibeuplink.com/oauth/token'
extra_args = {'client_id': client_id, 'client_secret': client_secret}


def token_saver(token):
    '''Token stuff, bruges til at opdatere token efter en request på api'''
    with open(token_filename, 'w') as token_file:
        dump(token, token_file)

with open(token_filename, 'r') as token_file:
    token = load(token_file)


nibeuplink = OAuth2Session(client_id=client_id, token=token, auto_refresh_url=token_url, auto_refresh_kwargs=extra_args, token_updater=token_saver)


def gettime():
    now = datetime.now()

    current_time = now.strftime("%H")
    return(current_time)

def getstatus(index):
    df = pd.read_csv('combineddata.csv')
    try:
        value = df['TurnOn'].iloc[index]
        return(value)
    except Exception as e:
        return(e)


url = 'https://api.nibeuplink.com/api/v1/systems/138372/parameters/'

time = int(gettime())
status = getstatus(time)
print(status)
print("Current time is ", time)
if status == "True":
    query = {
        'settings':{
        '47011':'10'
        }
    }
    print("Heat pump set to: 10")
elif status == "False":
    query = {
        'settings':{
        '47011':'-10'
        }
    }
    print("Heat pump set to: -10")
elif status == "Normal":
    query = {
        'settings':{
        '47011':'0'
        }
    }
    print("Heat pump set to: 0")
response = nibeuplink.put(url, json=query)
if response.status_code == HTTP_STATUS_OK:
    print("HTTP Status: OK", "\n200")
else:
    print('HTTP Status: ' + str(response.status_code))
data = {
        "username": "NIBE Bot",
        "embeds": [
            {
                "title": "The Automator",
                "color": 5763719,
                "description": f'Changed temperature! \nResponse from API: Parameter: {response.json()[0]["parameter"]["parameterId"]} Value: {response.json()[0]["parameter"]["displayValue"]} \nTime is now: {time}  \nStatus: {status}',
                "footer": {
                    "text": "Author: Ramlov",
                    "icon_url": "https://avatars.githubusercontent.com/u/17428562?v=4",
                    "url": "https://github.com/Ramlov"
                }
            }
        ]
    }
payload = dumps(data)
response = requests.post("https://discord.com/api/webhooks/1092461466000576764/TZuzacO5VbowCLekKPDdESvZxK4UBmLVVcNWc9U5J4CuqYXarEVdLB-A02Vu4PRJMtjz", data=payload, headers={"Content-Type": "application/json"})
