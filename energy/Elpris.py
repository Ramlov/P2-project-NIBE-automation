from datetime import datetime, date, timedelta
import requests

class Elpris:

    def get_time(self):
        """ Gets the current time of the device running the code, returns today(today's date), hour(current hour) and hour_next(current hour + 1) """
        today = date.today()
        now = datetime.now()
        hour = now.strftime("%H:00")
        hour_next = (now + timedelta(hours=1)).strftime("%H:00")
        return today, hour, hour_next

    def get_pricedata(self) -> list:
        """ Outputs a list with today's raw energy price in kr./kWh without VAT """
        today, hour, hour_next = self.get_time()
        URL=f"https://api.energidataservice.dk/dataset/Elspotprices?start={today}T{hour}&end={today}T{hour_next}&filter={{%22PriceArea%22:[%22DK1%22]}}"
        r = requests.get(URL)
        pricedata = r.json()
        pricedata_list = [pricedata["records"][0]["HourDK"], (pricedata["records"][0]["SpotPriceDKK"] / 1000)]
        return pricedata_list

    def add_fees(self, price_raw, hour, month) -> float:
        """ Adds VAT, transporttarifs and other things """
        price_vat = price_raw * 0.25                # Adds VAT to raw electric price
        price_elafgift = 0.008                      # Adds electric fee (paid to the state)
        price_energinet = ( 0.058 + 0.054 ) * 1.25  # Adds energi-net fee (paid to the transmission net-company)
        price_electriccompany = 0                   # Adds fee to the electrical company
        if 17 <= hour <= 21 and ( 1 <= month <= 3 or 10 <= month <= 12 ): # Adds the transport tarif (paid to the transmission net-company)
            price_tarif = 1.05619 * 1.25
        else:
            price_tarif = 0.432225 * 1.25
        price_total = (price_raw + price_vat + price_tarif + price_elafgift + price_energinet + price_electriccompany)
        return price_total

    def get_current_price(self) -> float:
        """ Calls functions and returns the current price for the current hour and add fees and extras """
        today, hour, null = self.get_time()
        hour = int(hour[0:2])
        month = str(today)[5:7]
        raw_price = self.get_pricedata()[1]
        total_price = self.add_fees(raw_price, hour, month)        
        return total_price

if __name__ == "__main__":
    price = Elpris()
    print(price.get_current_price())
