import pandas as pd
import os

# Simplified logic to find reasons
target_dir = r"d:\OneDrive - Jiráskovo gymnázium, Náchod, Řezníčkova 451\Dokumenty\Antigravity_Prijimacky_analyza 3"
files = [f for f in os.listdir(target_dir) if f.endswith('.xlsx')]
for f in files:
    try:
        fpath = os.path.join(target_dir, f)
        df = pd.read_excel(fpath)
        duvod_cols = [c for c in df.columns if 'duvod' in c.lower()]
        
        print(f"\nFile: {f}")
        for col in duvod_cols:
            print(f"  Col {col} unique values: {df[col].dropna().unique().tolist()}")
    except Exception as e:
        print(f"Error {f}: {e}")
