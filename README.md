# JPZ - Analýza přijímacích zkoušek

Interaktivní aplikace pro vizualizaci a analytiku výsledků jednotných přijímacích zkoušek (JPZ). Nástroj je určen pro ředitele škol a pedagogy a umožňuje hloubkovou analýzu přijímacího řízení včetně porovnání škol, detailního rozboru jednotlivých škol a sledování „přelivu" studentů.

## 🚀 Hlavní funkce

### Srovnání škol

- **Interaktivní grafy**: Zobrazení bodového zisku přijatých uchazečů v závislosti na pořadí, s barevným rozlišením škol a oborů.
- **Odlišení cizinců**: Speciální značky (×) pro uchazeče s odpuštěnou zkouškou z ČJL.
- **Kompaktní tabulka**: Pivot tabulka s metrikami — počet uchazečů, průměrný bodový zisk, rozpad dle důvodu přijetí/nepřijetí.
- **Navigace proklikem**: Kliknutím na řádek v tabulce přejdete na detailní rozbor školy.

### Detailní rozbor školy

- **KPI karty**: 6 klíčových ukazatelů — počet přihlášek, úspěšnost přijetí, index přetlaku, kapacitní odmítnutí, úspěšnost 1. priority, kvalita ztracených.
- **Rozložení bodů**: Graf bodového zisku přijatých s možností porovnání s konkurencí.
- **Analýza priorit**: Dva sloupcové grafy (procentuální) — priority všech přihlášek vs. priority přijatých.
- **Koláčový graf důvodů nepřijetí**: Vizuální přehled proč nebyli uchazeči přijati.
- **Analýza přelivu** (3 kategorie):
  - A) Přijati na vyšší prioritu — kam odešli studenti, kteří měli školu na nižší prioritě.
  - B) Nepřijati z kapacitních důvodů — kam byli přijati ti, pro které nebylo místo.
  - C) Nesplnili podmínky — kam byli přijati ti, kteří neprospěli u zkoušky.
- **Srovnání kvality**: Průměrné body přijatých vs. ztracených uchazečů.
- **Export**: Download dat jako CSV nebo PDF report.
- **Navigace zpět**: Tlačítko „Zpět na srovnání" se zapamatováním výběru škol.

### Obecné

- **Podpora více let**: Přepínání mezi výsledky ročníků 2024, 2025.
- **Filtrování dle kola**: Výběr 1. nebo 2. kola zkoušky.
- **Filtrování dle ročníku**: Oddělené statistiky pro 5., 7. a 9. třídu.

## 🛠️ Instalace a spuštění

### Lokálně

1. **Naklonujte repozitář**:

    ```bash
    git clone https://github.com/skoda6404/JPZ.git
    cd JPZ
    ```

2. **Nainstalujte závislosti**:

    ```bash
    pip install -r requirements.txt
    ```

3. **Spusťte aplikaci**:

    ```bash
    streamlit run app.py
    ```

### Windows (dvojklik)

Spusťte `run_app.bat` — automaticky nainstaluje závislosti a otevře aplikaci v prohlížeči.

### Streamlit Cloud

Aplikace je optimalizovaná pro běh na [Streamlit Community Cloud](https://streamlit.io/cloud).

1. Forkněte si tento repozitář.
2. Přihlašte se na Streamlit Cloud.
3. Vytvořte novou aplikaci a vyberte tento repozitář.
4. Jako hlavní soubor zvolte `app.py`.

## 📂 Struktura projektu

| Soubor | Popis |
|--------|-------|
| `app.py` | Hlavní aplikace (Streamlit) |
| `requirements.txt` | Python závislosti |
| `run_app.bat` | Windows spouštěč |
| `skoly.csv` | Rejstřík škol (mapování RED_IZO → název) |
| `kkov_map.json` | Mapování KKOV kódů na názvy oborů |
| `extract_kkov.py` | Skript pro extrakci KKOV z PDF |
| `PZ{ROK}_kolo{X}_*.xlsx` | Datové soubory s výsledky zkoušek |

## 📊 Požadavky na data

Aplikace očekává Excel soubory s názvy ve formátu `PZ{ROK}_kolo{CISLO}_*.xlsx` obsahující sloupce:

- `ss{1-5}_redizo` — RED_IZO kódy škol
- `ss{1-5}_kkov` — KKOV kódy oborů
- `ss{1-5}_prijat` — status přijetí (1 = přijat)
- `ss{1-5}_duvod_neprijeti` — důvod nepřijetí
- `c_procentni_skor`, `m_procentni_skor` — bodové výsledky

## 🔧 Technologie

- **Python 3.12+**
- **Streamlit** — UI framework
- **Pandas** — zpracování dat
- **Plotly** — interaktivní grafy
- **FPDF2** — generování PDF reportů

## 📄 Licence

Tento projekt je licencován pod licencí MIT — viz soubor [LICENSE](LICENSE).
