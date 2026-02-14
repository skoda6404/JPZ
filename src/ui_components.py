import streamlit as st

METRIC_HELP = {
    "Celkový zájem (přihlášky)": {
        "title": "Celkový počet podaných přihlášek.",
        "desc": "🎯 **Pro uchazeče:** Ukazuje celkovou popularitu oboru. Vysoké číslo značí silnou konkurenci, ale i to, že se na obor hlásí hodně lidí jako na jednu z mnoha voleb.\n\n"
                "🏛️ **Pro ředitele:** Indikátor kapacity trhu a administrativní náročnosti. Klíčové pro plánování marketingu."
    },
    "Index převisu": {
        "title": "Poměr uchazečů na jedno volné místo.",
        "desc": "🎯 **Pro uchazeče:** Vyjadřuje, kolik studentů v průměru bojuje o jednu židli v lavici.\n\n"
                "🏛️ **Pro ředitele:** Vyjadřuje sílu poptávky. Hodnota pod 1.0 znamená neobsazenou kapacitu."
    },
    "Index reálné poptávky": {
        "title": "Skutečný zájem vážných uchazečů o místo v lavici.",
        "desc": "🎯 **Pro uchazeče:** Ukazuje reálnou konkurenci. Počítá pouze s těmi, kteří na škole reálně chtěli studovat (byli přijati nebo odmítnuti jen kvůli kapacitě).\n\n"
                "🏛️ **Pro ředitele:** Nejdůležitější číslo pro strategii. Vyjadřuje tlak na kapacitu školy ze strany vážných zájemců.\n\n"
                "💡 **Výpočet:** (Přijatí + Odmítnutí z kapacity) / Kapacita\n"
                "• *Příklad 1:* Kapacita 30, přijato 30, odmítnuto z kapacity 5. Index = (30+5)/30 = **1.17** (převis vážných zájemců).\n"
                "• *Příklad 2:* Kapacita 15, přijato 7, nikdo neodmítnut z kapacity. Index = 7/15 = **0.47** (zájem nepokryl ani polovinu kapacity)."
    },
    "Celková úspěšnost (%)": {
        "title": "Jaká byla šance na přijetí na školu.",
        "desc": "🎯 **Pro uchazeče:** Pravděpodobnost, že mé úsilí povede k úspěchu. Čím vyšší %, tím 'snažší' je se na školu dostat.\n\n"
                "🏛️ **Pro ředitele:** Ukazatel selektivity školy. Nízká čísla značí prestiž a velký převis.\n\n"
                "⚠️ **Poznámka:** Pokud reálná poptávka nepřekročila kapacitu, je úspěšnost **100 %***, protože každý, kdo splnil podmínky, mohl být přijat."
    },
    "Přijatí (celkem / průměr)": {
        "title": "Celkový počet přijatých a jejich průměrný bodový výsledek.",
        "desc": "🎯 **Pro uchazeče:** Představuje počet budoucích spolužáků a jejich průměrnou úroveň. Pokud jsem v testech nad touto hodnotou, jsem v 'klidové zóně'.\n\n"
                "🏛️ **Pro ředitele:** Ukazatel naplněnosti a kvality studijních předpokladů ročníku."
    },
    "Body posledního přijatého": {
        "title": "Skutečný výsledek uzavírající pořadí přijatých.",
        "desc": "🎯 **Pro uchazeče:** Klíčový bod pro odhad šance. Body pod touto hodnotou loni ke vstupu nestačily.\n\n"
                "🏛️ **Pro ředitele:** Ukazuje bodové dno ročníku. Stabilně nízká hodnota je varováním pro budoucí výsledky u maturit."
    },
    "Průměr horních 10 %": {
        "title": "Akademická úroveň nejlepších přijatých.",
        "desc": "🎯 **Pro uchazeče:** Ukazuje, jak vysoko jsou 'špičky' mezi přijatými. Motivace pro excelentní studenty.\n\n"
                "🏛️ **Pro ředitele:** Reprezentuje schopnost školy přitáhnout regionální talenty."
    },
    "Průměr spodních 25 %": {
        "title": "Bodová úroveň slabší čtvrtiny přijatých.",
        "desc": "🎯 **Pro uchazeče:** Ukazuje stabilitu 'konce' pole. Pokud jsem nad touto hodnotou, nejsem jen těsně nad hranou.\n\n"
                "🏛️ **Pro ředitele:** Indikuje, jak moc klesá kvalita na konci pořadníku. Čím blíž průměru, tím vyrovnanější třída."
    },
    "Bodový rozdíl (Gap)": {
        "title": "Rozdíl mezi průměrem vašich přijatých vs. těch, co odešli na vyšší priority.",
        "desc": "🎯 **Pro uchazeče:** Pro strategii nevýznamné.\n\n"
                "🏛️ **Pro ředitele:** Strategický ukazatel konkurenceschopnosti. Plusová hodnota znamená, že o kvalitnější žáky přicházíte ve prospěch jiných škol."
    },
    "Poptávka skalních zájemců (%)": {
        "title": "Podíl kapacity, kterou by naplnili nejvěrnější zájemci (volba č. 1).",
        "desc": "🎯 **Pro uchazeče:** Ukazuje, jak velkou část třídy tvoří 'srdcaři'. Čím vyšší %, tím silnější je komunita.\n\n"
                "🏛️ **Pro ředitele:** Ukazuje, kolik % kapacity dokáže škola naplnit bez ohledu na to, zda k ní někdo 'propadne' z jiných škol."
    },
    "Podíl skalních žáků (%)": {
        "title": "Podíl kapacity školy naplněný těmi, kteří zde chtěli nejvíce.",
        "desc": "🎯 **Pro uchazeče:** Ukazuje, z kolika procent bude třída tvořena lidmi, pro které byla škola první volbou.\n\n"
                "🏛️ **Pro ředitele:** Ukazatel loajality žáků. Čím vyšší, tím nižší riziko odchodu v průběhu studia."
    },
    "Podíl náhradních voleb (P3+) (%)": {
        "title": "Podíl kapacity školy naplněný žáky, pro které jsme byli 'záchranná brzda'.",
        "desc": "🎯 **Pro uchazeče:** Ukazuje, kolik spolužáků se na školu dostalo až jako na svou 3. a další prioritu.\n\n"
                "🏛️ **Pro ředitele:** Pomocný ukazatel pro marketing. Tito žáci u vás nekončí primárně z vlastní vůle."
    },
    "Intenzita odlivu (%)": {
        "title": "Procento uchazečů, kteří dali přednost jiné škole.",
        "desc": "🎯 **Pro uchazeče:** Ukazuje 'lákavost' konkurence. Pokud je číslo vysoké, škola je často vnímána jako druhá volba.\n\n"
                "🏛️ **Pro ředitele:** Klíčový ukazatel konkurenceschopnosti. Kolik % z těch, které jste chtěli, si nakonec vybralo jinou školu."
    },
    "Hustota u hranice": {
        "title": "Počet uchazečů v pásmu ±5 bodů od konce přijatých.",
        "desc": "🎯 **Pro uchazeče:** Míra rizika. Vysoké číslo znamená, že každý bod v testu rozhoduje o osudu desítek lidí.\n\n"
                "🏛️ **Pro ředitele:** Homogenita nebo 'nával'. Ukazuje, jak těsné jsou rozestupy mezi žáky na hraně."
    },
    "Kapacita": {
        "title": "Uchazeči, kteří uspěli, ale nevešli se.",
        "desc": "🎯 **Pro uchazeče:** Skupina, která 'ostrouhala' jen kvůli čáře. Pokud je zde vysoký průměr, byla konkurence extrémně tvrdá.\n\n"
                "🏛️ **Pro ředitele:** Potenciál pro navýšení kapacity. Jsou to žáci, které jste chtěli, ale nemohli přijmout."
    },
    "Vyšší priorita": {
        "title": "Uchazeči, kteří k vám byli přijati, ale nastoupili jinam.",
        "desc": "🎯 **Pro uchazeče:** Skupina, která mi reálně uvolnila místo.\n\n"
                "🏛️ **Pro ředitele:** Klíč k pochopení konkurence. Pokud tito lidé mají vysoký průměr, prohráváte boj o talenty."
    },
    "Nesplnili podmínky": {
        "title": "Uchazeči, kteří nezvládli zkoušku nebo kritéria.",
        "desc": "🎯 **Pro uchazeče:** Indikátor náročnosti. Pokud je zde mnoho lidí, jsou testy/kritéria nastavena přísně.\n\n"
                "🏛️ **Pro ředitele:** Adekvátnost nároků k úrovni populace, která se na školu hlásí."
    },
    "Plánovaná kapacita": {
        "title": "Počet míst nabízených školou do 1. kola.",
        "desc": "🎯 **Pro uchazeče:** Základní rozměr školy. Čím větší kapacita, tím širší je šance na přijetí.\n\n"
                "🏛️ **Pro ředitele:** Cílový stav pro naplnění rozpočtu a personálních kapacit."
    },
    "Míra naplněnosti (%)": {
        "title": "Poměr přijatých uchazečů k nabízené kapacitě.",
        "desc": "🎯 **Pro uchazeče:** Ukazuje, zda škola naplnila třídy. Nízké % znamená, že škola měla volná místa i po přijímačkách.\n\n"
                "🏛️ **Pro ředitele:** Nejdůležitější ukazatel efektivity náboru. Indikátor přežití školy v tržním prostředí."
    },
    "Volná místa": {
        "title": "Počet neobsazených míst po 1. kole.",
        "desc": "🎯 **Pro uchazeče:** Přímá informace o volné kapacitě pro případná další kola nebo odvolání.\n\n"
                "🏛️ **Pro ředitele:** Nevyužitý potenciál a varovný signál pro financování."
    },
    "Vzdali se přijetí": {
        "title": "Počet žáků, kteří byli přijati, ale rozhodli se nenastoupit.",
        "desc": "🎯 **Pro uchazeče:** Ukazuje, kolik lidí dalo přednost jiné škole. To uvolňuje místa pro náhradníky a další kola.\n\n"
                "🏛️ **Pro ředitele:** Ukazatel 'reálného zápisového lístku'. Vysoké číslo značí, že škola je často vnímána jako záložní varianta."
    },
    "Úspěšnost 1. priority (%)": {
        "title": "Šance pro ty, kteří školu preferují nejvíce.",
        "desc": "🎯 **Pro uchazeče:** Má šance, pokud si školu zvolím jako svou nejvyšší prioritu. Většinou vyšší než celková úspěšnost.\n\n"
                "🏛️ **Pro ředitele:** Ukazuje, jak škola plní očekávání svých nejvěrnějších zájemců."
    }
}

def inject_custom_css():
    """Custom CSS for a professional, 'Excel-inspired' compact look"""
    st.markdown("""
        <style>
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 0.5rem;
            padding-left: 1.5rem;
            padding-right: 1.5rem;
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
        
        /* Force wrapping in dataframes and headers */
        div[data-testid="stDataFrame"] thead th {
            white-space: pre-wrap !important;
            vertical-align: bottom !important;
        }
        div[data-testid="stDataFrame"] td {
            white-space: pre-wrap !important;
        }
        
        /* Grouped KPI section styling */
        .kpi-group-header {
            margin-top: 15px;
            margin-bottom: 5px;
            padding-left: 5px;
            border-left: 4px solid #1f77b4;
            font-weight: bold;
            color: #31333f;
        }
        </style>
        """, unsafe_allow_html=True)

def render_kpi_cards(kpi_data):
    """Renders expanded KPI cards grouped into logical blocks using central help dictionary"""
    
    def get_help(key):
        h = METRIC_HELP.get(key, {})
        return f"**{h.get('title', '')}**\n\n{h.get('desc', '')}"

    def fmt_struct(stats):
        if not stats: return " – "
        avg_str = f"{stats['avg_reg']:.1f}" if stats['avg_reg'] is not None else " – "
        total_cnt = stats['cnt_reg'] + stats.get('cnt_exc', 0)
        base = f"{total_cnt}"
        if stats.get('cnt_exc', 0) > 0:
            base += f" ({stats['cnt_exc']} ciz.)"
        base += f" / {avg_str}"
        return base

    # Block 1: Hlavní výsledky
    st.markdown('<div class="kpi-group-header">📊 HLAVNÍ VÝSLEDKY</div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    
    # Updated logic for unfilled schools (A.1.1 and A.1.2)
    is_unfilled = kpi_data['fullness_rate'] < 100
    
    # success_rate is now pre-calculated (display-ready) in analysis.py
    succ_val = f"{kpi_data['success_rate']:.1f} %"
    if kpi_data['success_rate'] == 100.0 and kpi_data['pure_demand_idx'] <= 1.0:
        succ_val = "100 %*"
        
    m1.metric("Celkový zájem (přihlášky)", kpi_data['total_apps'], help=get_help("Celkový zájem (přihlášky)"))
    m2.metric("Index převisu", f"{kpi_data['comp_idx']:.2f}x", help=get_help("Index převisu"))
    m3.metric("Index reálné poptávky", f"{kpi_data['pure_demand_idx']:.2f}x", help=get_help("Index reálné poptávky"))
    m4.metric("Celková úspěšnost (%)", succ_val, help=get_help("Celková úspěšnost (%)"))

    # Block 2: Bodová úroveň
    st.markdown('<div class="kpi-group-header">📈 BODOVÁ ÚROVEŇ</div>', unsafe_allow_html=True)
    q1, q2, q3, q4, q5 = st.columns(5)
    
    # Updated to use structured data if available
    adm_struct = kpi_data.get('avg_admitted_struct')
    q1.metric("Přijatí (celkem / průměr)", fmt_struct(adm_struct) if adm_struct else (f"{kpi_data['avg_admitted']:.1f} b." if kpi_data['avg_admitted'] else "-"), help=get_help("Přijatí (celkem / průměr)"))
    
    q2.metric("Body posledního přijatého", f"{kpi_data['min_score']:.1f} b." if kpi_data['min_score'] else "-", help=get_help("Body posledního přijatého"))
    q3.metric("Průměr horních 10 %", f"{kpi_data['elite_avg']:.1f} b." if kpi_data['elite_avg'] else "-", help=get_help("Průměr horních 10 %"))
    q4.metric("Průměr spodních 25 %", f"{kpi_data['bottom_25_avg']:.1f} b." if kpi_data['bottom_25_avg'] else "-", help=get_help("Průměr spodních 25 %"))
    q5.metric("Bodový rozdíl (Gap)", f"+{kpi_data['talent_gap']:.1f} b." if kpi_data['talent_gap'] > 0 else f"{kpi_data['talent_gap']:.1f} b.", help=get_help("Bodový rozdíl (Gap)"))

    # Block 3: Strategické ukazatele
    st.markdown('<div class="kpi-group-header">🎯 STRATEGICKÉ UKAZATELE (PRIORITY A MOTIVACE)</div>', unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    
    s1.metric("Poptávka skalních zájemců (%)", f"{kpi_data['interest_p1_pct']:.1f} %", help=get_help("Poptávka skalních zájemců (%)"))
    s2.metric("Podíl skalních žáků (%)", f"{kpi_data['intake_p1_pct']:.1f} %", help=get_help("Podíl skalních žáků (%)"))
    s3.metric("Podíl náhradních voleb (P3+) (%)", f"{kpi_data['intake_p3p_pct']:.1f} %", help=get_help("Podíl náhradních voleb (P3+) (%)"))
    s4.metric("Intenzita odlivu (%)", f"{kpi_data['release_rate']:.1f} %", help=get_help("Intenzita odlivu (%)"))

    # Block 4: Analýza nepřijatých
    st.markdown('<div class="kpi-group-header">❌ ANALÝZA NEPŘIJATÝCH (POČET / PRŮMĚR)</div>', unsafe_allow_html=True)
    r1, r2, r3, r4 = st.columns(4)
    
    # Use structured stats for rejection analysis
    r1.metric("Kapacita (přeliv)", fmt_struct(kpi_data.get('cap_stats')), help=get_help("Kapacita"))
    r2.metric("Vyšší priorita", fmt_struct(kpi_data.get('lost_stats')), help=get_help("Vyšší priorita"))
    r3.metric("Nesplnili podmínky", fmt_struct(kpi_data.get('fail_stats')), help=get_help("Nesplnili podmínky"))
    
    dens_val = kpi_data['boundary_density'] if kpi_data['boundary_density'] is not None else " – "
    r4.metric("Hustota u hranice", dens_val, help=get_help("Hustota u hranice"))

    # Block 5: Kapacitní analýza (SYSTÉMOVÁ)
    st.markdown('<div class="kpi-group-header">🏢 KAPACITNÍ ANALÝZA (SYSTÉMOVÁ)</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    
    cap_val = kpi_data.get('planned_capacity')
    c1.metric("Plánovaná kapacita", str(cap_val) if cap_val is not None else "-", help=get_help("Plánovaná kapacita"))
    full_val = f"{kpi_data['fullness_rate']:.1f} %"
    if is_unfilled:
        full_val = f"⚠️ {full_val}"

    c2.metric("Míra naplněnosti (%)", full_val, help=get_help("Míra naplněnosti (%)"))
    c3.metric("Volná místa", kpi_data['vacant_seats'], help=get_help("Volná místa"))
    c4.metric("Vzdali se přijetí", kpi_data['gave_up_count'], help=get_help("Vzdali se přijetí"))
    c5.metric("Úspěšnost 1. priority (%)", f"{kpi_data['p1_loyalty']:.1f} %", help=get_help("Úspěšnost 1. priority (%)"))

