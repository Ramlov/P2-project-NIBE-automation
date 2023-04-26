import pandas as pd
import plotly.express as px

data = pd.read_csv('your_data_file.csv')

fig = px.scatter(data, x='x_column_name', y='y_column_name', title='Your Title Here')

fig.show()
