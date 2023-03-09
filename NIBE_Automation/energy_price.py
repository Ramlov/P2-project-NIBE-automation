import requests
from datetime import date, timedelta
import csv
import pandas as pd

class EnergyPriceCollector:

    def __init__(self):
        self.data_file = 'data.csv'
    
    def getdate(self):
        today = str(date.today())
        dates = today.split('-')
        return dates

    #def getdate(self):
    # #   tomorrow = date.today() + timedelta(days=1)
    #    tomorrow_str = str(tomorrow)
    #    dates = tomorrow_str.split('-')
    #    print(dates)
    #    return dates

    def collect_energy_prices(self):
        dates = self.getdate()
        url = f'https://www.elprisenligenu.dk/api/v1/prices/{dates[0]}/{dates[1]}-{dates[2]}_DK1.json'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            df.to_csv(self.data_file, index=False)
        self.fees()
        self.sort_price()

    def fees(self):
        df = pd.read_csv(self.data_file)
        date = int(self.getdate()[1])
        if date <= 3 or date > 9:
            print("un3")
            df.iloc[0:6, df.columns.get_loc("DKK_per_kWh")] +=0.2127
            df.iloc[6:17, df.columns.get_loc("DKK_per_kWh")] +=0.6379
            df.iloc[17:21, df.columns.get_loc("DKK_per_kWh")] +=1.9135
            df.iloc[21:24, df.columns.get_loc("DKK_per_kWh")] +=0.6379
        elif date > 3:
            print("ove3")
            df.iloc[0:6, df.columns.get_loc("DKK_per_kWh")] +=0.2127
            df.iloc[6:17, df.columns.get_loc("DKK_per_kWh")] +=0.3189
            df.iloc[17:21, df.columns.get_loc("DKK_per_kWh")] +=0.8292
            df.iloc[21:24, df.columns.get_loc("DKK_per_kWh")] +=0.3189

        df.to_csv(self.data_file, index=False)

    def sort_price(self):
        df = pd.read_csv(self.data_file)
        sorted_df = df.sort_values('DKK_per_kWh')
        num_rows = len(sorted_df)
        third = num_rows // 3
        lowest = sorted_df.iloc[:third]
        middle = sorted_df.iloc[third:-third]
        highest = sorted_df.iloc[-third:]
        df['turn_on'] = ''
        df.loc[lowest.index, 'turn_on'] = 'True'
        df.loc[middle.index, 'turn_on'] = 'Normal'
        df.loc[highest.index, 'turn_on'] = 'False'
        df.to_csv(self.data_file, index=False)

price_collector = EnergyPriceCollector() 

price_collector.collect_energy_prices()
