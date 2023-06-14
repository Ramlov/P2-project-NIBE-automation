import pandas as pd
from datetime import datetime
from json import dump, load, dumps
from requests_oauthlib import OAuth2Session
import requests

# Load the configuration from the 'config.json' file
with open('config.json') as c:
    config = load(c)

# Extract the API configuration parameters
HTTP_STATUS_OK = 200
api_config = config['api']
client_id = api_config['client_id']
client_secret = api_config['client_secret']
token_filename = api_config['token_filename']
token_url = api_config['token_url']

extra_args = {'client_id': client_id, 'client_secret': client_secret}


def token_saver(token):
    '''
    Saves the access token to a file.

    This function is used to update the access token after making a request to the API.

    Args:
        token (dict): The access token to be saved.

    Returns:
        None
    '''
    with open(token_filename, 'w') as token_file:
        dump(token, token_file)
# Load the access token from the file
with open(token_filename, 'r') as token_file:
    token = load(token_file)

# Create an OAuth2Session using the access token
nibeuplink = OAuth2Session(client_id=client_id, token=token, auto_refresh_url=token_url, auto_refresh_kwargs=extra_args, token_updater=token_saver)


def gettime():
    '''
    Returns the current hour as a string.

    Returns:
        str: The current hour.
    '''
    now = datetime.now()

    current_time = now.strftime("%H")
    return(current_time)

def getstatus(index):
    '''
    Retrieves the status value based on the given index.

    This function first tries to read the value from the 'schedule.csv' file, and if that fails,
    it falls back to reading the value from the 'data.csv' file.

    Args:
        index (int): The index to retrieve the status value for.

    Returns:
        int: The status value.
    '''
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

# Get the current hour
time = int(gettime())

# Get the status value for the current hour
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
# Make a PUT request to update the parameter value on the API
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
# Send the notification to discord with the prepared data
response = requests.post(" ", data=payload, headers={"Content-Type": "application/json"})
