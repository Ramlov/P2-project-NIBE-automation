from flask import Flask, render_template, request, redirect
from helper_class import helper
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pymysql
import pandas as pd
import json

#from waitress import serve

helpers = helper()

app = Flask(__name__)

with open('config.json', 'r') as file:
    config = json.load(file)
# MySQL database connection details
db_host = config['database']['host']
db_name = config['database']['dbname']
db_username = config['database']['username']
db_password = config['database']['password']

@app.route('/', methods=['GET', 'POST'])
def home():
    chart = heating_chart()
    if request.method == 'POST' and 'submit' in request.form:
        temp = request.form['temp']
        helpers.put_request(temp)
        return render_template('index.html',heating_chart=chart, varme_temperatur=temp, pump_speed=helpers.get_request(43437), flow_temp=helpers.get_request(40014), udendors_temperatur=helpers.get_request(40004), last_usage_kwh=helpers.usage(24)[0], last_usage_dkk=round(helpers.usage(24)[2],2))
    else:
        return render_template('index.html',heating_chart=chart, pump_speed=helpers.get_request(43437), flow_temp=helpers.get_request(40014), udendors_temperatur=helpers.get_request(40004), last_usage_kwh=helpers.usage(24)[0], last_usage_dkk=round(helpers.usage(24)[2],2))

@app.route('/heating_chart')
def heating_chart():
    conn = pymysql.connect(host=db_host, user=db_username, passwd=db_password, db=db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT HourDK, SpotPriceDKK, TurnOn FROM heating")
    data = cursor.fetchall()
    hours = [row[0] for row in data]
    spot_prices = [row[1] for row in data]
    turn_on = [row[2] for row in data]

    cursor.close()
    conn.close()

    # Create the plot
    fig = make_subplots(rows=1, cols=1, specs=[[{'secondary_y': True}]])
    fig.add_trace(go.Scatter(x=hours, y=spot_prices, mode='lines', marker=dict(color='orange'), name='Spot Price DKK'), row=1, col=1, secondary_y=True)
    fig.add_trace(go.Scatter(x=hours, y=turn_on, mode='lines', marker=dict(color='green'), name='Turn On'), row=1, col=1, secondary_y=False)
    fig.update_yaxes(title_text='Spot Price DKK', secondary_y=True)
    fig.update_yaxes(title_text='Turn On', secondary_y=False)
    fig.update_layout(title='Heating Data Line Plot', xaxis_title='HourDK')

    chart = fig.to_html(full_html=False)
    return chart
    #return render_template('index.html', heating_chart=chart)


@app.route('/chart')
def chart():
    conn = pymysql.connect(host=db_host, user=db_username, passwd=db_password, db=db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT time, value, price FROM pulse_data")
    data = cursor.fetchall()
    times = [row[0] for row in data]
    values = [row[1] for row in data]
    prices = [row[2] for row in data]

    cursor.close()
    conn.close()

    fig = make_subplots(rows=1, cols=1, specs=[[{'secondary_y': True}]])
    fig.add_trace(go.Scatter(x=times, y=values, mode='lines', marker=dict(color='green'), name='Value'), row=1, col=1, secondary_y=False)
    fig.add_trace(go.Scatter(x=times, y=prices, mode='lines', marker=dict(color='orange'), name='Price'), row=1, col=1, secondary_y=True)
    fig.update_yaxes(title_text='Value', secondary_y=False)
    fig.update_yaxes(title_text='Price', secondary_y=True)
    fig.update_layout(title='Pulse Data Line Plot', xaxis_title='Time')


    last_7_days = pd.Timestamp.now() - pd.DateOffset(days=7)
    fig.update_xaxes(range=[last_7_days, pd.Timestamp.now()])
    chart = fig.to_html(full_html=False)

    return render_template('usage/chart.html', chart=chart)



@app.route('/test')
def test():
  # do something
  print('Function called successfully.')
  return("")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
   #app.run(debug=True)
