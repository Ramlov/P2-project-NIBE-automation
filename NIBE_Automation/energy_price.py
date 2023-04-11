import requests
from datetime import datetime, date, timedelta
import pandas as pd

class ElectricityPricing:
    def __init__(self):
        self.url = "https://api.energidataservice.dk/dataset/Elspotprices"
        self.price_areas = "DK1"
        self.vat_rate = 0.25
        self.tarif_1_rate = 1.05619
        self.tarif_2_rate = 0.432225
        self.elafgift_rate = 0.008
        self.energinet_rate = (0.058 + 0.054) * 1.25
        self.electric_company_rate = 0

    def get_time(self):
        try:
            tomorrow = date.today() + timedelta(days=1)
            tomorrow2 = date.today() + timedelta(days=2)
            hour = "00:00"
            return tomorrow, tomorrow2, hour
        except Exception as e:
            print(f"An error occurred while getting time: {e}")
            return None, None, None

    def get_pricedata(self):
        try:
            tomorrow, tomorrow2, hour = self.get_time()
            params = {
                "start": f"{tomorrow}T{hour}",
                "end": f"{tomorrow2}T{hour}",
                "filter": f'{{"PriceArea":["{self.price_areas}"]}}'
            }
            r = requests.get(self.url, params=params)
            r.raise_for_status()
            pricedata = r.json()
            df = pd.DataFrame(pricedata)
            df.to_csv('data.csv', index=False)
            df = pd.read_csv('data.csv')
            df = pd.json_normalize(df['records'].apply(eval))
            df = df[['HourDK', 'SpotPriceDKK']]
            df = df.sort_values(by=['HourDK'], ascending=True)
            df['SpotPriceDKK'] = df['SpotPriceDKK'] / 1000
            df.to_csv('data.csv', index=False)
        except Exception as e:
            print(f"An error occurred while getting price data: {e}")
        
    def add_to_price(self, month):
        df = pd.read_csv('data.csv')
        try:
            if 1 <= int(month) <= 3 or 10 <= int(month) <= 12:
                price_tarif = self.tarif_1_rate * 1.25  
                df.iloc[17:20, df.columns.get_loc("SpotPriceDKK")] += price_tarif
                price_tarif = self.tarif_2_rate * 1.25
                df.loc[~df.index.isin(range(17, 20)), 'SpotPriceDKK'] += price_tarif  
            else:
                price_tarif = self.tarif_2_rate * 1.25
                df['SpotPriceDKK'] += price_tarif  
            df.to_csv('data.csv', index=False) 
        except Exception as e:
            print(f"An error occurred while calculating price: {e}")


    def sort_price(self):
        df = pd.read_csv('data.csv')
        sorted_df = df.sort_values('SpotPriceDKK')
        num_rows = len(sorted_df)
        third = num_rows // 3
        lowest = sorted_df.iloc[:third]
        middle = sorted_df.iloc[third:-third]
        highest = sorted_df.iloc[-third:]
        df['turn_on'] = ''
        df.loc[lowest.index, 'turn_on'] = 'True'
        df.loc[middle.index, 'turn_on'] = 'Normal'
        df.loc[highest.index, 'turn_on'] = 'False'
        df.to_csv('data.csv', index=False)
    
    def collect_energy_prices(self):
        try:
            self.get_pricedata()
            self.add_to_price((datetime.now().month))
            self.sort_price()
            return "Got Prices"
        except Exception as e:
            return f'An error occured: {e}'
        
