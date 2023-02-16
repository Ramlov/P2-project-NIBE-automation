from os import path
from json import dump
from requests_oauthlib import OAuth2Session


client_id = '' # (32 hex digits)
client_secret = '' # (44 characters)


redirect_url = 'https://ramlov.org/nibeuplink/oauth2callback/index.php'

query_scope = 'WRITESYSTEM'
unique_state = 'STATESTRING'
token_url = 'https://api.nibeuplink.com/oauth/token'
authorize_url = 'https://api.nibeuplink.com/oauth/authorize'


nibeuplink = OAuth2Session(client_id=client_id, scope=query_scope, redirect_uri=redirect_url, state=unique_state)

print('Use a Web Browser to connect to:  ' + authorize_url + '?response_type=code&client_id=' + client_id + '&scope=' + query_scope + '&redirect_uri=' + redirect_url + '&state=' + unique_state)

authorization_code = input('Enter (copy-and-paste) the Authorization Code printed in the Web Browser:  ')


if len(authorization_code) < 99:
    raise SystemExit('Invalid Authorization Code entered; exiting')


token = nibeuplink.fetch_token(token_url=token_url, code=authorization_code, include_client_id=True, client_secret=client_secret)


if token['token_type'] != 'bearer':
    raise SystemExit('Invalid Token received; exiting')


token_filename = '.NIBE_Uplink_API_Token.json'
with open(token_filename, 'w') as token_file:
    dump(token, token_file)


print('Token saved to file  ' + token_filename)

