import requests
from datetime import datetime, date, timedelta
from time import sleep
import pandas as pd
import json

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
                "filter": f'{{"PriceArea":["{self.price_areas}"]}}'
            }
            r = requests.get(self.url, params=params)
            r.raise_for_status()
            pricedata = r.json()
            df = pd.DataFrame(pricedata)
            df.to_csv('pricedata.csv', index=False)
            df = pd.read_csv('pricedata.csv')
            df = pd.json_normalize(df['records'].apply(eval))
            df = df[['HourDK', 'SpotPriceDKK']]
            df = df.sort_values(by=['HourDK'], ascending=True)
            df['SpotPriceDKK'] = df['SpotPriceDKK'] / 1000
            df.to_csv('pricedata.csv', index=False)
        except Exception as e:
            print(f"An error occurred while getting price data: {e}")
        
    def add_to_price(self, month):
        try:
            df = pd.read_csv('pricedata.csv')
            if 1 <= int(month) <= 3 or 10 <= int(month) <= 12:
                price_tarif = self.tarif_1_rate * 1.25  
                df.iloc[17:20, df.columns.get_loc("SpotPriceDKK")] += price_tarif
                price_tarif = self.tarif_2_rate * 1.25
                df.loc[~df.index.isin(range(17, 20)), 'SpotPriceDKK'] += price_tarif  
            else:
                price_tarif = self.tarif_2_rate * 1.25
                df['SpotPriceDKK'] += price_tarif  
            df.to_csv('pricedata.csv', index=False) 
        except Exception as e:
            print(f"An error occurred while calculating price: {e}")

    def sort_price(self):
        try:
            df = pd.read_csv('pricedata.csv')
            sorted_df = df.sort_values('SpotPriceDKK')
            num_rows = len(sorted_df)
            third = num_rows // 3
            lowest = sorted_df.iloc[:third]
            middle = sorted_df.iloc[third:-third]
            highest = sorted_df.iloc[-third:]
            df['SpotPriceRelative'] = ''
            df.loc[lowest.index, 'SpotPriceRelative'] = 'Cheap'
            df.loc[middle.index, 'SpotPriceRelative'] = 'Normal'
            df.loc[highest.index, 'SpotPriceRelative'] = 'Expensive'
            df.to_csv('pricedata.csv', index=False)
        except Exception as e:
            print(f"An error occurred while sorting price: {e}")
    
    def collect_energy_prices(self):
        try:
            self.get_pricedata()
            self.add_to_price((datetime.now().month))
            self.sort_price()
            return "Got Prices"
        except Exception as e:
            return f'An error occured: {e}'

class Temperature:
    def __init__(self) -> None:
        self.POSITION = {"lat": 56.985460, "long": 9.985583}
        self.today = (datetime.today()).strftime("%Y-%m-%d")
        self.tomorrow = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        self.API_URL=f"https://api.open-meteo.com/v1/metno?latitude={self.POSITION['lat']}&longitude={self.POSITION['long']}&hourly=temperature_2m&timezone=Europe%2FBerlin&start_date={self.today}&end_date={self.tomorrow}"
        #self.API_URL=f"https://api.open-meteo.com/v1/forecast?latitude={self.POSITION['lat']}&longitude={self.POSITION['long']}&hourly=temperature_2m&timezone=Europe%2FBerlin&start_date={self.today}&end_date={self.tomorrow}"
        # Jeg er ikke helt sikker på, hvad forskellen på de to API'er er (og om der er forskel), det returnerer i dag samme temperatur

    def get_tempdata(self) -> dict:
        try:
            r = requests.get(self.API_URL)
            tempdata = r.json()
            return tempdata
        except Exception as e:
            print(f"An error occurred while getting tempdata: {e}")

    def sort_tempdata(self, raw_data) -> dict:
        try:
            tempdict = {"HourDK": [], "Temperature": []}
            for i in range(24): #DEBUG
                time = raw_data["hourly"]["time"][i]
                temp = raw_data["hourly"]["temperature_2m"][i]
                #print(f"Time: {time} - Temperature: {temp}")
                tempdict["HourDK"].append(time)
                tempdict["Temperature"].append(temp)
            return tempdict

        except Exception as e:
            print(f"An error occurred while sorting price: {e}")
            return None


    def write_csv(self, datalist) -> None:
        try:
            df = pd.DataFrame(datalist)
            df = df.sort_values(by=["HourDK"], ascending=True)
            df.to_csv("tempdata.csv", index=False)

            df = pd.read_csv("tempdata.csv")
            sorted_df = df.sort_values("Temperature")
            lowest = sorted_df.iloc[:6]
            highest = sorted_df.iloc[-6:]
            df["TemperatureRelative"] = 'Normal'
            df.loc[lowest.index, "TemperatureRelative"] = 'Cold'
            df.loc[highest.index, "TemperatureRelative"] = 'Hot'
            df.to_csv('tempdata.csv', index=False)
        except Exception as e:
            print(f"An error occurred while writing tempdata to csv: {e}")

class Combine:
    def __init__(self) -> None:
        try:
            temp = Temperature()
            temp.write_csv(temp.sort_tempdata(temp.get_tempdata()))
            ep = ElectricityPricing()
            ep.collect_energy_prices()
        except Exception as e:
            print(f"An error occurred while instantiating class Combine: {e}")

    def combine_data(self) -> None:
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
        try:
            df_price = pd.read_csv('pricedata.csv')
            df_temp = pd.read_csv('tempdata.csv')
            new = {"HourDK": [], "SpotPriceDKK": [], "Temperature": [], "SpotPriceRelative": [],  "TemperatureRelative": [], "TurnOn": []}
            df_new = pd.DataFrame(new)
            df_new["HourDK"] = df_temp["HourDK"]
            df_new["SpotPriceDKK"] = df_price["SpotPriceDKK"]
            df_new["Temperature"] = df_temp["Temperature"]
            df_new["SpotPriceRelative"] = df_price["SpotPriceRelative"]
            df_new["TemperatureRelative"] = df_temp["TemperatureRelative"]
            for i in range(len(df_new["HourDK"])):
                if df_new["SpotPriceRelative"][i] == "Cheap":
                    df_new.loc[i, ("TurnOn")] = True
                elif df_new["SpotPriceRelative"][i] == "Normal" and df_new["TemperatureRelative"][i] == "Hot":
                    df_new.loc[i, ("TurnOn")] = True
                elif df_new["SpotPriceRelative"][i] == "Normal":
                    df_new.loc[i, ("TurnOn")] = "Normal"
                else:
                    df_new.loc[i, ("TurnOn")] = False
            df_new.to_csv('combineddata.csv', index=False)
            payload = json.dumps(data)
            requests.post("https://discord.com/api/webhooks/1092461466000576764/TZuzacO5VbowCLekKPDdESvZxK4UBmLVVcNWc9U5J4CuqYXarEVdLB-A02Vu4PRJMtjz", data=payload, headers={"Content-Type": "application/json"})
        except Exception as e:
            print(f"An error occurred while combining price- and tempdata: {e}")
    
    def check_data(self):
        while True:
            try:
                df = pd.read_csv('combineddata.csv')
                if len(df) > 22:
                    print(df)
                    print(len(df))
                    print("Data")
                    break
            except:
                self.combine_data()
                sleep(3*60)

if __name__ == "__main__":
    comb = Combine()
    comb.combine_data()
    comb.check_data()
