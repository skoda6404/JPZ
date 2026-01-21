# JPZ - Analýza přijímacích zkoušek

Aplikace pro vizualizaci a analýzu výsledků přijímacích zkoušek (JPZ). Nástroj umožňuje filtrovat data podle roku, kola zkoušky, školy a oboru a zobrazit přehledné statistiky o přijatých a nepřijatých uchazečích.

## 🚀 Funkce
- **Interaktivní grafy**: Zobrazení bodového zisku uchazečů v závislosti na pořadí.
- **Odlišení skupin**: Barevné rozlišení škol a oborů, speciální značky pro uchazeče s odpuštěnou zkouškou z ČJL.
- **Detailní statistiky**: 
    - Pivot tabulka pro každou školu a obor.
    - Metriky: Počet uchazečů, průměrný bodový zisk, min. body posledního přijatého.
    - Rozpad podle důvodu přijetí/nepřijetí (Kapacita, Nesplnění podmínek atd.).
- **Podpora pro více let**: Snadné přepínání mezi výsledky ročníků 2024, 2025 atd.

## 🛠️ Instalace a spuštění (Lokálně)

1.  **Naklonujte repozitář**:
    ```bash
    git clone https://github.com/skoda6404/JPZ.git
    cd JPZ
    ```

2.  **Nainstalujte závislosti**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Spusťte aplikaci**:
    ```bash
    streamlit run app.py
    ```

## ☁️ Spuštění na Streamlit Cloud
Tato aplikace je optimalizovaná pro běh na [Streamlit Community Cloud](https://streamlit.io/cloud).

1.  Forkněte si tento repozitář.
2.  Přihlašte se na Streamlit Cloud.
3.  Vytvořte novou aplikaci a vyberte tento repozitář.
4.  Jako hlavní soubor zvolte `app.py`.

## 📂 Struktura dat
Aplikace očekává Excel soubory v kořenovém adresáři s názvy ve formátu `PZ{ROK}_kolo{CISLO}_*.xlsx`. Dále vyžaduje soubor `skoly.csv` pro mapování názvů škol.

## 📄 Licence
Tento projekt je licensován pod licencí MIT - viz soubor [LICENSE](LICENSE) pro detaily.
