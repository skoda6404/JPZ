import pandas as pd
import os
from src.data_loader import load_year_data, load_school_map, load_kkov_map, get_long_format, load_capacity_data, load_izo_to_redizo_map
from src.analysis import calculate_kpis

def run_sanity_check(year):
    print(f"\n--- SANITY CHECK FOR {year} ---")
    school_map = load_school_map()
    izo_to_redizo = load_izo_to_redizo_map()
    raw_df = load_year_data(year)
    capacity_dfs = {r: load_capacity_data(year, r) for r in [1, 2]}
    kkov_map = load_kkov_map()
    
    long_df_all = get_long_format(raw_df, school_map, kkov_map)
    
    anomalies = []
    
    for school_name, school_data in long_df_all.groupby('SchoolName'):
        # Total Capacity
        total_planned = 0
        riz_detail = str(school_data['RED_IZO'].iloc[0])
        redizo_key = izo_to_redizo.get(riz_detail, riz_detail)
        
        for kkov in school_data['KKOV'].unique():
            kkov_s = str(kkov)
            match = capacity_dfs[1][(capacity_dfs[1]['REDIZO'] == redizo_key) & (capacity_dfs[1]['KKOV'] == kkov_s)]
            if not match.empty:
                total_planned += int(match['KAPACITA'].sum())
        
        if total_planned == 0: continue # Skip if no capacity data
        
        kpis = calculate_kpis(school_data, planned_capacity=total_planned)
        
        # Check 1: Vacant seats vs Capacity and Admitted
        # vacant = capacity - (admitted - gave_up_if_was_admitted)
        # If my logic is correct, it should align.
        
        # Check 2: Fullness > 100% (Over-admission)
        if kpis['fullness_rate'] > 110: # Allow some buffer for rounding or small over-admission
             anomalies.append(f"[Fullness] {school_name}: {kpis['fullness_rate']:.1f}% ({kpis['total_admitted']} adm / {kpis['planned_capacity']} cap)")
             
        # Check 3: Negative vacant seats
        if kpis['vacant_seats'] < 0:
             anomalies.append(f"[Negative Vacant] {school_name}: {kpis['vacant_seats']}")

    if not anomalies:
        print("No obvious anomalies found.")
    else:
        print(f"Found {len(anomalies)} anomalies:")
        for a in anomalies[:20]:
            print(f"  {a}")

if __name__ == "__main__":
    run_sanity_check("2024")
    run_sanity_check("2025")
