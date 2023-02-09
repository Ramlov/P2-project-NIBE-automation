import requests
from datetime import date
import pandas as pd

def getdate():
    today = str(date.today())
    dates = today.split('-')
    return dates

def collect_energy_prices():
    dates = getdate()
    url = f'https://www.elprisenligenu.dk/api/v1/prices/{dates[0]}/{dates[1]}-{dates[2]}_DK1.json'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        df.to_csv('data.csv', index=False)

def calc_good_price():
    df = pd.read_csv("data.csv")
    df_sum = df["DKK_per_kWh"].sum()
    print(df_sum/24)




collect_energy_prices()
calc_good_price()


