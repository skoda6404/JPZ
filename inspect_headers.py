
import pandas as pd
import os

files = ['PZ2024_kolo1_uchazeci_prihlasky_vysledky.xlsx', 'PZ2025_kolo1_uchazeci_prihlasky_vysledky.xlsx']

for f in files:
    if os.path.exists(f):
        print(f"--- {f} ---")
        try:
            df = pd.read_excel(f, nrows=0) # Read only headers
            for col in df.columns:
                print(col)
        except Exception as e:
            print(f"Error reading {f}: {e}")
    else:
        print(f"File not found: {f}")
