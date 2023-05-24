import ntplib
import os
from datetime import datetime
import pytz

def update_time_ntp():
    try:
        ntp_server = 'pool.ntp.org'
        client = ntplib.NTPClient()
        response = client.request(ntp_server, version=3)
        utc_time = datetime.fromtimestamp(response.tx_time, tz=pytz.utc)
        target_timezone = pytz.timezone('Europe/Copenhagen')
        target_time = utc_time.astimezone(target_timezone)
        time_format = '%Y-%m-%d %H:%M:%S'
        formatted_time = target_time.strftime(time_format)
        os.system('sudo date -s "%s"' % formatted_time)
        print("Time updated successfully:", formatted_time)
    except Exception as e:
        print("Error updating time:", str(e))


update_time_ntp()