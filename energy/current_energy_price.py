import requests
from datetime import datetime, date, timedelta

class ElectricityPricing:
    def __init__(self):
        self.url = "https://api.energidataservice.dk/dataset/Elspotprices"
        self.price_areas = ["DK1"]
        self.vat_rate = 0.25
        self.tarif_1_rate = 1.05619
        self.tarif_2_rate = 0.432225
        self.elafgift_rate = 0.008
        self.energinet_rate = (0.058 + 0.054) * 1.25
        self.electric_company_rate = 0  # <----------------------- Vi skal finde ud af, hvad Preb betaler pr kWh til Norlys

    def get_time(self):
        try:
            today = date.today()
            now = datetime.now()
            hour = now.strftime("%H:00")
            hour_next = (now + timedelta(hours=1)).strftime("%H:00")
            return today, hour, hour_next
        except Exception as e:
            print(f"An error occurred while getting time: {e}")
            return None, None, None

    def get_pricedata(self):
        try:
            today, hour, hour_next = self.get_time()
            if not all([today, hour, hour_next]):
                return 0
            params = {
                "start": f"{today}T{hour}",
                "end": f"{today}T{hour_next}",
                "filter": f'{{"PriceArea":["{self.price_areas[0]}"]}}'
            }
            
            r = requests.get(self.url, params=params)
            r.raise_for_status()
            pricedata = r.json()
            pricedata_list = [pricedata["records"][0]["HourDK"], (pricedata["records"][0]["SpotPriceEUR"] / 1000)]
            return pricedata_list
        except Exception as e:
            print(f"An error occurred while getting price data: {e}")
            return 0

    def add_to_price(self, price_raw, hour, month):
        try:
            price_vat = price_raw * self.vat_rate
            if 17 <= int(hour) <= 20 and (1 <= int(month) <= 3 or 10 <= int(month) <= 12):
                price_tarif = self.tarif_1_rate * 1.25           
            else:
                price_tarif = self.tarif_2_rate * 1.25
            price_total = (price_raw + price_vat + price_tarif + self.elafgift_rate + self.energinet_rate + self.electric_company_rate)
            return price_total
        except Exception as e:
            print(f"An error occurred while calculating price: {e}")
            return 0

    def get_current_price(self):
        try:
            today, hour, null = self.get_time()
            hour = int(hour[0:2])
            month = str(today)[5:7]
            raw_price = (self.get_pricedata()[1]*7.44697)
            total_price = self.add_to_price(raw_price, hour, month)        
            return total_price
        except Exception as e:
            print(f"Error occurred: {e}")
            return 0


ep = ElectricityPricing()

print(ep.get_current_price())