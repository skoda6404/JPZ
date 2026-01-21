import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys
import re

# --- CONFIG ---
# --- CONFIG ---
st.set_page_config(page_title="JPZ", layout="wide")

# ... (omitted lines)

# --- MAIN PAGE ---
st.title(f"📈 JPZ {selected_year}")

if not selected_schools or not selected_fields:
    st.info("Zvolte v bočním panelu školy a obory.")
    st.stop()

display_df = long_df[(long_df['SchoolName'].isin(selected_schools)) & (long_df['KKOV'].isin(selected_fields))]
# In 2024 bool was True/False -> 1/0. In 2025 1/2. 
# My normalization made it 1 for accepted.
admitted_only = display_df[display_df['Prijat'] == 1].copy()

# Header metrics removed per request, moved relevant details to the table below.
st.markdown("### 📊 Výsledky přijímacího řízení")

# Chart
if admitted_only.empty:
    st.warning("Žádná data o PŘIJATÝCH uchazečích.")
else:
    import plotly.graph_objects as go
    
    fig = go.Figure()
    
    # Sort by school/field to maintain consistent colors
    groups = sorted(admitted_only.groupby(['SchoolName', 'KKOV']), key=lambda x: x[0])
    
    # Define a color palette cycle if needed, or rely on plotly's default
    colors = px.colors.qualitative.Plotly
    
    for i, ((school, field), group) in enumerate(groups):
        color = colors[i % len(colors)]
        label = f"{school} [{field}]"
        
        # Sort all by total points for ranking
        group_s = group.sort_values('TotalPoints', ascending=False).reset_index(drop=True)
        group_s['Rank'] = group_s.index + 1
        
        # Split into Regular and Exempt
        regular = group_s[~group_s['IsExempt']]
        exempt = group_s[group_s['IsExempt']]
        
        # Trace 1: Regular students (Line + Markers)
        if not regular.empty:
            fig.add_trace(go.Scatter(
                x=regular['Rank'], y=regular['TotalPoints'],
                mode='lines+markers',
                name=label,
                legendgroup=label,
                line=dict(color=color),
                marker=dict(color=color)
            ))
            
            # Trace 2: Exempt students (Markers only, Distinct Symbol)
        if not exempt.empty:
            fig.add_trace(go.Scatter(
                x=exempt['Rank'], y=exempt['TotalPoints'],
                mode='markers',
                name=f"{label} (Odp. CJL)",
                legendgroup=label,
                # Fix: Use same color as line, apply width to line prop of marker if needed, but color is key
                marker=dict(color=color, symbol='x-thin', size=10, line=dict(color=color, width=2)),
                showlegend=False, 
                hovertemplate="<b>%{text}</b><br>Rank: %{x}<br>Points: %{y}<extra></extra>",
                text=[f"{label} (Odp. CJL)"] * len(exempt)
            ))
            
    fig.update_layout(
        xaxis_title="Pořadí",
        yaxis_title="Body",
        template="plotly_white",
        height=700,
        margin=dict(l=40, r=40, t=20, b=40),
        legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="left", x=0)
    )
    st.plotly_chart(fig, use_container_width=True)

# Table
st.markdown("### 📋 Podrobné statistiky")

# Pre-calc colors
groups = sorted(display_df.groupby(['SchoolName', 'KKOV']), key=lambda x: x[0])
colors = px.colors.qualitative.Plotly
color_map = {} # (School, Field) -> Color

stats_base = []

for i, ((school, field), group) in enumerate(groups):
    color = colors[i % len(colors)]
    color_map[(school, field)] = color
    
    # Clean Reason
    group['ReasonClean'] = group['Reason'].replace(['nan', 'None', '', 'nan'], 'Neuvedeno')
    group.loc[group['Prijat'] == 1, 'ReasonClean'] = 'PŘIJAT'
    
    # Aggregation per reason
    reason_groups = group.groupby('ReasonClean')
    
    # Calculate Min Score of Admitted (Regular only)
    admitted_regular = group[(group['Prijat'] == 1) & (~group['IsExempt'])]
    min_score_val = round(admitted_regular['TotalPoints'].min(), 1) if not admitted_regular.empty else None

    for reason, r_group in reason_groups:
        # Split exempt
        exempt = r_group[r_group['IsExempt']]
        regular = r_group[~r_group['IsExempt']]
        
        cnt_regular = len(regular)
        cnt_exempt = len(exempt)
        
        # Avg only for regular
        avg_points_reg = round(regular['TotalPoints'].mean(), 1) if cnt_regular > 0 else 0
        
        stats_base.append({
            "SchoolName": school,
            "KKOV": field,
            "TotalCount": len(group), # Store total for the group
            "MinScore": min_score_val,
            "Reason": reason,
            "Počet": cnt_regular,
            "Průměr": avg_points_reg,
            "Cizinci": cnt_exempt
        })

# Mapping for nicer columns
reason_map = {
    'PŘIJAT': 'PŘIJAT',
    'prijat_na_vyssi_prioritu': 'Vyšší priorita',
    'pro_nedostacujici_kapacitu': 'Kapacita',
    'pro_nesplneni_podminek': 'Nesplnil',
    'Neuvedeno': 'Jiné'
}
def get_reason_label(r):
    return reason_map.get(r, r)

if stats_base:
    df_base = pd.DataFrame(stats_base)
    
    # Create Combined String Column
    # Format: "Cnt / Avg" (plus exempts if any)
    def fmt_val(row):
        base = f"{int(row['Počet'])} / {row['Průměr']:.1f}"
        if row['Cizinci'] > 0:
            base += f" (+{int(row['Cizinci'])} ciz)"
        return base
        
    df_base['DisplayVal'] = df_base.apply(fmt_val, axis=1)
    df_base['ReasonShort'] = df_base['Reason'].map(get_reason_label)
    
    # Pivot
    # We include TotalCount and MinScore in index so it is preserved, then reset
    pivot = df_base.pivot(index=['SchoolName', 'KKOV', 'TotalCount', 'MinScore'], columns='ReasonShort', values='DisplayVal')
    
    # Columns are now just the reason names. 
    # Optional: Reorder columns? PŘIJAT first?
    cols = sorted(pivot.columns.tolist())
    # Move PŘIJAT to front if exists
    if 'PŘIJAT' in cols:
        cols.insert(0, cols.pop(cols.index('PŘIJAT')))
    pivot = pivot[cols]
    
    pivot = pivot.reset_index()
    pivot.rename(columns={
        'SchoolName': 'Škola', 
        'KKOV': 'Obor', 
        'TotalCount': 'Celkem přihlášek',
        'MinScore': 'Poslední přijatý (body)'
    }, inplace=True)
    
    # Fill NaN (where reason didn't exist for that school)
    pivot = pivot.fillna("-") 
    
    # Styling
    def get_row_style(row):
        key = (row['Škola'], row['Obor'])
        c = color_map.get(key, '#000000')
        return [f'color: {c}; font-weight: bold;' for _ in row.index]

    styler = pivot.style.apply(get_row_style, axis=1)\
                  .hide(axis='index')
    
    st.dataframe(styler, use_container_width=True, hide_index=True)
else:
    st.info("Žádná data pro statistiku.")
