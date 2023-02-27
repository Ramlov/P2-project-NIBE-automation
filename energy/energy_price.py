import requests
from datetime import date
import csv
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

def fees():
    data="data.csv"
    df =pd.read_csv(data)
    df.iloc[0:6, df.columns.get_loc("DKK_per_kWh")] +=0.2127
    df.iloc[6:17, df.columns.get_loc("DKK_per_kWh")] +=0.6379
    df.iloc[17:21, df.columns.get_loc("DKK_per_kWh")] +=1.9135
    df.iloc[21:24, df.columns.get_loc("DKK_per_kWh")] +=0.6379
    df.to_csv("data.csv", index=False)



collect_energy_prices()
fees()
#calc_good_price()


