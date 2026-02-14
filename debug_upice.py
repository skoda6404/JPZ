import pandas as pd
import os
from src.data_loader import load_year_data, load_school_map, load_kkov_map, get_long_format, load_capacity_data, load_izo_to_redizo_map
from src.analysis import calculate_kpis

def debug_upice():
    year = "2024"
    school_keyword = "Úpice"
    
    print(f"--- Debugging Úpice ({year}) ---")
    
    # Load data
    school_map = load_school_map()
    izo_to_redizo = load_izo_to_redizo_map()
    raw_df = load_year_data(year)
    capacity_dfs = {r: load_capacity_data(year, r) for r in [1, 2]}
    kkov_map = load_kkov_map()
    
    if raw_df.empty:
        print("Raw data empty")
        return

    long_df_all = get_long_format(raw_df, school_map, kkov_map)
    # Find all schools in Upice to be sure
    school_data = long_df_all[long_df_all['SchoolName'].str.contains(school_keyword, na=False)]
    
    # Check for multi-admitted students in raw_df
    prijat_cols = [c for c in raw_df.columns if 'prijat' in c]
    total_assigned_per_student = raw_df[prijat_cols].sum(axis=1)
    multi_assigned = raw_df[total_assigned_per_student > 1]
    if not multi_assigned.empty:
        print(f"\n[WARNING] Found {len(multi_assigned)} students with multiple Prijat=1 in raw data!")
        # Check if any of these are in Upice data
        upice_uuids = school_data['Student_UUID'].unique()
        multi_upice = multi_assigned[multi_assigned.index.isin(upice_uuids)]
        if not multi_upice.empty:
            print(f"  -> {len(multi_upice)} of these students are associated with Upice!")
            print(multi_upice[prijat_cols].to_string())
        else:
            print("  -> None of these multi-assigned students are associated with Upice.")
    
    if school_data.empty:
        print(f"School matching '{school_keyword}' not found in long format data")
        # List first 5 schools for debugging
        print("Available schools (sample):", long_df_all['SchoolName'].unique()[:5])
        return

    school_name = school_data['SchoolName'].iloc[0]
    print(f"Found school: {school_name}")
    red_izo = school_data['RED_IZO'].iloc[0]
    print(f"RED_IZO (normalized): {red_izo}")
    
    if school_data.empty:
        print("School data empty after long format transformation")
        return

    # Calculate capacity
    total_planned = 0
    riz_detail = str(school_data['RED_IZO'].iloc[0])
    for kkov in school_data['KKOV'].unique():
        kkov_s = str(kkov)
        # Assuming R1 for capacity check as per app.py logic
        match = capacity_dfs[1][(capacity_dfs[1]['REDIZO'] == izo_to_redizo.get(riz_detail, riz_detail)) & (capacity_dfs[1]['KKOV'] == kkov_s)]
        if not match.empty:
            cap = int(match['KAPACITA'].sum())
            print(f"  Field {kkov_s} capacity: {cap}")
            total_planned += cap
            
    print(f"Total planned capacity: {total_planned}")
    
    print("\n--- Capacity DataFrame Matching Rows ---")
    match_all = capacity_dfs[1][capacity_dfs[1]['REDIZO'] == izo_to_redizo.get(riz_detail, riz_detail)]
    print(match_all.to_string())
    
    # Analyze admitted and gave up
    admitted = school_data[school_data['Prijat'] == 1]
    print(f"\nUnique Reasons for admitted students: {admitted['Reason'].value_counts().to_dict()}")
    
    gave_up = school_data[school_data['Reason'].str.contains('vzdal', case=False, na=False)]
    gave_up_admitted = admitted[admitted['Reason'].str.contains('vzdal', case=False, na=False)]
    
    print("\n--- Admitted counts per field ---")
    for kkov in school_data['KKOV'].unique():
        kkov_s = str(kkov)
        adm_count = len(admitted[admitted['KKOV'] == kkov_s])
        # Assuming R1 for capacity check as per app.py logic
        match = capacity_dfs[1][(capacity_dfs[1]['REDIZO'] == izo_to_redizo.get(riz_detail, riz_detail)) & (capacity_dfs[1]['KKOV'] == kkov_s)]
        cap = int(match['KAPACITA'].sum()) if not match.empty else 0
        print(f"  Field {kkov_s}: Admitted={adm_count}, Capacity={cap}, Vacant={cap-adm_count}")
    
    kkov_81 = '79-41-K/81'
    adm_81 = admitted[admitted['KKOV'] == kkov_81]
    gv_81 = gave_up[gave_up['KKOV'] == kkov_81]
    
    print(f"\n--- Scores in {kkov_81} ---")
    print(f"Admitted (Count: {len(adm_81)}):")
    print(adm_81.sort_values('TotalPoints', ascending=False)[['TotalPoints', 'Priority', 'Reason']].to_string())
    print(f"\n'Vzdal se' (Count: {len(gv_81)}):")
    print(gv_81.sort_values('TotalPoints', ascending=False)[['TotalPoints', 'Priority', 'Reason']].to_string())
    
    actual_occupied = len(admitted) - len(gave_up_admitted)
    vacant_seats = total_planned - actual_occupied
    
    print(f"Total admitted (Prijat=1): {len(admitted)}")
    print(f"Total 'vzdal se' in all applicants: {len(gave_up)}")
    print(f"Total 'vzdal se' among admitted: {len(gave_up_admitted)}")
    
    neuvedeno_not_prijat = school_data[(school_data['Reason'] == 'Neuvedeno') & (school_data['Prijat'] != 1)]
    print(f"\n--- Applicants with Reason: Neuvedeno but Prijat != 1 (Count: {len(neuvedeno_not_prijat)}) ---")
    if not neuvedeno_not_prijat.empty:
        print(neuvedeno_not_prijat[['RED_IZO', 'KKOV', 'Prijat', 'Reason', 'Priority']].to_string())
    
    prijat_nan = school_data[school_data['Prijat'].isna()]
    print(f"\n--- Applicants with Prijat: NaN (Count: {len(prijat_nan)}) ---")
    if not prijat_nan.empty:
        print(prijat_nan[['RED_IZO', 'KKOV', 'Prijat', 'Reason', 'Priority']].to_string())
    
    print("\n--- Admitted Applicants Details ---")
    print(admitted[['RED_IZO', 'KKOV', 'Prijat', 'Reason', 'Priority']].to_string())
    
    print("\n--- All Applicants in 68-43-M/01 ---")
    kkov_ms = '68-43-M/01'
    ms_apps = school_data[school_data['KKOV'] == kkov_ms]
    print(ms_apps.sort_values(['Prijat', 'TotalPoints'], ascending=False)[['Student_UUID', 'TotalPoints', 'Prijat', 'Reason', 'Priority']].to_string())
    
    # KPIs calculation
    kpis = calculate_kpis(school_data, planned_capacity=total_planned)
    print("\n--- KPI Results ---")
    for key in ['total_apps', 'total_admitted', 'gave_up_count', 'planned_capacity', 'fullness_rate', 'vacant_seats']:
        print(f"{key}: {kpis.get(key)}")

if __name__ == "__main__":
    debug_upice()
