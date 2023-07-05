import csv
import pandas as pd

try:
    schedule_file_path = 'schedule.csv'
    data_file_path = 'data.csv'
    column_name = 'TurnOn'
    values_to_replace = []

    with open(schedule_file_path, 'r') as schedule_file:
        reader = csv.DictReader(schedule_file)
        for index, row in enumerate(reader):
            value = int(row['Value'])
            if value != 0:
                values_to_replace.append((index, value))

    if not values_to_replace:
        raise ValueError("No values to replace")

    df = pd.read_csv(data_file_path)
    for index, value in values_to_replace:
        df.loc[index, column_name] = value
    df.to_csv(data_file_path, index=False)

except (FileNotFoundError, ValueError) as e:
    print(f"An error occurred: {e}")
