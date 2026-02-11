import pdfplumber

pdf_path = 'seznam_jednotlivych_oboru_vzdelani_a_skupin_oboru_vzdelani.pdf'

with pdfplumber.open(pdf_path) as pdf:
    with open('debug_extract.txt', 'w', encoding='utf-8') as f:
        if len(pdf.pages) > 0:
            first_page = pdf.pages[0]
            text = first_page.extract_text()
            f.write(text)
