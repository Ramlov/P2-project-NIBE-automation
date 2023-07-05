import csv
import pandas as pd

def replace_nonzero_values(schedule_file_path, data_file_path, column_name):
    values_to_replace = []

    with open(schedule_file_path, 'r') as schedule_file:
        reader = csv.DictReader(schedule_file)
        for index, row in enumerate(reader):
            value = int(row['Value'])
            if value != 0:
                values_to_replace.append((index, value))

    if not values_to_replace:
        return

    df = pd.read_csv(data_file_path)
    for index, value in values_to_replace:
        df.loc[index, column_name] = value
    df.to_csv(data_file_path, index=False)

schedule_file_path = '../NIBE-Auto/schedule.csv'
data_file_path = '../NIBE-Auto/data.csv'
column_name = 'TurnOn'

replace_nonzero_values(schedule_file_path, data_file_path, column_name)
