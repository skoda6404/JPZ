import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys
import re
import json
import io
from fpdf import FPDF

# --- CONFIG ---
# --- CONFIG ---
st.set_page_config(page_title="JPZ", layout="wide")

def create_pdf_report(school_name, year, rounds, pivot_df, kpi_data):
    pdf = FPDF()
    pdf.add_page()
    # fpdf2 supports some unicode if we use built-in core fonts, but for Czech TTF is best.
    # We will use "helvetica" and replace special chars if they break, 
    # but fpdf2 has better internal support than old fpdf.
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, f"Detailni report: {school_name}", ln=True, align="C")
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 10, f"Rok: {year} | Kola: {', '.join(map(str, rounds))}", ln=True, align="C")
    pdf.ln(10)
    
    # KPIs
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "Klicove metriky skoly:", ln=True)
    pdf.set_font("helvetica", "", 11)
    pdf.cell(60, 8, f"Prihlasek: {kpi_data['total_apps']}")
    pdf.cell(60, 8, f"Uspesnost: {kpi_data['success_rate']:.1f}%")
    pdf.cell(60, 8, f"Pretlak: {kpi_data['comp_idx']:.2f}x")
    pdf.ln(15)
    
    # Table Header
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("helvetica", "B", 9)
    # Simple labels for PDF to avoid encoding issues with complex headers
    cols = ["Obor", "Prihl.", "Prijat", "Min. body", "Elita (10%)"]
    w = [90, 20, 25, 25, 30]
    for i, col in enumerate(cols):
        pdf.cell(w[i], 10, col, 1, 0, "C", True)
    pdf.ln()
    
    # Table Data
    pdf.set_font("helvetica", "", 8)
    # In the pivot, 'PŘIJAT' might be missing if no one was admitted.
    # We look for rows where we have stats.
    # The pivot passed here is the one formatted for display.
    for _, row in pivot_df.iterrows():
        # Truncate field name if too long
        field = str(row['Obor'])[:55]
        pdf.cell(w[0], 8, field, 1)
        pdf.cell(w[1], 8, str(row['Celkem přihlášek']), 1, 0, "C")
        
        adm_val = str(row.get('PŘIJAT', '-'))
        pdf.cell(w[2], 8, adm_val, 1, 0, "C")
        
        min_b = str(row.get('Poslední přijatý (body)', '-'))
        pdf.cell(w[3], 8, min_b, 1, 0, "C")
        
        elite = str(row.get('Elitní průměr (10%)', '-'))
        pdf.cell(w[4], 8, elite, 1, 0, "C")
        pdf.ln()
    
    return pdf.output()


# Custom CSS for a professional, "Excel-inspired" compact look
st.markdown("""
    <style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 0.5rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }
    .stPlotlyChart {
        height: 700px !important;
    }
    div[data-testid="stMetric"] {
        background-color: #f8f9fa;
        padding: 5px 15px;
        border-radius: 4px;
        border: 1px solid #dee2e6;
    }
    section[data-testid="stSidebar"] > div {
        padding-top: 1.5rem;
    }
    .stTable {
        font-size: 0.85rem;
    }
    /* Compact headers */
    h1 { margin-bottom: 0.5rem !important; font-size: 1.8rem !important; }
    h3 { margin-top: 1rem !important; margin-bottom: 0.5rem !important; font-size: 1.2rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- DATA NORMALIZATION HELPERS ---
def clean_col_name(col):
    """Strip non-ascii characters and normalize case"""
    s = "".join([c if ord(c) < 128 else "" for c in str(col)])
    return s.strip().lower()

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
        df = pd.read_csv('skoly.csv', encoding='cp1250', sep=';')
    except:
        df = pd.read_csv('skoly.csv', encoding='utf-8', sep=';')
    
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
                # Map True/False to 1/0, or keep 1/2 from 2025
                # We normalize so that 1 ALWAYS means accepted.
                # In 2025 Excel, 1 was accepted. In 2024 bool, True is accepted.
                if df[col].dtype == bool:
                    df[col] = df[col].astype(int)
                else:
                    # If it's 1/2 or something Else, we assume 1 is success.
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
            
            dfs.append(df)
        except Exception as e:
            st.error(f"Chyba při načítání {f}: {e}")
            
    if not dfs: return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True)

# --- SESSION STATE INITIALIZATION ---
if 'selected_year' not in st.session_state:
    available_years = sorted([f[2:6] for f in os.listdir('.') if f.startswith('PZ') and f.endswith('.xlsx')], reverse=True)
    st.session_state.selected_year = available_years[0] if available_years else "2025"

# --- SIDEBAR: CORE FILTERS ---
st.sidebar.markdown("### 📊 Nastavení analýzy")

available_years = sorted(list(set([f[2:6] for f in os.listdir('.') if f.startswith('PZ') and f.endswith('.xlsx')])), reverse=True)
if not available_years:
    st.error("Nenalezena žádná data.")
    st.stop()

y_idx = available_years.index(st.session_state.selected_year) if st.session_state.selected_year in available_years else 0
# Use radio button for quick 1-click selection
selected_year = st.sidebar.radio("Rok konání", available_years, index=y_idx, key='year_select', horizontal=True)
st.session_state.selected_year = selected_year

school_map = load_school_map()
raw_df = load_year_data(selected_year)

if raw_df.empty:
    st.warning(f"Data pro rok {selected_year} nejsou k dispozici.")
    st.stop()

available_rounds = sorted(raw_df['kolo'].dropna().unique().astype(int).tolist())
st.sidebar.markdown("### Kolo zkoušky")
selected_rounds = []
# Fixed 2-column layout for checkboxes is cleaner
c1, c2 = st.sidebar.columns(2)
cols = [c1, c2]

for i, r in enumerate(available_rounds):
    # Use index to distribute between columns
    col = cols[i % 2]
    # Checkbox with persistent state (key ensures persistence)
    # Explicitly ensure 'r' is treated as integer for the label
    label = f"{int(r)}\\. kolo"
    if col.checkbox(label, value=True, key=f"round_chk_{selected_year}_{r}"):
        selected_rounds.append(r)

st.session_state.selected_rounds = selected_rounds

filtered_df = raw_df[raw_df['kolo'].isin(selected_rounds)] if selected_rounds else raw_df.iloc[0:0]

# --- DATA TRANSFORMATION ---
@st.cache_data
@st.cache_data
def get_long_format(df_in, _school_map, _kkov_map):
    if df_in.empty: return pd.DataFrame()
    normalized_data = []
    
    cjl_col = 'c_procentni_skor' if 'c_procentni_skor' in df_in.columns else None
    mat_col = 'm_procentni_skor' if 'm_procentni_skor' in df_in.columns else None
    
    for i in range(1, 6):
        r_col, k_col, p_col = f'ss{i}_redizo', f'ss{i}_kkov', f'ss{i}_prijat'
        d_col = f'ss{i}_duvod_neprijeti'
        
        if r_col in df_in.columns and k_col in df_in.columns:
            subset = df_in[[r_col, k_col, p_col, 'kolo']].copy()
            subset.rename(columns={r_col: 'RED_IZO', k_col: 'KKOV', p_col: 'Prijat'}, inplace=True)
            subset['Priority'] = i
            
            # Extract Reason
            if d_col in df_in.columns:
                subset['Reason'] = df_in[d_col].fillna("Neuvedeno")
            else:
                subset['Reason'] = "Neuvedeno"

            # Identify Exemptions from CJL
            # In source data, exemption might be NaN or text. 'load_year_data' coerces to NaN.
            # So if cjl is NaN but mat is valid (not NaN), we assume exemption.
            # We strictly check if CJL is NaN before filling it.
            
            # Fix: Read scores from df_in and ensure correct index alignment
            cjl_raw = df_in[cjl_col] if cjl_col else pd.Series(None, index=subset.index)
            mat_raw = df_in[mat_col] if mat_col else pd.Series(None, index=subset.index)
            
            # Coerce to numeric first to turn strings to NaN, but keep NaNs as is for check
            cjl_num = pd.to_numeric(cjl_raw, errors='coerce')
            mat_num = pd.to_numeric(mat_raw, errors='coerce')
            
            # Logic: If CJL is NaN but MAT is Valid (>=0), then Exempt.
            # Note: A student absent from both would be NaN in both (or 0 if normalization logic filled it earlier).
            # But here we are operating on columns from 'df_in' which were already coerced in 'load_year_data'.
            # Wait, 'load_year_data' already did pd.to_numeric(..., errors='coerce').
            # So if it was "Omluven", it is NaN. If it was 0, it is 0.
            
            subset['CJL_pct'] = cjl_num
            subset['MAT_pct'] = mat_num
            
            subset['IsExempt'] =  subset['CJL_pct'].isna() & subset['MAT_pct'].notna()
            
            # Fill NaNs for point calc
            subset['CJL_pct'] = subset['CJL_pct'].fillna(0)
            subset['MAT_pct'] = subset['MAT_pct'].fillna(0)
            
            subset['TotalPoints'] = (subset['CJL_pct'] * 0.5) + (subset['MAT_pct'] * 0.5)
            
            normalized_data.append(subset)
    
    if not normalized_data: return pd.DataFrame()
    res = pd.concat(normalized_data, ignore_index=True)
    res['SchoolName'] = res['RED_IZO'].map(_school_map).fillna("Neznámá škola (" + res['RED_IZO'].astype(str).str.replace('.0','') + ")")
    # Map KKOV to Name
    res['FieldName'] = res['KKOV'].map(_kkov_map).fillna(res['KKOV'])
    # Combine for display if needed, but keeping separate is better for filtering
    res['FieldLabel'] = res['FieldName'] + " (" + res['KKOV'] + ")"
    
    # Clean Reason
    res['Reason'] = res['Reason'].astype(str).str.strip()
    return res

kkov_map = load_kkov_map()
long_df = get_long_format(filtered_df, school_map, kkov_map)

# --- SIDEBAR: SELECTION FILTERS ---
# --- SIDEBAR: VIEW MODE ---
st.sidebar.markdown("---")
view_mode = st.sidebar.radio("Zobrazení", ["Srovnání škol", "Detailní rozbor školy"], key='view_mode_select')

# --- SIDEBAR: SELECTION FILTERS ---
st.sidebar.markdown("---")

if not long_df.empty:
    if view_mode == "Srovnání škol":
        # 1. School Filter (Multiple)
        available_schools = sorted(long_df['SchoolName'].unique().tolist())
        if 'selected_schools' not in st.session_state: st.session_state.selected_schools = []
        st.session_state.selected_schools = [s for s in st.session_state.selected_schools if s in available_schools]
        
        selected_schools = st.sidebar.multiselect("Výběr škol", options=available_schools, key='schools_select_v2', placeholder="Vyberte...")
        st.session_state.selected_schools = selected_schools
        
        if selected_schools:
            school_sub = long_df[long_df['SchoolName'].isin(selected_schools)]
            available_fields = sorted(school_sub['FieldLabel'].unique().tolist())
            selected_fields = st.sidebar.multiselect("Výběr oborů", options=available_fields, key='fields_select_v2', placeholder="Vyberte...")
        else:
            selected_fields = []
    else:
        # Detail Mode: Select single school
        available_schools = sorted(long_df['SchoolName'].unique().tolist())
        selected_school = st.sidebar.selectbox("Vyberte školu pro detail", options=available_schools, key='single_school_select')
        selected_schools = [selected_school] if selected_school else []
        
        # In detail mode, we usually show all fields for that school
        if selected_school:
            school_sub = long_df[long_df['SchoolName'] == selected_school]
            available_fields = sorted(school_sub['FieldLabel'].unique().tolist())
            selected_fields = available_fields # Show all fields in detail by default
        else:
            selected_fields = []
else:
    st.sidebar.warning("Žádná data pro vybrané parametry.")
    selected_schools, selected_fields = [], []


# --- MAIN PAGE CONTENT ---
if view_mode == "Detailní rozbor školy" and selected_schools:
    school_name = selected_schools[0]
    st.title(f"🏛️ Detail školy: {school_name}")
    
    school_data = long_df[long_df['SchoolName'] == school_name]
    
    # 1. KPI Cards
    total_apps = len(school_data)
    total_admitted = len(school_data[school_data['Prijat'] == 1])
    success_rate = (total_admitted / total_apps * 100) if total_apps > 0 else 0
    competition_index = (total_apps / total_admitted) if total_admitted > 0 else 0
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Celkem přihlášek", total_apps)
    m2.metric("Úspěšnost přijetí", f"{success_rate:.1f}%")
    m3.metric("Index přetlaku", f"{competition_index:.2f}x")
    
    st.markdown("---")
    
    # 2. Charts Row
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.markdown("#### Distribuce priorit (Zájem o obory)")
        prio_counts = []
        for f in sorted(school_data['FieldLabel'].unique()):
            f_data = school_data[school_data['FieldLabel'] == f]
            for p in range(1, 6):
                cnt = len(f_data[f_data['Priority'] == p])
                prio_counts.append({"Obor": f, "Priorita": f"{p}. priorita", "Počet": cnt})
        
        if prio_counts:
            df_prio = pd.DataFrame(prio_counts)
            fig_prio = px.bar(df_prio, x="Obor", y="Počet", color="Priorita", 
                              title="Rozdělení priorit přihlášek",
                              barmode="stack", color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_prio, use_container_width=True)
            
    with c2:
        st.markdown("#### Důvody nepřijetí")
        reason_counts = school_data[school_data['Prijat'] != 1]['Reason'].value_counts().reset_index()
        reason_counts.columns = ['Důvod', 'Počet']
        reason_counts['Důvod'] = reason_counts['Důvod'].map(lambda x: reason_map.get(x, x))
        
        if not reason_counts.empty:
            fig_pie = px.pie(reason_counts, values='Počet', names='Důvod', 
                             hole=0.4, title="Proč nebyli uchazeči přijati?")
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Žádná data o nepřijatých.")

    # 3. Detailed Stats Table
    st.markdown("#### 📋 Podrobné statistiky oborů")
    # (Reuse the same table generation logic but filtered for this school)
    # We already have display_df pre-filtered by selected_schools/selected_fields
    display_df = long_df[(long_df['SchoolName'] == school_name)]
    
    # ... (Rest of the table logic follows) ...
else:
    # --- COMPARISON MODE (Original logic) ---
    st.title(f"📈 JPZ {selected_year}")
    
    if not selected_schools or not selected_fields:
        st.info("Zvolte v bočním panelu školy a obory.")
        st.stop()
    
    display_df = long_df[(long_df['SchoolName'].isin(selected_schools)) & (long_df['FieldLabel'].isin(selected_fields))]

# --- SHARED TABLE & CHART LOGIC (Common for both or adjusted) ---
# Admitted chart is mostly relevant for Comparison mode, but can be shown in Detail too.
admitted_only = display_df[display_df['Prijat'] == 1].copy()

if view_mode == "Srovnání škol":
    st.markdown("### 📊 Výsledky přijímacího řízení")
    if admitted_only.empty:
        st.warning("Žádná data o PŘIJATÝCH uchazečích.")
    else:
        import plotly.graph_objects as go
        fig = go.Figure()
        groups = sorted(admitted_only.groupby(['SchoolName', 'FieldLabel']), key=lambda x: x[0])
        colors = px.colors.qualitative.Plotly
        for i, ((school, field), group) in enumerate(groups):
            color = colors[i % len(colors)]
            label = f"{school} [{field}]"
            group_s = group.sort_values('TotalPoints', ascending=False).reset_index(drop=True)
            group_s['Rank'] = group_s.index + 1
            regular = group_s[~group_s['IsExempt']]; exempt = group_s[group_s['IsExempt']]
            if not regular.empty:
                fig.add_trace(go.Scatter(x=regular['Rank'], y=regular['TotalPoints'], mode='lines+markers', name=label, legendgroup=label, line=dict(color=color), marker=dict(color=color)))
            if not exempt.empty:
                fig.add_trace(go.Scatter(x=exempt['Rank'], y=exempt['TotalPoints'], mode='markers', name=f"{label} (Odp. CJL)", legendgroup=label, marker=dict(color=color, symbol='x-thin', size=10, line=dict(color=color, width=2)), showlegend=False, hovertemplate="<b>%{text}</b><br>Rank: %{x}<br>Points: %{y}<extra></extra>", text=[f"{label} (Odp. CJL)"] * len(exempt)))
        fig.update_layout(xaxis_title="Pořadí", yaxis_title="Body", template="plotly_white", height=700, margin=dict(l=40, r=40, t=20, b=40), legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="left", x=0))
        st.plotly_chart(fig, use_container_width=True)

# Shared Statistics Table
if not display_df.empty:
    st.markdown("### 📋 Statistický přehled")
    groups = sorted(display_df.groupby(['SchoolName', 'FieldLabel']), key=lambda x: x[0])
    colors = px.colors.qualitative.Plotly
    color_map = {}
    stats_base = []

    for i, ((school, field), group) in enumerate(groups):
        color = colors[i % len(colors)]
        color_map[(school, field)] = color
        dist_all = []; dist_adm = []
        total_group = len(group); total_adm = len(group[group['Prijat'] == 1])
        for prio in range(1, 6):
            cnt_all = len(group[group['Priority'] == prio])
            pct_all = (cnt_all / total_group * 100) if total_group > 0 else 0
            dist_all.append(f"{cnt_all} ({round(pct_all)}%)")
            cnt_adm = len(group[(group['Prijat'] == 1) & (group['Priority'] == prio)])
            pct_adm = (cnt_adm / total_adm * 100) if total_adm > 0 else 0
            dist_adm.append(f"{cnt_adm} ({round(pct_adm)}%)")
        priority_dist_all_str = " + ".join(dist_all); priority_dist_admitted_str = " + ".join(dist_adm)
        
        # Calculate Elite Average (Top 10% of applicants in the field)
        top_10_count = max(1, round(len(group) * 0.1))
        elite_avg = round(group.sort_values('TotalPoints', ascending=False).head(top_10_count)['TotalPoints'].mean(), 1)
        
        group['ReasonClean'] = group['Reason'].replace(['nan', 'None', '', 'nan'], 'Neuvedeno')
        group.loc[group['Prijat'] == 1, 'ReasonClean'] = 'PŘIJAT'
        reason_groups = group.groupby('ReasonClean')
        admitted_regular = group[(group['Prijat'] == 1) & (~group['IsExempt'])]
        min_score_val = round(admitted_regular['TotalPoints'].min(), 1) if not admitted_regular.empty else None

        for reason, r_group in reason_groups:
            exempt = r_group[r_group['IsExempt']]; regular = r_group[~r_group['IsExempt']]
            cnt_regular = len(regular); cnt_exempt = len(exempt)
            avg_points_reg = round(regular['TotalPoints'].mean(), 1) if cnt_regular > 0 else 0
            stats_base.append({
                "SchoolName": school, "KKOV": field, "TotalCount": len(group),
                "PriorityDistAll": priority_dist_all_str, "PriorityDistAdm": priority_dist_admitted_str,
                "EliteAvg": elite_avg,
                "MinScore": min_score_val, "Reason": reason, "Počet": cnt_regular,
                "Průměr": avg_points_reg, "Cizinci": cnt_exempt
            })

    if stats_base:
        df_base = pd.DataFrame(stats_base)
        df_base['DisplayVal'] = df_base.apply(lambda row: f"{int(row['Počet'])} / {row['Průměr']:.1f}" + (f" (+{int(row['Cizinci'])} ciz)" if row['Cizinci'] > 0 else ""), axis=1)
        df_base['ReasonShort'] = df_base['Reason'].map(get_reason_label)
        pivot = df_base.pivot(index=['SchoolName', 'KKOV', 'TotalCount', 'PriorityDistAll', 'PriorityDistAdm', 'EliteAvg', 'MinScore'], columns='ReasonShort', values='DisplayVal').reset_index()
        pivot.rename(columns={
            'SchoolName': 'Škola', 'KKOV': 'Obor', 'TotalCount': 'Celkem přihlášek', 
            'PriorityDistAll': 'Priority (všichni)', 'MinScore': 'Poslední přijatý (body)', 
            'PriorityDistAdm': 'Priority (přijatí)', 'EliteAvg': 'Elitní průměr (10%)'
        }, inplace=True)
        
        current_cols = pivot.columns.tolist()
        final_cols = ['Škola', 'Obor', 'Celkem přihlášek', 'Priority (všichni)', 'Poslední přijatý (body)', 'Elitní průměr (10%)']
        if 'PŘIJAT' in current_cols:
            final_cols.append('PŘIJAT')
            if 'Priority (přijatí)' in current_cols: final_cols.append('Priority (přijatí)')
        for c in current_cols:
            if c not in final_cols: final_cols.append(c)
        pivot = pivot[final_cols].fillna("-")
        
        # Action Buttons for Detail Mode
        if view_mode == "Detailní rozbor školy":
            c1, c2 = st.columns(2)
            with c1:
                csv = pivot.to_csv(index=False).encode('utf-8-sig')
                st.download_button(label="📥 Stáhnout jako CSV", data=csv, file_name=f'stats_{school_name.replace(" ", "_")}.csv', mime='text/csv', use_container_width=True)
            with c2:
                kpi_data = {'total_apps': total_apps, 'success_rate': success_rate, 'comp_idx': competition_index}
                pdf_bytes = create_pdf_report(school_name, selected_year, selected_rounds, pivot, kpi_data)
                st.download_button(label="📄 Stáhnout PDF Report", data=pdf_bytes, file_name=f'report_{school_name.replace(" ", "_")}.pdf', mime='application/pdf', use_container_width=True)

        st.dataframe(pivot.style.apply(lambda row: [f'color: {color_map.get((row["Škola"], row["Obor"]), "#000000")}; font-weight: bold;' for _ in row.index], axis=1), use_container_width=True, hide_index=True)
    else:
        st.info("Žádná data pro statistiku.")
else:
    st.info("Žádná data pro statistiku.")
