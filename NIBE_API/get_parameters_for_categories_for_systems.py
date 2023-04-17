from os import path
from json import dump, load
from requests_oauthlib import OAuth2Session

HTTP_STATUS_OK = 200

token_filename= '.NIBE_Uplink_API_Token_GET.json'

def token_saver(token):
    with open(token_filename, 'w') as token_file:
        dump(token, token_file)

client_id = '59682261e9f04ab9a867eb7cfa93e840' # (32 hex digits)
client_secret = '/xADpEzVVYraWKnP6lZvcbT2RX51N4TDSM34Lry+w7w=' # (44 characters)
token_url = 'https://api.nibeuplink.com/oauth/token'


with open(token_filename, 'r') as token_file:
    token = load(token_file)

extra_args = {'client_id': client_id, 'client_secret': client_secret}
nibeuplink = OAuth2Session(client_id=client_id, token=token, auto_refresh_url=token_url, auto_refresh_kwargs=extra_args, token_updater=token_saver)


response = nibeuplink.get('https://api.nibeuplink.com/api/v1/systems')
if response.status_code != HTTP_STATUS_OK:
    print('HTTP Status: ' + str(response.status_code))
    print(response.text)
    raise SystemExit('API call not successful')
systems = response.json()['objects']

for system in systems:
    system_id = system['systemId']
    print(system_id)
    print('System Id:  ' +  str(system_id))
    response = nibeuplink.get('https://api.nibeuplink.com/api/v1/systems/' + str(system_id) + '/units')
    if response.status_code != HTTP_STATUS_OK:
        print('HTTP Status: ' + str(response.status_code))
        print(response.text)
        raise SystemExit('API call not successful')
    units = response.json()
    print(units)
    for unit in units:
        unit_id = unit['systemUnitId']
        print('\tUnit Id:  ', unit_id)

        params = {'systemUnitId': unit_id}
        print("Mathais   ", params)
        response = nibeuplink.get('https://api.nibeuplink.com/api/v1/systems/' + str(system_id) + '/serviceinfo/categories', params=params)
        if response.status_code != HTTP_STATUS_OK:
            print('HTTP Status: ' + str(response.status_code))
            print(response.text)
            raise SystemExit('API call not successful')
        
        categories = response.json()

        for category in categories:
            category_id = category['categoryId']
            print('\t\tCategory Id:  ', category_id)
            response = nibeuplink.get('https://api.nibeuplink.com/api/v1/systems/' + str(system_id) + '/serviceinfo/categories/' + str(category_id), params=params)
            if response.status_code != HTTP_STATUS_OK:
                print('HTTP Status: ' + str(response.status_code))
                print(response.text)
                raise SystemExit('API call not successful')
            
            #   The JSON output is simply an array of Parameters
            parameters = response.json()
            
            for parameter in parameters:
                parameter_id = parameter['parameterId']
                parameter_name = parameter['name']
                parameter_title = parameter['title']
                parameter_designation = parameter['designation']
                parameter_unit = parameter['unit']
                parameter_display_value = parameter['displayValue']
                parameter_raw_value = parameter['rawValue']
                print('\t\t\tParameter Id:              ' + str(parameter_id))
                print('\t\t\t\tParameter Name:          ' + str(parameter_name))
                print('\t\t\t\tParameter Title:         ' + str(parameter_title))
                print('\t\t\t\tParameter Designation:   ' + str(parameter_designation))
                print('\t\t\t\tParameter Unit:          ' + str(parameter_unit))
                print('\t\t\t\tParameter Display Value: ' + str(parameter_display_value))
                print('\t\t\t\tParameter Raw Value:     ' + str(parameter_raw_value))
