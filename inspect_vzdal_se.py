import pandas as pd
import os

def inspect_vzdal_se():
    files = [f for f in os.listdir('.') if 'uchazeci' in f and f.endswith('.xlsx')]
    for f in files:
        print(f"\n--- Inspecting {f} ---")
        try:
            df = pd.read_excel(f)
            # Find any column that contains 'duvod' or 'neprijet'
            reason_cols = [c for c in df.columns if 'duvod' in str(c).lower() or 'neprijet' in str(c).lower()]
            # Find any column that contains 'prijat'
            prijat_cols = [c for c in df.columns if 'prijat' in str(c).lower()]
            
            if not reason_cols or not prijat_cols:
                print("Could not find reason or prijat columns")
                continue
                
            # Filter rows where ANY reason col contains 'vzdal'
            mask = pd.Series(False, index=df.index)
            for col in reason_cols:
                mask |= df[col].astype(str).str.contains('vzdal', case=False, na=False)
            
            vzdal_se_df = df[mask]
            if vzdal_se_df.empty:
                print("No 'vzdal se' cases found")
                continue
                
            print(f"Found {len(vzdal_se_df)} 'vzdal se' cases")
            # For each 'vzdal se', check correlating 'prijat' column
            for col in prijat_cols:
                # Use regex to find which 'prijat' corresponds to which 'vzdal'
                print(f"  Distribution in {col}:")
                print(vzdal_se_df[col].value_counts(dropna=False))
                
        except Exception as e:
            print(f"Error reading {f}: {e}")

if __name__ == "__main__":
    inspect_vzdal_se()
