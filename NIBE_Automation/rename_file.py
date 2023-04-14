import pandas as pd

import os

def rename_csv_file(old_file_path, new_file_path):
    try:
        os.rename(old_file_path, new_file_path)
        print(f"CSV file renamed from '{old_file_path}' to '{new_file_path}' successfully!")
    except OSError as e:
        print(f"Failed to rename CSV file: {e}")

old_file_path = "combineddata.csv"
new_file_path = "data.csv"
rename_csv_file(old_file_path, new_file_path)
