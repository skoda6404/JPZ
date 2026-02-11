import pdfplumber

pdf_path = 'seznam_jednotlivych_oboru_vzdelani_a_skupin_oboru_vzdelani.pdf'

with pdfplumber.open(pdf_path) as pdf:
    if len(pdf.pages) > 0:
        first_page = pdf.pages[0]
        text = first_page.extract_text()
        print("--- FIRST PAGE TEXT ---")
        print(text)
        print("-----------------------")
    else:
        print("PDF is empty")
