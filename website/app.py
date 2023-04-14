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
    if request.method == 'POST' and 'submit' in request.form:
        temp = request.form['temp']
        helpers.put_request(temp)
        return render_template('index.html', varme_temperatur=temp, udendors_temperatur=helpers.get_request(40004))
    else:
        return render_template('index.html', udendors_temperatur=helpers.get_request(40004))

@app.route('/chart')
def chart():
    # Connect to MySQL database
    conn = pymysql.connect(host=db_host, user=db_username, passwd=db_password, db=db_name)
    cursor = conn.cursor()

    # Fetch data from database
    cursor.execute("SELECT time, value FROM pulse_data")
    data = cursor.fetchall()

    # Close database connection
    cursor.close()
    conn.close()

    # Extract time and value from fetched data
    times = [row[0] for row in data]
    values = [row[1] for row in data]

    # Create a subplot with a line plot
    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(go.Scatter(x=times, y=values, mode='lines', marker=dict(color='green'), name='Value'),
                  row=1, col=1)
    fig.update_layout(title='Pulse Data Line Plot', xaxis_title='Time', yaxis_title='Watts')

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
    app.run(host='0.0.0.0', port=3000, debug=True)
   #app.run(debug=True)
