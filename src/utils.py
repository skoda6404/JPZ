import re

def clean_pdf_text(text):
    """Simple ASCII transliteration for PDF fonts that don't support Unicode"""
    if not isinstance(text, str): return str(text)
    trans = {
        'á': 'a', 'č': 'c', 'ď': 'd', 'é': 'e', 'ě': 'e', 'í': 'i', 'ň': 'n', 'ó': 'o', 'ř': 'r', 'š': 's', 'ť': 't', 'ú': 'u', 'ů': 'u', 'ý': 'y', 'ž': 'z',
        'Á': 'A', 'Č': 'C', 'Ď': 'D', 'É': 'E', 'Ě': 'E', 'Í': 'I', 'Ň': 'N', 'Ó': 'O', 'Ř': 'R', 'Š': 'S', 'Ť': 'T', 'Ú': 'U', 'Ů': 'U', 'Ý': 'Y', 'Ž': 'Z'
    }
    for k, v in trans.items():
        text = text.replace(k, v)
    return text

def get_grade_level(kkov):
    """Identifies grade based on KKOV code (8-year, 6-year, 4-year)"""
    k = str(kkov)
    if k.endswith('/81'): return "5. (8leté)"
    if k.endswith('/61'): return "7. (6leté)"
    return "9. (4leté/obory)"

def clean_col_name(col):
    """Strip non-ascii characters and normalize case"""
    s = "".join([c if ord(c) < 128 else "" for c in str(col)])
    return s.strip().lower()

reason_map = {
    "prijat_na_vyssi_prioritu": "Přijat na vyšší prioritu",
    "neprijat_pro_nedostatecnou_kapacitu": "Kapacita",
    "pro_nedostacujici_kapacitu": "Kapacita",
    "neprijat_pro_nesplneni_podminek": "Nesplnil podmínky",
    "pro_nesplneni_podminek": "Nesplnil podmínky",
    "vzdal_se_u_nas": "Vzdal se (u nás)",
    "vzdal_se": "Vzdal se (u nás)",
    "Neuvedeno": "Neuvedeno"
}

def get_reason_label(reason):
    return reason_map.get(reason, reason)
