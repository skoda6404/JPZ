import pandas as pd
import os

def debug_capacity():
    filename = 'PZ2024_kolo1_skolobory_kapacity.xlsx'
    df = pd.read_excel(filename)
    df['REDIZO_STR'] = pd.to_numeric(df['REDIZO'], errors='coerce').fillna(0).astype(int).astype(str)
    df['KKOV_STR'] = df['KKOV'].astype(str).str.strip()
    
    it_gym = df[df['REDIZO_STR'] == '691013489']
    print("--- IT GYMNASIUM CAPACITY DATA ---")
    print(it_gym[['REDIZO', 'KKOV', 'KAPACITA', 'REDIZO_STR', 'KKOV_STR']])
    
    # Check for hidden characters in KKOV
    if not it_gym.empty:
        for idx, row in it_gym.iterrows():
            kkov = row['KKOV_STR']
            print(f"\nKKOV: '{kkov}' (len={len(kkov)})")
            print(f"Bytes: {kkov.encode('utf-8')}")

if __name__ == "__main__":
    debug_capacity()
