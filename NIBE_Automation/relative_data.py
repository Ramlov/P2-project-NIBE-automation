import requests
from datetime import datetime, date, timedelta
import pandas as pd
from time import sleep
import numpy as np
import json

class ElectricityPricing:
    def __init__(self):
        self.BASE_URL = "https://api.energidataservice.dk/dataset/Elspotprices"
        self.PRICE_AREA = "DK1"
        self.VAT_FACTOR = 0.25
        self.TARIF_HIGH_RATE = 1.05619
        self.TARIF_LOW_RATE = 0.432225
        self.ELAFGIFT_RATE = 0.008
        self.ENERGINET_RATE = (0.058 + 0.054) * 1.25
        self.ELECTRIC_COMPANY_RATE = 0

    def get_time(self):
        try:
            tomorrow = date.today() + timedelta(days=0)
            tomorrow2 = date.today() + timedelta(days=1)
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
                "filter": f'{{"PriceArea":["{self.PRICE_AREA}"]}}'
            }
            r = requests.get(self.BASE_URL, params=params)
            r.raise_for_status()
            pricedata = r.json()
            df = pd.DataFrame(pricedata)
            df.to_csv('pricedata.csv', index=False)
            df = pd.read_csv('pricedata.csv')
            df = pd.json_normalize(df['records'].apply(eval))
            df = df[['HourDK', 'SpotPriceDKK']]
            df = df.sort_values(by=['HourDK'], ascending=True)
            df['SpotPriceDKK'] = df['SpotPriceDKK'] / 1000
            self.add_to_price((datetime.now().month), df)
            df.to_csv('pricedata.csv', index=False)
        except Exception as e:
            print(f"An error occurred while getting price data: {e}")
        
    def add_to_price(self, month,  df):
        try:
            df['SpotPriceDKK'] *= 1.25
            if 1 <= int(month) <= 3 or 10 <= int(month) <= 12:
                price_tarif = self.TARIF_HIGH_RATE * 1.25  
                df.iloc[17:20, df.columns.get_loc("SpotPriceDKK")] += price_tarif
                price_tarif = self.TARIF_LOW_RATE * 1.25
                df.loc[~df.index.isin(range(17, 20)), 'SpotPriceDKK'] += price_tarif  
            else:
                price_tarif = self.TARIF_LOW_RATE * 1.25
                df['SpotPriceDKK'] += price_tarif  
            df['SpotPriceDKK'] += self.ELAFGIFT_RATE + self.ENERGINET_RATE + self.ELECTRIC_COMPANY_RATE
            df.to_csv('pricedata.csv', index=False) 
        except Exception as e:
            print(f"An error occurred while calculating price: {e}")

class Temperature:
    def __init__(self) -> None:
        self.POSITION = {"lat": 56.985460, "long": 9.985583}
        self.tomorrow = (datetime.today() + timedelta(days=0)).strftime("%Y-%m-%d")
        self.tomorrow2 = (datetime.today() + timedelta(days=0)).strftime("%Y-%m-%d")
        self.API_URL=f"https://api.open-meteo.com/v1/metno?latitude={self.POSITION['lat']}&longitude={self.POSITION['long']}&hourly=temperature_2m&timezone=Europe%2FBerlin&start_date={self.tomorrow}&end_date={self.tomorrow2}"
       
    def get_tempdata(self) -> dict:
        try:
            r = requests.get(self.API_URL)
            tempdata = r.json()
            return tempdata
        except Exception as e:
            print(f"An error occurred while getting tempdata: {e}")

    def sort_tempdata(self, raw_data) -> dict:
        try:
            tempdict = {"HourDK": raw_data["hourly"]["time"][:24],
                        "Temperature": raw_data["hourly"]["temperature_2m"][:24]}
            return tempdict
        except Exception as e:
            print(f"An error occurred while sorting price: {e}")
            return None

    def write_csv(self, datalist) -> None:
        try:
            df = pd.DataFrame(datalist)
            df = df.sort_values(by=["HourDK"], ascending=True)
            df.to_csv("tempdata.csv", index=False)
        except Exception as e:
            print(f"An error occurred while writing tempdata to csv: {e}")

class Combine:
    def __init__(self) -> None:
        try:
            temp = Temperature()
            temp.write_csv(temp.sort_tempdata(temp.get_tempdata()))
            ep = ElectricityPricing()
            ep.get_pricedata()
        except Exception as e:
            print(f"An error occurred while instantiating class Combine: {e}")

    def combine_data(self) -> None:
        try:
            df_price = pd.read_csv('pricedata.csv')
            df_temp = pd.read_csv('tempdata.csv')
            new = {"HourDK": [], "SpotPriceDKK": [], "Temperature": []}
            df_new = pd.DataFrame(new)
            df_new["HourDK"] = df_temp["HourDK"]
            df_new["SpotPriceDKK"] = df_price["SpotPriceDKK"]
            df_new["Temperature"] = df_temp["Temperature"]
            df_new['HourDK'] = pd.to_datetime(df_new['HourDK'])
            df_new['COP'] = 0.0033 * df_new['Temperature'] ** 2 + 0.0667 * df_new['Temperature'] + 3.2 
            df_new['CHP'] = df_new['SpotPriceDKK'] / df_new['COP']

            df_new = df_new.sort_values('CHP')

            max_chp = df_new['CHP'].max()
            min_chp = df_new['CHP'].min()

            df_new['Offset'] = ((df_new['CHP'] - min_chp) / (max_chp - min_chp) * 20) - 10

            df_new['Offset'] = np.where(df_new['CHP'] < df_new['CHP'].median(), df_new['Offset'].abs(), -df_new['Offset'].abs())

            df_new['Offset'] = df_new['Offset'].round()
            df_new.to_csv('combineddata.csv', index=False)
        except Exception as e:
            print(f"An error occurred while combining price- and tempdata: {e}")

    def check_data(self):
        data = {
            "username": "NIBE Bot",
            "embeds": [
                {
                    "title": "The Automator",
                    "color": 5763719,
                    "description": f'Price collected! \nBot still going strong!',
                    "footer": {
                        "text": "Author: Ramlov",
                        "icon_url": "https://avatars.githubusercontent.com/u/17428562?v=4",
                        "url": "https://github.com/Ramlov"
                    }
                }
            ]
        }
        while True:
            try:
                df = pd.read_csv('combineddata.csv')
                if len(df) > 22:
                    payload = json.dumps(data)
                    requests.post("https://discord.com/api/webhooks/1092461466000576764/TZuzacO5VbowCLekKPDdESvZxK4UBmLVVcNWc9U5J4CuqYXarEVdLB-A02Vu4PRJMtjz", data=payload, headers={"Content-Type": "application/json"})
                    break
            except:
                sleep(5*60)
                self.combine_data()



if __name__ == "__main__":
    comb = Combine()
    comb.combine_data()
    comb.check_data()
