import pandas as pd
from datetime import datetime
from json import dump, load, dumps
from requests_oauthlib import OAuth2Session
import requests

with open('../config.json') as c:
    config = load(c)


HTTP_STATUS_OK = 200
api_config = config['api']
client_id = api_config['client_id']
client_secret = api_config['client_secret']
token_filename = api_config['token_filename_put']
token_url = api_config['token_url_oauth']

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
    try:
        df = pd.read_csv('schedule.csv')
        value = df['Value'].iloc[index]
        if (int(value) != 0):
            print("Værdi er", type(value))
            return(value)
        raise ValueError()
    except:
        df = pd.read_csv('data.csv')
        try:
            value = df['TurnOn'].iloc[index]
            if value == "True":
                status = 5
            elif value == "Normal":
                status = -4
            elif value == "False":
                status = -10
            return(status)
        except:
            return df['Offset'].iloc[index]


url = 'https://api.nibeuplink.com/api/v1/systems/138372/parameters/'

time = int(gettime())
status = getstatus(time)
print(status)
print("Current time is ", time)
status = int(status)
query = {
    'settings':{
    '47011':status
    }
}
print("Heat pump set to: ", status)
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
