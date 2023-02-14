from os import path
from json import dump, load
from requests_oauthlib import OAuth2Session

HTTP_STATUS_OK = 200 #En statuskode returneret af API
client_id = '' # (32 hex digits)
client_secret = '' # (44 characters)
token_filename= 'NIBE_API/.NIBE_Uplink_API_Token.json'
token_url = 'https://api.nibeuplink.com/oauth/token'
extra_args = {'client_id': client_id, 'client_secret': client_secret}


def token_saver(token):
    '''Token stuff, bruges til at opdatere token efter en request på api'''
    with open(token_filename, 'w') as token_file:
        dump(token, token_file)

with open(token_filename, 'r') as token_file:
    token = load(token_file)


nibeuplink = OAuth2Session(client_id=client_id, token=token, auto_refresh_url=token_url, auto_refresh_kwargs=extra_args, token_updater=token_saver)

query = {
    'settings':{
    '47011':'0'
    }
}
url = 'https://api.nibeuplink.com/api/v1/systems/138372/parameters/'


response = nibeuplink.put(url, json=query)

if response.status_code == HTTP_STATUS_OK:
    print("HTTP Status: OK", "\n200")
else:
    print('HTTP Status: ' + str(response.status_code))
    print(response.text)
    raise SystemExit('API call not successful')
