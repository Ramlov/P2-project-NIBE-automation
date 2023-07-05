import sqlite3
from datetime import datetime, timedelta

def savings(hours_back):
    conn = sqlite3.connect("ramlov.db")
    cursor = conn.cursor()

    now = datetime.now()
    start_time = now - timedelta(hours=hours_back)
    end_time = now

    query = f"SELECT value, price, value * price as value_price FROM pulse_data WHERE time BETWEEN '{start_time}' AND '{end_time}'"
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    sum_value = sum(row[0] for row in rows) / 1000
    avg_price = sum(row[1] for row in rows) / len(rows)
    try: value_price_total = (sum(row[2] for row in rows) / 1000) / sum_value 
    except: value_price_total = 0
    price_used = value_price_total * sum_value
    price_avg = avg_price * sum_value
    saved = price_avg-price_used

    return saved


print(savings(1000))