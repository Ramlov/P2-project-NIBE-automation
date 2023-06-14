from flask import Flask, render_template, request, redirect
from helper_class import helper
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pymysql, json
import pandas as pd
import datetime
import os
import sys
sys.path.append('/root/NIBE/')
from push_data import push



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
    """
    Renders the home page.

    Retrieves data from the Nibe Uplink API and the database to display on the home page.
    Handles the form submission to update the heating temperature parameter.

    Returns:
        str: The rendered HTML template of the home page.
    """
    now = datetime.datetime.now()
    date_string = "{} the {} of {}".format(now.strftime('%A'), now.strftime('%d'), now.strftime('%B'))
    chart = heating_chart()
    if request.method == 'POST' and 'submit' in request.form:
        temp = request.form['temp']
        helpers.put_request(parameter_id=47011, value=temp)
        return render_template('index.html',heating_chart=chart, date=date_string, 
                                varme_temperatur=temp, return_temp=helpers.get_request(40012,"SYSTEM_1"), 
                                pump_speed=helpers.get_request(43437,"STATUS"), flow_temp=helpers.get_request(40014,"STATUS"), 
                                udendors_temperatur=helpers.get_request(40004,"STATUS"), last_usage_kwh=round(helpers.usage(24)[0],2), 
                                last_usage_dkk=round(helpers.usage(24)[2],2), last7_usage_kwh=round(helpers.usage(168)[0],2), 
                                last7_usage_dkk=round(helpers.usage(168)[2],2))
    else:
        return render_template('index.html',heating_chart=chart, date=date_string, return_temp=helpers.get_request(40012,"SYSTEM_1"), 
                                pump_speed=helpers.get_request(43437,"STATUS"), flow_temp=helpers.get_request(40014,"STATUS"), 
                                udendors_temperatur=helpers.get_request(40004,"STATUS"), last_usage_kwh=round(helpers.usage(24)[0],2), 
                                last_usage_dkk=round(helpers.usage(24)[2],2), last7_usage_kwh=round(helpers.usage(168)[0],2), 
                                last7_usage_dkk=round(helpers.usage(168)[2],2))

@app.route('/heating_chart')
def heating_chart():
    """
    Retrieves data from the database and creates a heating chart.

    Returns:
        str: The HTML representation of the heating chart.
    """
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
    fig.update_layout(xaxis_title='Hour')

    chart = fig.to_html(full_html=False)
    return chart


@app.route('/chart')
def chart():
    """
    Renders the usage chart page.

    Retrieves data from the database and creates a line chart to display the usage data.

    Returns:
        str: The rendered HTML template of the usage chart page.
    """
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
    fig.add_trace(go.Scatter(x=times, y=values, mode='lines', marker=dict(color='green'), name='Watt Hour'), row=1, col=1, secondary_y=False)
    fig.add_trace(go.Scatter(x=times, y=prices, mode='lines', marker=dict(color='orange'), name='Price'), row=1, col=1, secondary_y=True)
    fig.update_yaxes(title_text='Watt Hour', secondary_y=False)
    fig.update_yaxes(title_text='Price', secondary_y=True)
    fig.update_layout(title='Pulse Data Line Plot', xaxis_title='Time')


    last_7_days = pd.Timestamp.now() - pd.DateOffset(days=7)
    fig.update_xaxes(range=[last_7_days, pd.Timestamp.now()])
    chart = fig.to_html(full_html=False)

    return render_template('usage/chart.html', chart=chart,
                            usage1daydkk=round(helpers.usage(24)[2],2), usage1daykwh=round(helpers.usage(24)[0],2),
                            usage7daydkk=round(helpers.usage(168)[2],2), usage7daykwh=round(helpers.usage(168)[0],2),
                            usage30daydkk=round(helpers.usage(720)[2],2), usage30daykwh=round(helpers.usage(720)[0],2),
                            usage365daydkk=round(helpers.usage(8760)[2],2), usage365daykwh=round(helpers.usage(8760)[0],2))


@app.route('/toggle', methods=['POST'])
def toggle_button():
    """
    Handles the toggle button request.

    Updates the hot water boost parameter based on the value received from the request.

    Returns:
        dict: A JSON response indicating the success status.
    """
    value = request.json['value']
    helpers.put_request(parameter_id="hot_water_boost", value=value)
    return {'status': 'success'}  # Return a JSON response if needed

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """
    Renders the settings page.

    Saves the schedule to a CSV file if the request method is POST.

    Returns:
        str: The rendered HTML template of the settings page or a success message.
    """
    if request.method == 'POST':
        schedule = request.get_json()['schedule']
        df = pd.DataFrame({'Hour': range(24), 'Value': schedule})
        df['Value'] = df['Value'].apply(lambda x: min(x, 10))
        save_path = '/root/NIBE/'
        file_path = os.path.join(save_path, 'schedule.csv')
        df.to_csv(file_path, index=False)
        helpers.updatesche()
        return 'Schedule saved to CSV'
    else:
        return render_template('settings/settings.html')


@app.route('/reset', methods=['GET', 'POST'])
def reset():
    """
    Handles the reset request.

    Pushes the data and returns the settings page.

    Returns:
        str: The rendered HTML template of the settings page.
    """
    push()
    return render_template('settings/settings.html')




if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=80)
    #app.run(host='0.0.0.0', port=5000, debug=True)