import streamlit as st
import pandas as pd
import os
import re
import json
from .utils import clean_col_name, get_grade_level

def normalize_column_name(col):
    """Normalize 2024 mangled columns to 2025 standard names with robust string matching"""
    original = str(col)
    c = clean_col_name(col)
    
    # 1. Subject Scores
    if ('jl' in c and 'procent' in c) or ('jl' in c and 'lep' in c):
        return 'c_procentni_skor'
    if ('ma' in c and 'procent' in c) or ('ma' in c and 'lep' in c):
        return 'm_procentni_skor'
    
    # 2. Priority Columns (ss1..ss5)
    match = re.search(r's(\d)', c) or re.search(r's(\d)', c) # Handle cases where regex might fail due to mangling
    # Fallback to simple indices if digit is near 's'
    if not match:
        for i in range(1, 6):
            if f's{i}' in c or f's{i}' in c: 
                idx = str(i)
                break
        else: idx = None
    else: idx = match.group(1)

    if idx:
        new_prefix = f'ss{idx}_'
        if 'izo' in c or 'redizo' in c: return f'{new_prefix}redizo'
        if 'kkov' in c or 'obor' in c or 'kd' in c: return f'{new_prefix}kkov'
        if 'prijat' in c or 'pijat' in c: return f'{new_prefix}prijat'
        if 'duvod' in c: return f'{new_prefix}duvod_neprijeti'
    
    if 'kolo' in c: return 'kolo'
    if 'rok' in c: return 'rok'
    
    return original

@st.cache_data
def load_school_map():
    """Loads the school mapping (both RED_IZO and IZO -> Names)"""
    try:
        df = pd.read_csv('skoly.csv', encoding='cp1250', sep=';', low_memory=False)
    except:
        df = pd.read_csv('skoly.csv', encoding='utf-8', sep=';', low_memory=False)
    
    mapping = {}
    df['is_school'] = df['Nazev'].fillna('').astype(str).str.contains('škola|Gymnázium|Lyceum', case=False)
    # Sort: put actual schools at the top so we pick their name first
    df = df.sort_values(by=['is_school'], ascending=False)

    for _, row in df.iterrows():
        try:
            riz = int(float(row['RED_IZO']))
            iz = int(float(row['IZO']))
            
            short_name = str(row['Zkraceny_nazev']).strip()
            name_vessel = str(row['Nazev']).strip()
            full_name = str(row['Plny_nazev']).strip()
            
            final_name = full_name
            if not final_name or final_name.lower() == 'nan':
                 final_name = name_vessel

            misto = str(row['Misto']).strip() if 'Misto' in row and pd.notna(row['Misto']) else ""
            if misto and misto.lower() not in final_name.lower():
                final_name = f"{final_name} ({misto})"
            
            # Add to map using both RED_IZO and IZO keys
            if riz not in mapping: mapping[riz] = final_name
            if iz not in mapping: mapping[iz] = final_name
        except:
            continue
    return mapping

@st.cache_data
def load_izo_to_redizo_map():
    """Builds IZO (facility) → REDIZO (institution) mapping from skoly.csv.
    Student data uses facility IZOs in the ss_redizo columns, while capacity
    files use institution-level REDIZOs. This mapping translates between them."""
    try:
        df = pd.read_csv('skoly.csv', encoding='cp1250', sep=';', low_memory=False)
    except:
        df = pd.read_csv('skoly.csv', encoding='utf-8', sep=';', low_memory=False)
    
    izo_to_redizo = {}
    for _, row in df.iterrows():
        try:
            riz = str(int(float(row['RED_IZO'])))
            iz = str(int(float(row['IZO'])))
            if iz not in izo_to_redizo:
                izo_to_redizo[iz] = riz
            # Also map REDIZO to itself for schools where the data already uses REDIZO
            if riz not in izo_to_redizo:
                izo_to_redizo[riz] = riz
        except:
            continue
    return izo_to_redizo

@st.cache_data
def load_kkov_map():
    """Loads KKOV code to Name mapping from JSON"""
    if os.path.exists('kkov_map.json'):
        with open('kkov_map.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

@st.cache_data
def load_year_data(year):
    """Loads and normalizes data for a specific year"""
    files = [f for f in os.listdir('.') if f.startswith(f'PZ{year}') and f.endswith('.xlsx')]
    if not files: return pd.DataFrame()
        
    dfs = []
    for f in files:
        try:
            df = pd.read_excel(f)
            # Normalize column names
            df.columns = [normalize_column_name(c) for c in df.columns]
            
            # Deduplicate columns
            unique_cols = []
            seen = set()
            for c in df.columns:
                if c not in seen:
                    unique_cols.append(c)
                    seen.add(c)
                else:
                    unique_cols.append(f"{c}_dup_{len(seen)}")
            df.columns = unique_cols

            # Numeric conversion
            num_cols = [c for c in df.columns if 'redizo' in c or c == 'kolo' or 'procentni_skor' in c]
            for col in num_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Normalize 'Prijat' columns - in 2024 they might be bool, in 2025 numeric
            prijat_cols = [c for c in df.columns if 'prijat' in c]
            for col in prijat_cols:
                if df[col].dtype == bool:
                    df[col] = df[col].astype(int)
                else:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
            
            dfs.append(df)
        except Exception as e:
            st.error(f"Chyba při načítání {f}: {e}")
            
    if not dfs: return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True)

@st.cache_data
def load_capacity_data(year, round_num=1):
    """Loads official capacity data for a given year and round from Cermat XLSX"""
    filename = f'PZ{year}_kolo{round_num}_skolobory_kapacity.xlsx'
    if not os.path.exists(filename):
        return pd.DataFrame()
    
    try:
        df = pd.read_excel(filename)
        # Based on inspection: ['REDIZO', 'KKOV', 'KAPACITA'] are key
        # Using column indices or normalized names might be safer, but REDIZO/KKOV/KAPACITA seem stable
        cols_to_use = [c for c in df.columns if c in ['REDIZO', 'KKOV', 'KAPACITA']]
        df = df[cols_to_use].copy()
        
        # Try to find REDIZO or IZO
        id_cols = [c for c in df.columns if c in ['REDIZO', 'IZO', 'RED_IZO']]
        for col in id_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int).astype(str)
            
        if 'KKOV' in df.columns:
            df['KKOV'] = df['KKOV'].astype(str).str.strip()
            
        return df
    except Exception as e:
        print(f"Chyba při načítání kapacit {year} kolo {round_num}: {e}")
        return pd.DataFrame()

@st.cache_data
def get_long_format(df_in, _school_map, _kkov_map):
    if df_in.empty: return pd.DataFrame()
    
    # 1. Prepare wide data with unique Student ID
    df_wide = df_in.copy()
    df_wide['Student_UUID'] = range(len(df_wide))
    
    # Cast RED_IZO columns to normalized strings for mapping
    # Note: _school_map is passed as a dict where keys are ints (RED_IZO/IZO)
    str_school_map = {str(k): v for k, v in _school_map.items()}
    riz_cols = [f'ss{j}_redizo' for j in range(1, 6) if f'ss{j}_redizo' in df_wide.columns]
    for col in riz_cols:
        df_wide[col] = pd.to_numeric(df_wide[col], errors='coerce').fillna(0).astype(int).astype(str)

    normalized_data = []
    cjl_col = 'c_procentni_skor' if 'c_procentni_skor' in df_wide.columns else None
    mat_col = 'm_procentni_skor' if 'm_procentni_skor' in df_wide.columns else None
    
    for i in range(1, 6):
        r_col, k_col, p_col = f'ss{i}_redizo', f'ss{i}_kkov', f'ss{i}_prijat'
        d_col = f'ss{i}_duvod_neprijeti'
        
        if r_col in df_wide.columns and k_col in df_wide.columns:
            subset = df_wide[['Student_UUID', r_col, k_col, p_col, 'kolo']].copy()
            subset.rename(columns={r_col: 'RED_IZO', k_col: 'KKOV', p_col: 'Prijat'}, inplace=True)
            subset['Priority'] = i
            
            # School Name for current row
            subset['SchoolName'] = subset['RED_IZO'].map(str_school_map).fillna("Neznámá škola (" + subset['RED_IZO'] + ")")

            # Clean Reason
            if d_col in df_wide.columns:
                subset['Reason'] = df_wide[d_col].fillna("Neuvedeno").astype(str).str.strip()
            else:
                subset['Reason'] = "Neuvedeno"

            # Point Calcs and Exemption identification
            cjl_raw = df_wide[cjl_col] if cjl_col else pd.Series(None, index=subset.index)
            mat_raw = df_wide[mat_col] if mat_col else pd.Series(None, index=subset.index)
            
            cjl_num = pd.to_numeric(cjl_raw, errors='coerce')
            mat_num = pd.to_numeric(mat_raw, errors='coerce')
            
            subset['IsExempt'] = cjl_num.isna() & mat_num.notna()
            subset['TotalPoints'] = ((cjl_num.fillna(0) * 0.5) + (mat_num.fillna(0) * 0.5)).clip(0, 100)
            
            # Map KKOV to Name
            subset['Grade'] = subset['KKOV'].map(get_grade_level)
            subset['FieldName'] = subset['KKOV'].map(_kkov_map).fillna(subset['KKOV'])
            subset['FieldLabel'] = subset['FieldName'] + " (" + subset['KKOV'] + ")"
            
            # Detect "vzdal se přijetí"
            subset['GaveUpSpot'] = subset['Reason'].str.contains('vzdal', case=False, na=False)
            
            normalized_data.append(subset)
    
    if not normalized_data: return pd.DataFrame()
    res = pd.concat(normalized_data, ignore_index=True)
    
    # 2. POST-PROCESSING: Cross-reference across all priorities for EACH student
    admitted_rows = res[res['Prijat'] == 1].copy()
    admitted_rows['CombinedLabel'] = admitted_rows['SchoolName'] + " (" + admitted_rows['FieldLabel'] + ")"
    
    success_map_school = admitted_rows.set_index('Student_UUID')['SchoolName'].to_dict()
    success_map_detail = admitted_rows.set_index('Student_UUID')['CombinedLabel'].to_dict()
    
    res['AcceptedSchoolName'] = res['Student_UUID'].map(success_map_school).fillna("Nepřijat / neznámá")
    res['AcceptedDetail'] = res['Student_UUID'].map(success_map_detail).fillna("Nepřijat / neznámá")
    
    return res
