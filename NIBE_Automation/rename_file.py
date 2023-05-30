import pandas as pd
import os
import json
import requests
import datetime

now = datetime.datetime.now()
tomorrow = now + datetime.timedelta(days=1)

date_string = "{} the {} of {}".format(tomorrow.strftime('%A'), tomorrow.strftime('%d'), tomorrow.strftime('%B'))

data = {
    "username": "NIBE Bot",
    "embeds": [
        {
            "title": "The Automator",
            "color": 10181046,
            "description": f'Heating system update to {date_string}! \nBot still going strong!',
            "footer": {
                "text": "Author: Ramlov",
                "icon_url": "https://avatars.githubusercontent.com/u/17428562?v=4",
                "url": "https://github.com/Ramlov"
            }
        }
    ]
}



def rename_csv_file(old_file_path, new_file_path):
    try:
        os.rename(old_file_path, new_file_path)
        print(f"CSV file renamed from '{old_file_path}' to '{new_file_path}' successfully!")
    except OSError as e:
        print(f"Failed to rename CSV file: {e}")

old_file_path = "combineddata.csv"
new_file_path = "data.csv"
rename_csv_file(old_file_path, new_file_path)
payload = json.dumps(data)
requests.post(" ", data=payload, headers={"Content-Type": "application/json"})
