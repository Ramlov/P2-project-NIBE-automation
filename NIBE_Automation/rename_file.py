import pandas as pd
import os
import json
import requests
import datetime

# Get current date and tomorrow's date
now = datetime.datetime.now()
tomorrow = now + datetime.timedelta(days=1)

# Format the date string
date_string = "{} the {} of {}".format(tomorrow.strftime('%A'), tomorrow.strftime('%d'), tomorrow.strftime('%B'))

# Prepare the data for the notification
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
    """
    Renames a CSV file.

    This function renames a CSV file from the old file path to the new file path.

    Args:
        old_file_path (str): The current path of the CSV file.
        new_file_path (str): The new path to rename the CSV file.

    Returns:
        None
    """
    try:
        os.rename(old_file_path, new_file_path)
        print(f"CSV file renamed from '{old_file_path}' to '{new_file_path}' successfully!")
    except OSError as e:
        print(f"Failed to rename CSV file: {e}")

# Specify the paths for the old and new CSV files
old_file_path = "combineddata.csv"
new_file_path = "data.csv"

# Rename the CSV file
rename_csv_file(old_file_path, new_file_path)

# Send the notification with the prepared data
payload = json.dumps(data)
requests.post(" ", data=payload, headers={"Content-Type": "application/json"})
