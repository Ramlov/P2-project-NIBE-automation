import requests
from datetime import datetime, date, timedelta
import pandas as pd
from time import sleep
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
        """
        Gets the current time from the system RTC.

        Args:
            None

        Returns:
            tuple: A tuple containing the date of tomorrow, the day after tomorrow and the hour 00:00.
        """
        try:
            tomorrow = date.today() + timedelta(days=1)
            tomorrow2 = date.today() + timedelta(days=2)
            hour = "00:00"
            return tomorrow, tomorrow2, hour
        except Exception as e:
            print(f"An error occurred while getting time: {e}")
            return None, None, None

    def get_pricedata(self):
        """
        Retrieves electricity prices for the forthcoming day and formats it into a csv-table and saves it as pricedata.csv
        Fees and tarifs are added to the price list using self.add_to_price()

        Args:
            None

        Returns:
            None, output is saved to pricedata.csv
        """
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
        
    def add_to_price(self, month, df):
        """
        Appends fees and tarifs to a dataframe. 

        Args:
            month (int): the current month in number-format; eg. 3 = mar and 12 = dec.
            df (pandas DataFrame): A table with pricedata. The column "SpotPriceDKK" contains the hourly electricity prices

        Returns:
            None, output is saved to pricedata.csv
        """
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
        self.POSITION = {"lat": 12.345678, "long": 98.765432} # <-------------------------------------------------------------------- # Enter coordinates of location.
        self.tomorrow = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        self.API_URL=f"https://api.open-meteo.com/v1/metno?latitude={self.POSITION['lat']}&longitude={self.POSITION['long']}&hourly=temperature_2m&timezone=Europe%2FBerlin&start_date={self.tomorrow}&end_date={self.tomorrow}"
       
    def get_tempdata(self) -> dict:
        """
        Retrieves temperature forecast for the forthcoming day

        Args:
            None

        Returns:
            tempdata as a json-object.
        """
        try:
            r = requests.get(self.API_URL)
            tempdata = r.json()
            return tempdata
        except Exception as e:
            print(f"An error occurred while getting tempdata: {e}")

    def sort_tempdata(self, raw_data) -> dict:
        """
        Formats temperature data into a csv-table and sorts it after ascending hour.

        Args:
            raw_data (json): raw temperature data fetched in self.get_tempdata()

        Returns:
            tempdata as key-value pairs (dictionary) with the hour as the key and the temp as the value
        """
        try:
            tempdict = {"HourDK": raw_data["hourly"]["time"][:24],
                        "Temperature": raw_data["hourly"]["temperature_2m"][:24]}
            return tempdict
        except Exception as e:
            print(f"An error occurred while sorting price: {e}")
            return None

    def write_csv(self, datalist) -> None:
        """
        Saves the input datalist to a csv named tempdata.csv

        Args:
            datalist (dictionary): A key-value dictionary containting HourDK - hours and Temperature - forecasted temperatures.

        Returns:
            None, output is saved to tempdata.csv
        """
        try:
            df = pd.DataFrame(datalist)
            df = df.sort_values(by=["HourDK"], ascending=True)
            df.to_csv("tempdata.csv", index=False)
        except Exception as e:
            print(f"An error occurred while writing tempdata to csv: {e}")

class Combine:
    def __init__(self) -> None:
        """
        Constructs a combine-object. Instantiates Temperature- and ElectricityPricing-objects and uses them to fetch data.

        Args:
            None

        Returns:
            None
        """
        try:
            temp = Temperature()
            temp.write_csv(temp.sort_tempdata(temp.get_tempdata()))
            ep = ElectricityPricing()
            ep.get_pricedata()
        except Exception as e:
            print(f"An error occurred while instantiating class Combine: {e}")

    def combine_data(self) -> None:
        """
        Loads data from Temperature- and ElectricityPricing-objects that are saved as csv-files and combines them to a new table.
        Calculates COP(estimated) and CHP. From this a new column, "TurnOn" is filled with 'False', 'True' or 'Normal' according to the CHP.
        The table is saved as the csv-file combineddata.csv

        Args:
            None

        Returns:
            None, data is saved in combineddata.csv
        """
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
            df_new['TurnOn'] = 'False'
            df_new.iloc[:6, -1] = 'True'
            df_new.iloc[6:12, -1] = 'Normal'
            df_new = df_new.sort_values('HourDK')
            df_new.to_csv('combineddata.csv', index=False)
        except Exception as e:
            print(f"An error occurred while combining price- and tempdata: {e}")

    def check_data(self):
        """
        Checks the integrity (length) of the submitted data.

        Args:
            None

        Returns:
            None
        """        
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
                    requests.post(" ", data=payload, headers={"Content-Type": "application/json"})
                    break
            except:
                sleep(5*60)
                self.combine_data()

if __name__ == "__main__":
    comb = Combine()
    comb.combine_data()
    comb.check_data()
