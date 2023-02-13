from os import path
from json import dump, load
from requests_oauthlib import OAuth2Session

HTTP_STATUS_OK = 200

home_dir = path.expanduser('~')
token_filename= '.NIBE_Uplink_API_Token.json'

def token_saver(token):
    with open(token_filename, 'w') as token_file:
        dump(token, token_file)

client_id = 'Få id fra Mahtias eller API' # (32 hex digits)
client_secret = 'Få secret fra Mahtias eller API' # (44 characters)

token_url = 'https://api.nibeuplink.com/oauth/token'

with open(token_filename, 'r') as token_file:
    token = load(token_file)

extra_args = {'client_id': client_id, 'client_secret': client_secret}

nibeuplink = OAuth2Session(client_id=client_id, token=token, auto_refresh_url=token_url, auto_refresh_kwargs=extra_args, token_updater=token_saver)

response = nibeuplink.get('https://api.nibeuplink.com/api/v1/systems')
if response.status_code == HTTP_STATUS_OK:
    ##print(response.json())
    count = response.json()['numItems']
    print('Total of ' + str(count) + ' system(s) returned by the API query')
    objects = response.json()['objects']
    for object in objects:
        print('System Id:   ' + str(object['systemId']))
        print('System Name: ' + str(object['name']))
else:
    print('HTTP Status: ' + str(response.status_code))
    print(response.text)
    raise SystemExit('API call not successful')
