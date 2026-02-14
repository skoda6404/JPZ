import pandas as pd
import numpy as np

def calculate_kpis(school_data, planned_capacity=None):
    """Calculates all key metrics for a given school data subset, excluding exempt students from averages."""
    total_apps = len(school_data)
    admitted = school_data[school_data['Prijat'] == 1]
    
    total_admitted = len(admitted)
    actual_occupied = total_admitted 
    
    gave_up_mask = school_data['Reason'].str.contains('vzdal', case=False, na=False)
    gave_up_total = len(school_data[gave_up_mask])
    
    # Calculate counts and basic indicators first
    cap_count = len(school_data[school_data['Reason'].str.contains('kapacit', case=False, na=False)])
    denom_demand = max(total_admitted, planned_capacity) if planned_capacity and planned_capacity > 0 else total_admitted
    pure_demand_idx = ((total_admitted + cap_count) / denom_demand) if denom_demand > 0 else 0
    
    # Smart Success Rate: If demand <= capacity, success is 100% (everyone meeting conditions could be admitted)
    if pure_demand_idx <= 1.0:
        success_rate = 100.0
    else:
        success_rate = (total_admitted / total_apps * 100) if total_apps > 0 else 0
    
    # SYSTEMIC FIX: Use planned capacity if available.
    denom = planned_capacity if planned_capacity is not None and planned_capacity > 0 else total_admitted
    competition_index = (total_apps / denom) if denom > 0 else 0
    
    # New metrics
    fullness_rate = (actual_occupied / planned_capacity * 100) if planned_capacity and planned_capacity > 0 else 100
    vacant_seats = max(0, planned_capacity - actual_occupied) if planned_capacity is not None else 0
    
    # Admitted metrics (avgs excluding exempts)
    regular_admitted = admitted[~admitted['IsExempt']]
    exempt_admitted = admitted[admitted['IsExempt']]
    min_score = regular_admitted['TotalPoints'].min() if not regular_admitted.empty else None
    
    avg_admitted_val = regular_admitted['TotalPoints'].mean() if not regular_admitted.empty else None
    
    # Structure for Admitted (count/avg/exempt)
    avg_admitted_struct = {
        'cnt_reg': len(regular_admitted), 
        'avg_reg': avg_admitted_val, 
        'cnt_exc': len(exempt_admitted)
    }
    
    # Elite (Top 10% of applicants in the field - ignoring exempts for avg?)
    # Usually "Elite" refers to high performers, so regular students.
    top_10_count = max(1, round(total_apps * 0.1))
    # Filter regular for elite avg calculation
    regular_apps = school_data[~school_data['IsExempt']]
    elite_avg = regular_apps.sort_values('TotalPoints', ascending=False).head(top_10_count)['TotalPoints'].mean() if not regular_apps.empty else None
    
    # Rejected Metrics Helper
    rejected = school_data[school_data['Prijat'] != 1]
    
    def get_reject_stats_struct(reason_pattern):
        subset = rejected[rejected['Reason'].str.contains(reason_pattern, case=False, na=False)]
        exempt = subset[subset['IsExempt']]
        regular = subset[~subset['IsExempt']]
        
        cnt_reg = len(regular)
        cnt_exc = len(exempt) # Cizinci
        avg_reg = regular['TotalPoints'].mean() if cnt_reg > 0 else None
        
        return {
            'cnt_reg': cnt_reg,
            'avg_reg': avg_reg,
            'cnt_exc': cnt_exc,
            'total': len(subset)
        }

    cap_stats = get_reject_stats_struct('kapacit')
    lost_stats = get_reject_stats_struct('vyssi_priorit|vyssi prioritu')
    fail_stats = get_reject_stats_struct('nespln|neprosp|nesplnil|nedosah|kriteri')
    
    # cap_count and pure_demand_idx are already calculated at the top
    cap_reject_rate = (cap_count / total_apps * 100) if total_apps > 0 else 0
    
    # Priority 1 loyalty
    p1_data = school_data[school_data['Priority'] == 1]
    p1_loyalty = (len(p1_data[p1_data['Prijat'] == 1]) / len(p1_data) * 100) if not p1_data.empty else 0
    
    # Talent Gap (Regular vs Regular)
    lost_avg_val = lost_stats['avg_reg']
    talent_gap = (lost_avg_val - avg_admitted_val) if (lost_avg_val is not None and avg_admitted_val is not None) else 0

    not_passed = school_data['Reason'].str.contains('nespln|neprosp|nesplnil|nedosah|kriteri', case=False, na=False)
    # pure_demand_idx is already calculated at the top
    
    # Pre-calculate counts for new strategic metrics
    p1_count = len(school_data[school_data['Priority'] == 1])
    intake_p1_count = len(admitted[admitted['Priority'] == 1])
    intake_p3p_count = len(admitted[admitted['Priority'] >= 3])

    # Strategic / Marketing KPIs
    # Interest P1 Concentration (Refined A.1.4: Relative to Capacity)
    denom_cap = max(1, planned_capacity) if planned_capacity else total_apps
    interest_p1_pct = (p1_count / denom_cap) * 100 if denom_cap > 0 else 0
    
    # Intake Motivation P1 (Refined A.1.1: Relative to Capacity)
    # How much of the planned class is filled by loyal P1 fans
    intake_p1_pct = (intake_p1_count / denom_cap) * 100 if denom_cap > 0 else 0
    
    # Intake Backup P3+ (Refined A.1.2: Relative to Capacity)
    # How much of the planned class is filled by backup choices
    intake_p3p_pct = (intake_p3p_count / denom_cap) * 100 if denom_cap > 0 else 0
    
    # Release Rate / Outflow Intensity (Refined A.1.3: Outflow / Total Potential)
    # Range 0-100%
    lost_count = lost_stats['total']
    release_rate = (lost_count / (total_admitted + lost_count)) * 100 if (total_admitted + lost_count) > 0 else 0

    # Bottom 25% of admitted (Regular only)
    bottom_25_count = max(1, round(len(regular_admitted) * 0.25))
    bottom_25_avg = regular_admitted.sort_values('TotalPoints', ascending=True).head(bottom_25_count)['TotalPoints'].mean() if not regular_admitted.empty else None

    # Boundary Density
    boundary_density = 0
    if min_score is not None and pure_demand_idx > 1.0:
        boundary_density = len(school_data[(school_data['TotalPoints'] >= min_score - 5) & (school_data['TotalPoints'] <= min_score + 5)])
    else:
        boundary_density = None

    return {
        'total_apps': total_apps,
        'total_admitted': total_admitted,
        'gave_up_count': gave_up_total,
        'planned_capacity': planned_capacity,
        'fullness_rate': fullness_rate,
        'vacant_seats': vacant_seats,
        'success_rate': success_rate,
        'comp_idx': competition_index,
        'min_score': min_score,
        
        'avg_admitted': avg_admitted_val, # Scalar for charts
        'avg_admitted_struct': avg_admitted_struct, # Structured for cards
        
        'elite_avg': elite_avg,
        'bottom_25_avg': bottom_25_avg,
        'cap_reject_rate': cap_reject_rate,
        'p1_loyalty': p1_loyalty,
        'talent_gap': talent_gap,
        'pure_demand_idx': pure_demand_idx,
        
        'interest_p1_pct': interest_p1_pct,
        'intake_p1_pct': intake_p1_pct,
        'intake_p3p_pct': intake_p3p_pct,
        'release_rate': release_rate,
        'boundary_density': boundary_density,
        
        'cap_count': cap_count,
        'cap_avg': cap_stats['avg_reg'], # Scalar for charts
        'lost_count': lost_count,
        'lost_avg': lost_avg_val, # Scalar
        'fail_count': fail_stats['total'],
        'fail_avg': fail_stats['avg_reg'], # Scalar
        
        'cap_stats': cap_stats, # New struct
        'lost_stats': lost_stats, # New struct
        'fail_stats': fail_stats, # New struct
    }

def get_decile_data(df):
    """Normalizes rank to percentiles (0-100) for decile chart comparison"""
    if df.empty: return df
    
    res_list = []
    groups = df.groupby(['SchoolName', 'FieldLabel'])
    for name, group in groups:
        group_s = group.sort_values('TotalPoints', ascending=False).reset_index(drop=True)
        # Percentile: (index / (len-1)) * 100 if len > 1 else 0
        # Actually user said "100% would be the count of students of school with highest/lowest...?"
        # Let's use rank / total_in_group * 100 for normalization.
        n = len(group_s)
        group_s['Percentile'] = ((group_s.index + 1) / n * 100).round(1)
        res_list.append(group_s)
    
    return pd.concat(res_list, ignore_index=True) if res_list else pd.DataFrame()
