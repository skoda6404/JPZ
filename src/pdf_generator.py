from fpdf import FPDF
from .utils import clean_pdf_text

def create_pdf_report(school_name, year, rounds, stats_df, kpi_data):
    pdf = FPDF()
    pdf.add_page()
    # fpdf2 supports some unicode if we use built-in core fonts, but for Czech TTF is best.
    # We will use "helvetica" and clean text
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, clean_pdf_text(f"Detailni report: {school_name}"), ln=True, align="C")
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 10, clean_pdf_text(f"Rok: {year} | Kola: {', '.join(map(str, rounds))}"), ln=True, align="C")
    pdf.ln(10)
    
    # KPIs Block 1
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, clean_pdf_text("Klicove metriky skoly:"), ln=True)
    pdf.set_font("helvetica", "", 11)
    pdf.cell(60, 8, clean_pdf_text(f"Prihlasek: {kpi_data['total_apps']}"))
    pdf.cell(60, 8, clean_pdf_text(f"Uspesnost: {kpi_data.get('success_rate', 0):.1f}%"))
    pdf.cell(60, 8, clean_pdf_text(f"Pretlak: {kpi_data.get('comp_idx', 0):.2f}x"))
    pdf.ln(8)
    pdf.cell(60, 8, clean_pdf_text(f"Kapacita (přeliv): {kpi_data.get('cap_count', 0)}"))
    pdf.cell(60, 8, clean_pdf_text(f"Uspesnost P1: {kpi_data.get('p1_loyalty', 0):.1f}%"))
    pdf.cell(60, 8, clean_pdf_text(f"Ztracene talenty (Gap): {kpi_data.get('talent_gap', 0):+.1f} b."))
    pdf.ln(8)
    
    # KPIs Block 2 (New)
    pdf.cell(60, 8, clean_pdf_text(f"Naplnenost: {kpi_data.get('fullness_rate', 0):.1f}%"))
    pdf.cell(60, 8, clean_pdf_text(f"Volna mista: {kpi_data.get('vacant_seats', 0)}"))
    pdf.cell(60, 8, clean_pdf_text(f"Vzdali se: {kpi_data.get('gave_up_count', 0)}"))
    pdf.ln(15)
    
    # Table Header (Updated to match app.py)
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("helvetica", "B", 8)
    cols = ["Obor", "Kapacita", "Prihl.", "Prijato (celkem / prumer)", "Min. body", "Vyssi priorita"]
    w = [60, 15, 15, 45, 20, 35]
    for i, col in enumerate(cols):
        pdf.cell(w[i], 10, clean_pdf_text(col), 1, 0, "C", True)
    pdf.ln()
    
    # Table Data
    pdf.set_font("helvetica", "", 8)
    for _, row in stats_df.iterrows():
        field = clean_pdf_text(str(row['Obor']))[:40]
        pdf.cell(w[0], 8, field, 1)
        pdf.cell(w[1], 8, str(row.get('Kapacita', '-')), 1, 0, "C")
        pdf.cell(w[2], 8, str(row.get('Přihlášky', '-')), 1, 0, "C")
        pdf.cell(w[3], 8, clean_pdf_text(str(row.get('Přijato', '-'))), 1, 0, "C")
        pdf.cell(w[4], 8, str(row.get('Min. bodů', '-')), 1, 0, "C")
        pdf.cell(w[5], 8, clean_pdf_text(str(row.get('Vyšší priorita', '-'))), 1, 0, "C")
        pdf.ln()
    return bytes(pdf.output())
