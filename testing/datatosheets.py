import csv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

creds_path = 'exalted-iridium-384920-14a0f16a5466.json'

doc_id = '1ArcpUMjb5Tu5EK5GQlwZehQ2oUJnGYjcET4OzTKqhGM'

worksheet_name = 'Data'

csv_path = 'usage.csv'

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
client = gspread.authorize(creds)

doc = client.open_by_key(doc_id)
worksheet = doc.worksheet(worksheet_name)

with open(csv_path, 'r') as f:
    reader = csv.reader(f)
    data = list(reader)
    worksheet.append_rows(data)
    print('Data inserted successfully.')
