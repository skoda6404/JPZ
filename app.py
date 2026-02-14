import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys
import re
import json
import io
import traceback

from src.data_loader import load_year_data, load_school_map, load_kkov_map, get_long_format, normalize_column_name, load_capacity_data, load_izo_to_redizo_map
from src.utils import get_grade_level, get_reason_label, clean_pdf_text, clean_col_name, reason_map
from src.pdf_generator import create_pdf_report
from src.ui_components import inject_custom_css, render_kpi_cards
from src.analysis import calculate_kpis, get_decile_data

# --- CONFIG ---
st.set_page_config(page_title="JPZ", layout="wide")

# --- ERROR LOGGING (for Cloud diagnostics) ---
def _log_error(context, e):
    """Log error to stderr (Cloud logs) and session state (page display)."""
    err_msg = f"[JPZ ERROR] {context}: {type(e).__name__}: {e}"
    tb = traceback.format_exc()
    print(err_msg, file=sys.stderr)
    print(tb, file=sys.stderr)
    st.session_state['_last_error'] = f"{err_msg}\n{tb}"

# --- NAVIGATION LOGIC ---
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "Srovnání škol"

try:
    # Apply pending navigation flags safely
    if st.session_state.get('pending_nav_school'):
        st.session_state['single_school_select'] = st.session_state['pending_nav_school']
        st.session_state.view_mode = "Detailní rozbor školy"
        st.session_state['navigated_from_comparison'] = True
        del st.session_state['pending_nav_school']
    
    if st.session_state.get('pending_back_nav'):
        st.session_state.view_mode = "Srovnání škol"
        del st.session_state['pending_back_nav']
        st.session_state['navigated_from_comparison'] = False
        # Clean up detail-mode widget keys to prevent orphaned state conflicts
        for key in ['detail_fields_select', 'single_school_select']:
            if key in st.session_state:
                del st.session_state[key]
        if 'saved_schools_selection' in st.session_state:
            st.session_state['_pending_upload_schools'] = st.session_state['saved_schools_selection']
        if 'saved_fields_selection' in st.session_state:
            st.session_state['_pending_upload_fields'] = st.session_state['saved_fields_selection']
except Exception as e:
    _log_error("Navigation flags", e)

# --- UI INITIALIZATION ---
inject_custom_css()

# --- GLOBAL CONSTANTS ---
# reason_map is now handled within get_reason_label in src.utils

# --- REMOVED: Load Functions (now in src/data_loader.py) ---

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

# --- DATA LOADING ---
school_map = load_school_map()
izo_to_redizo = load_izo_to_redizo_map()
raw_df = load_year_data(selected_year)
# Load capacities for all possible rounds (currently up to 2)
capacity_dfs = {r: load_capacity_data(selected_year, r) for r in [1, 2]}

def get_planned_capacity(riz, kkov, cap_dfs, selected_rounds):
    """
    Finds planned capacity for a specific school and field based on baseline logic:
    - Translates facility IZO to institution REDIZO using izo_to_redizo mapping.
    - If 1. kolo is selected (even with other rounds), use R1 as baseline.
    - If ONLY 2. kolo (or others) is selected, use that specific round's capacity.
    """
    if not selected_rounds or not cap_dfs: return None
    kkov_str = str(kkov).strip()
    
    # Translate facility IZO to institution REDIZO
    riz_str = str(riz)
    redizo = izo_to_redizo.get(riz_str, riz_str)
    
    # Priority: if R1 is in selected_rounds, use R1 capacity
    target_round = 1 if 1 in selected_rounds else selected_rounds[0]
    
    df = cap_dfs.get(target_round)
    if df is None or df.empty: return None

    # Try to find a match using REDIZO column (capacity files use institution-level REDIZO)
    if 'REDIZO' not in df.columns: return None
    
    match = df[(df['REDIZO'] == redizo) & (df['KKOV'] == kkov_str)]
    if not match.empty:
        return int(match['KAPACITA'].sum())
    
    # Fallback: try with original riz_str in case it's already a REDIZO
    if redizo != riz_str:
        match = df[(df['REDIZO'] == riz_str) & (df['KKOV'] == kkov_str)]
        if not match.empty:
            return int(match['KAPACITA'].sum())
    
    return None

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
# --- REMOVED: get_long_format (now in src/data_loader.py) ---

kkov_map = load_kkov_map()
long_df_all = get_long_format(filtered_df, school_map, kkov_map)

# --- SIDEBAR: GRADE FILTER ---
st.sidebar.markdown("---")
available_grades = sorted(long_df_all['Grade'].unique().tolist()) if not long_df_all.empty else []
if not available_grades:
    selected_grade = None
else:
    selected_grade = st.sidebar.radio("Ročník uchazeče", ["Všechny"] + available_grades, key='grade_filter')

if selected_grade and selected_grade != "Všechny":
    long_df = long_df_all[long_df_all['Grade'] == selected_grade]
else:
    long_df = long_df_all

# --- SIDEBAR: VIEW MODE ---
st.sidebar.markdown("---")
view_modes = ["Srovnání škol", "Detailní rozbor školy"]

# Use explicit key for stable widget identity across reruns
if 'view_mode_radio' not in st.session_state:
    st.session_state['view_mode_radio'] = st.session_state.view_mode
else:
    # Sync: if programmatic navigation changed view_mode, update the radio key
    if st.session_state.view_mode != st.session_state.get('view_mode_radio'):
        st.session_state['view_mode_radio'] = st.session_state.view_mode

view_mode = st.sidebar.radio("Zobrazení", view_modes, key='view_mode_radio')
st.session_state.view_mode = view_mode

# --- SIDEBAR: SELECTION FILTERS ---
if not long_df.empty:
    if view_mode == "Srovnání škol":
        # 1. School Filter (Multiple)
        available_schools = sorted(long_df['SchoolName'].unique().tolist())
        if 'selected_schools' not in st.session_state: st.session_state.selected_schools = []
        st.session_state.selected_schools = [s for s in st.session_state.selected_schools if s in available_schools]
        
        # Apply pending upload BEFORE widgets render (safe timing)
        if '_pending_upload_schools' in st.session_state:
            validated_schools = [s for s in st.session_state.pop('_pending_upload_schools') if s in available_schools]
            st.session_state['schools_select_v2'] = validated_schools
        if '_pending_upload_fields' in st.session_state:
            # Validate fields against the schools that will be selected
            pending_schools = st.session_state.get('schools_select_v2', [])
            if pending_schools:
                valid_field_options = sorted(long_df[long_df['SchoolName'].isin(pending_schools)]['FieldLabel'].unique().tolist())
                validated_fields = [f for f in st.session_state['_pending_upload_fields'] if f in valid_field_options]
                st.session_state['fields_select_v2'] = validated_fields
            del st.session_state['_pending_upload_fields']
        
        # Validate existing widget keys against current options (prevents stale-key crashes)
        if 'schools_select_v2' in st.session_state:
            st.session_state['schools_select_v2'] = [s for s in st.session_state['schools_select_v2'] if s in available_schools]
        
        selected_schools = st.sidebar.multiselect("Vyberte školy", options=available_schools, key='schools_select_v2', placeholder="Zvolte...")
        st.session_state.selected_schools = selected_schools
        
        available_fields = []
        if selected_schools:
            school_sub = long_df[long_df['SchoolName'].isin(selected_schools)]
            available_fields = sorted(school_sub['FieldLabel'].unique().tolist())
        
        # Validate existing field selection against current options
        if 'fields_select_v2' in st.session_state:
            st.session_state['fields_select_v2'] = [f for f in st.session_state['fields_select_v2'] if f in available_fields]
        
        selected_fields = st.sidebar.multiselect("Vyberte obory", options=available_fields, key='fields_select_v2', placeholder="Zvolte...")
        
        # --- CALLBACK FOR LOADING SELECTION ---
        def handle_selection_upload():
            if st.session_state.selection_upload_file is not None:
                try:
                    content = st.session_state.selection_upload_file.read().decode('utf-8-sig')
                    fav_data = json.loads(content)
                    new_schools = [s.strip() for s in fav_data.get('schools', [])]
                    new_fields = [f.strip() for f in fav_data.get('fields', [])]
                    
                    # Store as pending — applied safely before widgets on next rerun
                    valid_schools = [s for s in new_schools if s in available_schools]
                    st.session_state['_pending_upload_schools'] = valid_schools
                    st.session_state['_pending_upload_fields'] = new_fields
                except Exception as e:
                    st.session_state['upload_error'] = f"Chyba při nahrávání: {e}"

        # Simple File-based Export/Import
        st.sidebar.markdown(" ")
        with st.sidebar.expander("💾 Uložit / Načíst výběr"):
            if selected_schools:
                from src.storage import get_export_json
                export_data = get_export_json("vyber", selected_schools, selected_fields)
                st.download_button("📩 Uložit výběr do souboru", data=export_data, file_name="prijimacky_vyber.json", mime="application/json", width='stretch')
            
            st.markdown("---")
            st.markdown("📂 **Nahrát výběr ze souboru**")
            st.file_uploader("Vyberte JSON soubor s uloženým výběrem", type=['json'], label_visibility="collapsed", on_change=handle_selection_upload, key='selection_upload_file')
            
            if 'upload_error' in st.session_state:
                st.error(st.session_state.upload_error)
                del st.session_state['upload_error']

    else:
        # Detail Mode: Select single school
        st.sidebar.markdown("### 🏛️ Výběr školy")
        available_schools = sorted(long_df['SchoolName'].unique().tolist())
        selected_school = st.sidebar.selectbox("Škola pro detail", options=available_schools, index=None, key='single_school_select', placeholder="Zvolte...")
        selected_schools = [selected_school] if selected_school else []
        
        if selected_school:
            school_sub = long_df[long_df['SchoolName'] == selected_school]
            available_fields = sorted(school_sub['FieldLabel'].unique().tolist())
            
            # Clear stale field selection if it contains values not in current school's fields
            if 'detail_fields_select' in st.session_state:
                current_sel = st.session_state['detail_fields_select']
                if any(f not in available_fields for f in current_sel):
                    st.session_state['detail_fields_select'] = available_fields
            
            selected_fields = st.sidebar.multiselect("Vyberte obory", options=available_fields, default=available_fields, key='detail_fields_select', placeholder="Zvolte...")
        else:
            selected_fields = []
else:
    st.sidebar.warning("Žádná data pro vybrané parametry.")
    selected_schools, selected_fields = [], []


# --- MAIN PAGE CONTENT ---
if view_mode == "Detailní rozbor školy" and selected_schools:
    school_name = selected_schools[0]
    
    # Back button - strictly only if navigated from comparison
    if st.session_state.get('navigated_from_comparison'):
        if st.button("⬅️ Zpět na srovnání", width='stretch'):
            st.session_state['pending_back_nav'] = True
            st.rerun()

    school_data = long_df[(long_df['SchoolName'] == school_name) & (long_df['FieldLabel'].isin(selected_fields))]
    
    if school_data.empty:
        st.warning("Zvolte alespoň jeden obor v bočním panelu.")
        st.stop()
    
    # --- Points Comparison Chart ---
    col_hdr, col_tgl = st.columns([4, 1])
    with col_hdr:
        st.markdown("#### 📊 Rozložení bodů přijatých uchazečů")
    with col_tgl:
        st.markdown('<div style="text-align: right;">', unsafe_allow_html=True)
        use_deciles = st.checkbox("Decilové zobrazení", key="decile_detail", help="Normalizuje vodorovnou osu na 0-100 % kapacity oboru.")
        st.markdown('</div>', unsafe_allow_html=True)

    admitted_only_all = long_df[long_df['Prijat'] == 1].copy()
    if not admitted_only_all.empty:
        import plotly.graph_objects as go
        fig_pts = go.Figure()
        
        plot_df = get_decile_data(school_data[school_data['Prijat'] == 1]) if use_deciles else school_data[school_data['Prijat'] == 1].copy()
        if not use_deciles:
            # Add Rank manually if not using get_decile_data which adds Percentile
            res_list = []
            for name, group in plot_df.groupby(['FieldLabel']):
                group_s = group.sort_values('TotalPoints', ascending=False).reset_index(drop=True)
                group_s['Rank'] = group_s.index + 1
                res_list.append(group_s)
            plot_df = pd.concat(res_list) if res_list else plot_df

        groups_pts = sorted(plot_df.groupby(['FieldLabel']), key=lambda x: x[0])
        colors_pts = px.colors.qualitative.Plotly
        
        for i, (field, group) in enumerate(groups_pts):
            color = colors_pts[i % len(colors_pts)]
            label = f"{field}"
            x_col = 'Percentile' if use_deciles else 'Rank'
            regular = group[~group['IsExempt']]; exempt = group[group['IsExempt']]
            if not regular.empty:
                fig_pts.add_trace(go.Scatter(x=regular[x_col], y=regular['TotalPoints'], mode='lines+markers', name=label, line=dict(color=color), marker=dict(color=color)))
            if not exempt.empty:
                fig_pts.add_trace(go.Scatter(x=exempt[x_col], y=exempt['TotalPoints'], mode='markers', name=f"{label} (Odp. CJL)", marker=dict(color=color, symbol='x-thin', size=10), showlegend=False))
        
        fig_pts.update_layout(xaxis_title="Procenta (%)" if use_deciles else "Pořadí", yaxis_title="Body", template="plotly_white", height=400, margin=dict(l=40, r=40, t=20, b=40), legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="left", x=0))
        st.plotly_chart(fig_pts, width='stretch')
    
    st.markdown("---")
    
    # 1. KPI Cards
    # Calculate total capacity for all fields in the detail view
    total_planned = 0
    riz_detail = str(school_data['RED_IZO'].iloc[0]) if not school_data.empty else None
    if riz_detail:
        for kkov in school_data['KKOV'].unique():
            kkov_s = str(kkov)
            cap = get_planned_capacity(riz_detail, kkov_s, capacity_dfs, selected_rounds)
            if cap: total_planned += cap
            
    kpi_res = calculate_kpis(school_data, planned_capacity=total_planned if total_planned > 0 else None)
    
    # Unfilled school warning (A.1.2) - Status bar above Main Results
    if kpi_res['fullness_rate'] < 100:
        st.warning("⚠️ Škola ve vámi vybraném období nenaplnila kapacitu.")

    render_kpi_cards(kpi_res)
    
    st.markdown("---")
    
    # 2. Charts Row
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("#### 📝 Priority přihlášek (%)")
        prio_counts = []
        for f in sorted(school_data['FieldLabel'].unique()):
            f_data = school_data[school_data['FieldLabel'] == f]
            for p in range(1, 6):
                cnt = len(f_data[f_data['Priority'] == p])
                prio_counts.append({"Obor": f, "Priorita": f"{p}. priorita", "Počet": cnt})
        
        if prio_counts:
            df_prio = pd.DataFrame(prio_counts)
            total_per_obor = df_prio.groupby('Obor')['Počet'].transform('sum')
            df_prio['Procento'] = (df_prio['Počet'] / total_per_obor * 100).round(0)
            
            # Combine percentage and count for labels
            df_prio['Label'] = df_prio.apply(lambda r: f"{r['Procento']:.0f}% ({r['Počet']} přihlášek)" if r['Počet'] > 0 else "", axis=1)
            
            fig_prio = px.bar(df_prio, x="Obor", y="Procento", color="Priorita", 
                              height=400, text="Label",
                              barmode="stack", color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_prio.update_traces(textposition='inside', textfont_size=12)
            fig_prio.update_layout(yaxis_title="Procento (%)", showlegend=False)
            st.plotly_chart(fig_prio, width='stretch')

    with c2:
        st.markdown("#### ✅ Priority PŘIJATÝCH (%)")
        adm_data = school_data[school_data['Prijat'] == 1]
        prio_adm_counts = []
        for f in sorted(adm_data['FieldLabel'].unique()):
            f_data = adm_data[adm_data['FieldLabel'] == f]
            for p in range(1, 6):
                cnt = len(f_data[f_data['Priority'] == p])
                prio_adm_counts.append({"Obor": f, "Priorita": f"{p}. priorita", "Počet": cnt})
        
        if prio_adm_counts:
            df_prio_adm = pd.DataFrame(prio_adm_counts)
            total_per_obor_adm = df_prio_adm.groupby('Obor')['Počet'].transform('sum')
            df_prio_adm['Procento'] = (df_prio_adm['Počet'] / total_per_obor_adm * 100).round(0)
            
            # Combine percentage and count for labels
            df_prio_adm['Label'] = df_prio_adm.apply(lambda r: f"{r['Procento']:.0f}% ({r['Počet']} přijatých)" if r['Počet'] > 0 else "", axis=1)
            
            fig_prio_adm = px.bar(df_prio_adm, x="Obor", y="Procento", color="Priorita", 
                                  height=400, text="Label",
                                  barmode="stack", color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_prio_adm.update_traces(textposition='inside', textfont_size=12)
            fig_prio_adm.update_layout(yaxis_title="Procento (%)")
            st.plotly_chart(fig_prio_adm, width='stretch')

    st.markdown("---")
    
    # 3. Reasons Row (Restored)
    st.markdown("#### 🤔 Proč nebyli uchazeči přijati?")
    reason_counts = school_data[school_data['Prijat'] != 1]['Reason'].value_counts().reset_index()
    reason_counts.columns = ['Důvod', 'Počet']
    reason_counts['Důvod Label'] = reason_counts['Důvod'].map(lambda x: reason_map.get(x, x))
    
    if not reason_counts.empty:
        fig_pie = px.pie(reason_counts, values='Počet', names='Důvod Label', 
                         hole=0.4, height=350)
        fig_pie.update_layout(margin=dict(l=20, r=20, t=20, b=20), legend=dict(orientation="h", yanchor="bottom", y=-0.2))
        st.plotly_chart(fig_pie, width='stretch')

    st.markdown("---")
    
    # Redistribution Charts - Now stacked vertically with synced scale
    st.markdown("### 🔄 Analýza přelivu (Kam odešli ti, co k vám nenastoupili?)")
    not_here = school_data[school_data['Prijat'] != 1]
    
    # Robust categorization
    cat_a = not_here[not_here['Reason'].str.contains('vyssi_priorit|vyssi prioritu', case=False, na=False)]
    cat_b = not_here[not_here['Reason'].str.contains('kapacit', case=False, na=False)]
    cat_c = not_here[not_here['Reason'].str.contains('nespln|neprosp|nesplnil|nedosah|kriteri', case=False, na=False)]
    
    # NEW: Find global max across all categories for synced scale
    def get_max_count(df_red):
        df_v = df_red[df_red['AcceptedDetail'] != "Nepřijat / neznámá"]
        return df_v['AcceptedDetail'].value_counts().max() if not df_v.empty else 0
    
    global_max = max(get_max_count(cat_a), get_max_count(cat_b), get_max_count(cat_c), 1) # Min 1 to avoid range [0,0]
    
    def plot_redistribution(df_red, title, color_scale, max_x):
        df_valid = df_red[df_red['AcceptedDetail'] != "Nepřijat / neznámá"]
        if df_valid.empty:
            st.info(f"Pro kategorii '{title}' nemáme data o přijetí jinam.")
            return
        
        try:
            counts = df_valid['AcceptedDetail'].value_counts().reset_index().head(15)
            counts.columns = ['Cíl (Škola + Obor)', 'Počet']
            
            # Dynamic height with minimum to prevent rendering issues
            calc_height = max(250, 100 + (len(counts) * 45))
            
            fig = px.bar(counts, x='Počet', y='Cíl (Škola + Obor)', orientation='h',
                          title=title, color='Počet', color_continuous_scale=color_scale, 
                          height=calc_height, text='Počet',
                          range_x=[0, max_x * 1.1])
            
            fig.update_traces(textposition='outside', cliponaxis=False)
            fig.update_layout(
                yaxis={'categoryorder':'total ascending', 'title': None, 'automargin': True}, 
                xaxis={'title': 'Počet žáků'},
                margin=dict(l=20, r=50, t=50, b=50),
                title_x=0.0
            )
            st.plotly_chart(fig, width='stretch')
        except Exception as e:
            st.warning(f"Chyba při vykreslování grafu '{title}': {e}")

    # Stacked vertically as requested with synced scale
    plot_redistribution(cat_a, "A) Přijati na vyšší prioritu", "Viridis", global_max)
    plot_redistribution(cat_b, "B) Nepřijati z kapacitních důvodů", "Plasma", global_max)
    plot_redistribution(cat_c, "C) Nepřijati pro nesplnění podmínek (neprospěli)", "Magma", global_max)

    # Talent Comparison Chart (Tiny horizontal bar)
    # Talent Comparison Chart (Tiny horizontal bar)
    if not pd.isna(kpi_res['avg_admitted']) and not pd.isna(kpi_res['lost_avg']):
        st.markdown("---")
        talent_df = pd.DataFrame([
            {"Skupina": "Naši přijatí", "Body": kpi_res['avg_admitted'], "Barva": "green"},
            {"Skupina": "Utekli (vyšší priorita)", "Body": kpi_res['lost_avg'], "Barva": "red"}
        ])
        fig_talent = px.bar(talent_df, x="Body", y="Skupina", orientation='h',
                            title="Srovnání kvality: Naši přijatí vs. Ztracení (vyšší priorita)",
                            height=200, text=talent_df["Body"].apply(lambda x: f"{x:.1f} b."),
                            color="Skupina", color_discrete_map={"Naši přijatí": "#2ecc71", "Utekli (vyšší priorita)": "#e74c3c"})
        fig_talent.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_talent, width='stretch')

    # 3. Detailed Stats Table
    # (The shared table logic below will use this display_df)
    display_df = long_df[(long_df['SchoolName'] == school_name)]
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
    # --- Color Mapping ---
    # Create a stable color map for all selected school-field combinations
    all_groups = sorted(display_df.groupby(['SchoolName', 'FieldLabel']).groups.keys())
    color_palette = px.colors.qualitative.Plotly
    # We use a consistent label format for mapping
    color_map = {f"{s} ({f})": color_palette[i % len(color_palette)] for i, (s, f) in enumerate(all_groups)}

    # --- Main Chart ---
    col_hdr, col_tgl = st.columns([4, 1])
    with col_hdr:
        st.markdown("### 📊 Výsledky přijímacího řízení")
    with col_tgl:
        st.markdown('<div style="text-align: right;">', unsafe_allow_html=True)
        use_deciles_comp = st.checkbox("Decilové zobrazení", key="decile_comp", help="Normalizuje vodorovnou osu na 0-100 % kapacity oboru.")
        st.markdown('</div>', unsafe_allow_html=True)

    if admitted_only.empty:
        st.warning("Žádná data o PŘIJATÝCH uchazečích.")
    else:
        import plotly.graph_objects as go
        fig = go.Figure()
        
        plot_df_comp = get_decile_data(admitted_only) if use_deciles_comp else admitted_only.copy()
        if not use_deciles_comp:
            res_list = []
            for name, group in plot_df_comp.groupby(['SchoolName', 'FieldLabel']):
                group_s = group.sort_values('TotalPoints', ascending=False).reset_index(drop=True)
                group_s['Rank'] = group_s.index + 1
                res_list.append(group_s)
            plot_df_comp = pd.concat(res_list) if res_list else plot_df_comp

        groups = sorted(plot_df_comp.groupby(['SchoolName', 'FieldLabel']), key=lambda x: x[0])
        for (school, field), group in groups:
            label = f"{school} ({field})"
            color = color_map.get(label, "#333")
            x_col = 'Percentile' if use_deciles_comp else 'Rank'
            regular = group[~group['IsExempt']]; exempt = group[group['IsExempt']]
            if not regular.empty:
                fig.add_trace(go.Scatter(x=regular[x_col], y=regular['TotalPoints'], name=label, legendgroup=label, mode='lines+markers', line=dict(color=color), marker=dict(color=color)))
            if not exempt.empty:
                fig.add_trace(go.Scatter(x=exempt[x_col], y=exempt['TotalPoints'], mode='markers', name=f"{label} (Odp. CJL)", legendgroup=label, marker=dict(color=color, symbol='x-thin', size=10, line=dict(color=color, width=2)), showlegend=False, hovertemplate="<b>%{text}</b><br>"+x_col+": %{x}<br>Points: %{y}<extra></extra>", text=[f"{label} (Odp. CJL)"] * len(exempt)))
        fig.update_layout(xaxis_title="Procenta (%)" if use_deciles_comp else "Pořadí", yaxis_title="Body", template="plotly_white", height=700, margin=dict(l=40, r=40, t=20, b=40), legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="left", x=0), showlegend=True)
        st.plotly_chart(fig, width='stretch')

    # --- Metric Comparison Block ---
    st.markdown("---")
    st.markdown("### 📊 Srovnání škol podle metriky")
    
    comparable_metrics = {
        # Block 1: Hlavní výsledky
        "Celkový zájem (přihlášky)": "total_apps",
        "Index převisu": "comp_idx",
        "Index reálné poptávky": "pure_demand_idx",
        "Celková úspěšnost (%)": "success_rate",
        
        # Block 2: Bodová úroveň
        "Bodový průměr přijatých": "avg_admitted",
        "Body posledního přijatého": "min_score",
        "Průměr horních 10 %": "elite_avg",
        "Průměr spodních 25 %": "bottom_25_avg",
        "Bodový rozdíl (Gap)": "talent_gap",
        
        # Block 3: Strategické ukazatele
        "Poptávka skalních zájemců (%)": "interest_p1_pct",
        "Podíl skalních žáků (%)": "intake_p1_pct",
        "Podíl náhradních voleb (P3+) (%)": "intake_p3p_pct",
        "Intenzita odlivu (%)": "release_rate",
        
        # Block 5: Kapacitní analýza
        "Plánovaná kapacita": "planned_capacity",
        "Míra naplněnosti (%)": "fullness_rate",
        "Volná místa": "vacant_seats",
        "Vzdali se přijetí": "gave_up_count",
        "Úspěšnost 1. priority (%)": "p1_loyalty"
    }
    
    selected_metric_label = st.selectbox("Vyberte metriku pro srovnání", options=list(comparable_metrics.keys()))
    
    # --- Metric Explanation (NEW) ---
    from src.ui_components import METRIC_HELP
    if selected_metric_label in METRIC_HELP:
        help_data = METRIC_HELP[selected_metric_label]
        st.info(f"💡 **{help_data['title']}**\n\n{help_data['desc']}", icon="❔")
    
    selected_metric_key = comparable_metrics[selected_metric_label]
    
    # Calculate metrics for all selected groups
    metric_data = []
    overlay_data = []
    for (school, field), group in display_df.groupby(['SchoolName', 'FieldLabel']):
        # Get capacity for this specific school/field combination
        riz = str(group['RED_IZO'].iloc[0])
        kkov = str(group['KKOV'].iloc[0])
        field_cap = get_planned_capacity(riz, kkov, capacity_dfs, selected_rounds)
        
        kpis = calculate_kpis(group, planned_capacity=field_cap)
        val = kpis.get(selected_metric_key)
        if val is not None:
            # Scale metrics if labels have (%) and it's not already handled in analysis
            if "(%)" in selected_metric_label and selected_metric_key not in ["comp_idx", "pure_demand_idx"]:
                # Note: Most values are already 0-100 from analysis.py, 
                # but we keep this for consistency if needed.
                pass
                
            label = f"{school} ({field})"
            metric_data.append({"Škola/Obor": label, "Hodnota": round(val, 2), "Barva": color_map.get(label, "#333")})
            
            # Use specific overlays for specific metrics
            if selected_metric_key == "bottom_25_avg" and kpis.get("avg_admitted"):
                overlay_data.append({"Škola/Obor": label, "Reference": round(kpis["avg_admitted"], 2), "RefLabel": "Průměr třídy"})
            elif selected_metric_key == "pure_demand_idx" and kpis.get("comp_idx"):
                overlay_data.append({"Škola/Obor": label, "Reference": round(kpis["comp_idx"], 2), "RefLabel": "Index převisu"})
    
    if metric_data:
        # 1. EXPLICIT SORTING in Python
        df_metric = pd.DataFrame(metric_data).sort_values("Hodnota", ascending=True)
        sorted_labels = df_metric["Škola/Obor"].tolist()
        
        # SPECIAL CASE: Overlay Charts (Bottom 25% or Real Demand Index)
        use_overlay = selected_metric_key in ["bottom_25_avg", "pure_demand_idx"] and overlay_data
        
        if use_overlay:
            import plotly.graph_objects as go
            fig_metric = go.Figure()
            
            # Prepare overlay data map
            ov_map = {d['Škola/Obor']: d['Reference'] for d in overlay_data}
            ref_name = overlay_data[0]['RefLabel'] if overlay_data else "Reference"
            data_name = selected_metric_label
            
            # Background bars: Reference (Transparent with border)
            fig_metric.add_trace(go.Bar(
                x=[ov_map.get(lbl, 0) for lbl in sorted_labels],
                y=sorted_labels,
                orientation='h',
                name=ref_name,
                marker=dict(
                    color='rgba(150,150,150,0.05)', # Ultra-subtle background
                    line=dict(color='rgba(100,100,100,0.7)', width=1.5) # Sharper border
                ),
                hovertemplate=f"{ref_name}: %{{x:.2f}}<extra></extra>"
            ))
            
            # Foreground bars: Data (Colored)
            fig_metric.add_trace(go.Bar(
                x=df_metric["Hodnota"],
                y=sorted_labels,
                orientation='h',
                name=data_name,
                marker=dict(color=[color_map.get(lbl, "#333") for lbl in sorted_labels]),
                text=df_metric["Hodnota"],
                textposition='inside',
                insidetextanchor='end',
                hovertemplate=f"{data_name}: %{{x:.2f}}<extra></extra>"
            ))
            
            # Add Annotations (Delta and Reference Value)
            for lbl in sorted_labels:
                val_data = df_metric[df_metric["Škola/Obor"] == lbl]["Hodnota"].iloc[0]
                val_ref = ov_map.get(lbl)
                if val_ref:
                    delta = val_data - val_ref
                    # 1. Reference Value at the end of transparent bar
                    fig_metric.add_annotation(
                        x=val_ref, y=lbl,
                        text=f" {val_ref:.2f}",
                        showarrow=False,
                        xanchor='left',
                        font=dict(size=11, color="#666")
                    )
                    # 2. Delta (Δ) in the gap between bars
                    # Position it at midpoint if possible
                    gap_mid = (val_data + val_ref) / 2
                    if abs(val_data - val_ref) > (val_ref * 0.05): # Only show if gap is significant
                        fig_metric.add_annotation(
                            x=gap_mid, y=lbl,
                            text=f"Δ {delta:+.1f}",
                            showarrow=False,
                            font=dict(size=10, color="gray", style="italic")
                        )
            
            chart_height = 80 + len(sorted_labels) * 35
            fig_metric.update_layout(
                barmode='overlay',
                height=chart_height,
                showlegend=False
            )
        else:
            # Standard Plotly Express Bar
            chart_height = 80 + len(sorted_labels) * 35
            fig_metric = px.bar(df_metric, x="Hodnota", y="Škola/Obor", orientation='h',
                                color="Škola/Obor", color_discrete_map=color_map,
                                text="Hodnota", height=chart_height)
            fig_metric.update_traces(textposition='auto')

        fig_metric.update_layout(
            yaxis={'categoryorder':'array', 'categoryarray': sorted_labels, 'title': None}, 
            xaxis_title=selected_metric_label,
            showlegend=False,
            margin=dict(l=20, r=80, t=30, b=10) # Increased right margin for labels
        )
        st.plotly_chart(fig_metric, width='stretch')
    else:
        st.info(f"💡 Metrika **{selected_metric_label}** není pro vybrané školy relevantní. Pravděpodobně nenaplnily kapacitu, takže u nich nedošlo k omezení výběru a metrika 'hranice' u nich neexistuje.")

# Shared Statistics Table
if not display_df.empty:
    if view_mode == "Srovnání škol":
        st.markdown("### 📋 Statistický přehled (srovnání)")
    else:
        st.markdown("#### 📋 Podrobné statistiky oboru")
    
    groups = sorted(display_df.groupby(['SchoolName', 'FieldLabel']), key=lambda x: x[0])
    color_map = {}
    stats_data = []

    def format_stat(subset):
        if subset.empty: return "-"
        exempt = subset[subset['IsExempt']]
        regular = subset[~subset['IsExempt']]
        cnt_reg = len(regular)
        cnt_exc = len(exempt)
        avg_reg = round(regular['TotalPoints'].mean(), 1) if cnt_reg > 0 else 0
        
        total_cnt = cnt_reg + cnt_exc
        base = f"{total_cnt}"
        if cnt_exc > 0:
            base += f" ({cnt_exc} ciz.)"
        base += f" / {avg_reg:.1f}"
        return base

    for i, ((school, field), group) in enumerate(groups):
        color_map[(school, field)] = px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]
        
        # 3. Kapacita
        riz_val = str(group['RED_IZO'].iloc[0])
        kkov_val = str(group['KKOV'].iloc[0])
        planned_cap = get_planned_capacity(riz_val, kkov_val, capacity_dfs, selected_rounds)
        
        # 4. Počet přihlášek
        total_apps = len(group)
        
        # 5. Priorita přihl. (10+12+1+0+0)
        prio_counts = [len(group[group['Priority'] == p]) for p in range(1, 6)]
        prio_dist_str = "+".join(map(str, prio_counts))
        
        # 6. Přijato
        admitted = group[group['Prijat'] == 1]
        admitted_stat = format_stat(admitted)
        
        # 7. Min. bodů (only regular admitted)
        adm_reg = admitted[~admitted['IsExempt']]
        min_score = f"{adm_reg['TotalPoints'].min():.1f}" if not adm_reg.empty else "-"
        
        # 8. Priorita přij.
        prio_adm_counts = [len(admitted[admitted['Priority'] == p]) for p in range(1, 6)]
        prio_adm_str = "+".join(map(str, prio_adm_counts))
        
        # 9. Vzdali se (NEW)
        gave_up = group[group.get('GaveUpSpot', False) == True]
        gave_up_stat = format_stat(gave_up)

        # 10. Vyšší priorita (vzdal se nebo přijat výše)
        higher_prio = group[group['Reason'].str.contains('vzdal|vyssi_prioritu', case=False, na=False)]
        higher_prio_stat = format_stat(higher_prio)
        
        # 11. Kapacit. důvod
        cap_reject = group[group['Reason'].str.contains('kapacit', case=False, na=False)]
        cap_stat = format_stat(cap_reject)
        
        # 12. Nesplnili
        failed = group[group['Reason'].str.contains('nespln|neprosp|nesplnil|nedosah|kriteri', case=False, na=False)]
        failed_stat = format_stat(failed)
        
        stats_data.append({
            "Škola": school,
            "Obor": field,
            "Kapacita": planned_cap if planned_cap else "-",
            "Přihlášky": total_apps,
            "Priorita přihl.": prio_dist_str,
            "Přijato": admitted_stat,
            "Min. bodů": min_score,
            "Priorita přij.": prio_adm_str,
            "Vzdali se": gave_up_stat,
            "Vyšší priorita": higher_prio_stat,
            "Kapacit. důvod": cap_stat,
            "Nesplnili": failed_stat
        })

    if stats_data:
        df_stats = pd.DataFrame(stats_data)
        
        # Action Buttons
        if view_mode == "Detailní rozbor školy":
            c1, c2 = st.columns(2)
            with c1:
                csv = df_stats.to_csv(index=False).encode('utf-8-sig')
                st.download_button(label="📥 Stáhnout jako CSV", data=csv, file_name=f'stats_{school_name.replace(" ", "_")}.csv', mime='text/csv', width='stretch')
            with c2:
                kpi_data = calculate_kpis(school_data)
                pdf_bytes = create_pdf_report(school_name, selected_year, selected_rounds, df_stats, kpi_data)
                st.download_button(label="📄 Stáhnout PDF Report", data=pdf_bytes, file_name=f'report_{school_name.replace(" ", "_")}.pdf', mime='application/pdf', width='stretch')

        col_cfg = {
            "Škola": st.column_config.TextColumn("Škola", width=180),
            "Obor": st.column_config.TextColumn("Obor", width=160),
            "Kapacita": st.column_config.TextColumn("Kapacita", width=70),
            "Přihlášky": st.column_config.NumberColumn("Přihl.", width=60),
            "Priorita přihl.": st.column_config.TextColumn("Priorita přihl.", width=100),
            "Přijato": st.column_config.TextColumn("Přijato", width=110),
            "Min. bodů": st.column_config.TextColumn("Min. bodů", width=70),
            "Priorita přij.": st.column_config.TextColumn("Priorita přij.", width=100),
            "Vzdali se": st.column_config.TextColumn("Vzdali se", width=110),
            "Vyšší priorita": st.column_config.TextColumn("Vyšší priorita", width=110),
            "Kapacit. důvod": st.column_config.TextColumn("Kapacit. důvod", width=110),
            "Nesplnili": st.column_config.TextColumn("Nesplnili", width=110),
        }
        
        selected_row = st.dataframe(
            df_stats.style.apply(lambda row: [f'color: {color_map.get((row["Škola"], row["Obor"]), "#000000")}; font-weight: bold;' for _ in row.index], axis=1), 
            width='stretch', 
            hide_index=True,
            column_config=col_cfg,
            on_select="rerun",
            selection_mode="single-row"
        )
        
        if view_mode == "Srovnání škol" and selected_row and hasattr(selected_row, "selection") and selected_row.selection.rows:
            idx = selected_row.selection.rows[0]
            school_to_detail = df_stats.iloc[idx]['Škola']
            st.session_state['saved_schools_selection'] = st.session_state.get('schools_select_v2', [])
            st.session_state['saved_fields_selection'] = st.session_state.get('fields_select_v2', [])
            st.session_state['pending_nav_school'] = school_to_detail
            st.rerun()
    else:
        st.info("Žádná data pro statistiku.")
else:
    st.info("Žádná data pro statistiku.")

# --- DEBUG FOOTER (temporary, for Cloud diagnostics) ---
with st.expander("🔧 Debug info", expanded=bool(st.session_state.get('_last_error'))):
    if st.session_state.get('_last_error'):
        st.error("Poslední zachycená chyba:")
        st.code(st.session_state['_last_error'])
        if st.button("Smazat chybu"):
            del st.session_state['_last_error']
            st.rerun()
    debug_keys = ['view_mode', 'view_mode_radio', 'navigated_from_comparison',
                  'schools_select_v2', 'fields_select_v2', 'single_school_select',
                  'detail_fields_select', '_pending_upload_schools', '_pending_upload_fields',
                  'pending_nav_school', 'pending_back_nav']
    debug_state = {k: str(st.session_state.get(k, '---')) for k in debug_keys}
    st.json(debug_state)
