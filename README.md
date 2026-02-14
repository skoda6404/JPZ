# JPZ – Analýza přijímacích zkoušek

Interaktivní aplikace pro vizualizaci a analytiku výsledků **jednotných přijímacích zkoušek (JPZ)**. Nástroj je určen pro ředitele škol, pedagogy a uchazeče. Umožňuje hloubkovou analýzu přijímacího řízení, porovnání škol a sledování přelivu studentů.

---

## 🚀 Hlavní funkce

### 1. Srovnání škol
- **Srovnávací grafy**: Horizontální sloupcové grafy (bar chart) pro libovolné metriky — od indexu převisu po bodový průměr.
- **Overlay zobrazení**: U metrik *Průměr spodních 25 %* a *Index reálné poptávky* se zobrazuje referenční průhledný sloupec s deltou (Δ) pro okamžité porovnání s celkovým průměrem / celkovým převisem.
- **Kompaktní tabulka**: Pivot tabulka s metrikami — počet uchazečů, bodový zisk, rozpad dle důvodu přijetí/nepřijetí.
- **Navigace proklikem**: Kliknutím na řádek v tabulce přejdete na detailní rozbor školy.

### 2. Detailní rozbor školy
- **KPI karty** (4 bloky): Hlavní výsledky, bodová úroveň, strategické ukazatele, kapacitní analýza. Každá karta obsahuje nápovědu s vysvětlením metriky pro uchazeče i ředitele.
- **Rozložení bodů**: Bodový graf přijatých s možností porovnání s konkurencí (percentily / pořadí).
- **Analýza priorit**: Dva sloupcové grafy — priority všech přihlášek vs. priority přijatých s absolutními počty.
- **Koláčový graf důvodů nepřijetí**: Vizuální přehled proč nebyli uchazeči přijati.
- **Analýza přelivu** (3 kategorie):
  - A) Přijati na vyšší prioritu — kam odešli studenti, kteří měli školu na nižší prioritě.
  - B) Nepřijati z kapacitních důvodů — kam byli přijati ti, pro které nebylo místo.
  - C) Nesplnili podmínky — kam byli přijati ti, kteří neprospěli u zkoušky.
- **Export**: Download dat jako CSV nebo PDF report.

### 3. Obecné
- **Podpora více let**: Přepínání mezi ročníky (2024, 2025, …).
- **Filtrování dle kola**: Výběr 1. nebo 2. kola, nebo obou.
- **Filtrování dle ročníku**: Statistiky pro 5., 7. a 9. třídu.
- **Uložení/načtení výběru**: Export/import seznamu škol jako JSON.
- **Inteligentní nápověda**: Každá metrika má ikonu (?) s vysvětlením jak pro uchazeče, tak pro ředitele.

---

## 🛠️ Instalace a spuštění

### Požadavky
- **Python 3.12+**
- Závislosti: viz `requirements.txt`

### Lokálně (příkazový řádek)

```bash
# 1. Naklonujte repozitář
git clone https://github.com/skoda6404/JPZ.git
cd JPZ

# 2. Nainstalujte závislosti
pip install -r requirements.txt

# 3. Spusťte aplikaci
streamlit run app.py
```

### Windows (dvojklik)

Spusťte `run_app.bat` — automaticky nainstaluje závislosti a otevře aplikaci v prohlížeči.

### Streamlit Cloud

1. Forkněte repozitář.
2. Přihlašte se na [Streamlit Community Cloud](https://streamlit.io/cloud).
3. Vytvořte novou aplikaci a vyberte tento repozitář.
4. Jako hlavní soubor zvolte `app.py`.

---

## 📂 Struktura projektu

```
JPZ/
├── app.py                      # Hlavní aplikace (Streamlit)
├── src/
│   ├── analysis.py             # Výpočet KPI metrik (calculate_kpis)
│   ├── data_loader.py          # Načítání dat z XLSX a CSV
│   ├── ui_components.py        # KPI karty, CSS, nápověda (METRIC_HELP)
│   ├── pdf_generator.py        # Generování PDF reportů
│   ├── storage.py              # Ukládání/načítání oblíbených výběrů
│   └── utils.py                # Pomocné funkce (transliterace, KKOV, důvody)
├── kkov_map.json               # Mapování KKOV → nombre oboru
├── kkov_groups.json            # Seskupení KKOV oborů
├── skoly.csv                   # Rejstřík škol (REDIZO, IZO → název)
├── PZ{ROK}_kolo{X}_*.xlsx      # Datové soubory Cermat
├── requirements.txt            # Python závislosti
├── run_app.bat                 # Windows spouštěč
├── CHANGELOG.md                # Historie změn
├── ARCHITECTURE.md             # Technická architektura
├── CONTRIBUTING.md             # Pokyny pro přispěvatele
└── LICENSE                     # MIT licence
```

---

## 📊 Požadavky na data

Aplikace očekává Excel soubory s názvy ve formátu `PZ{ROK}_kolo{ČÍSLO}_*.xlsx`:

| Soubor | Obsah |
|--------|-------|
| `*_uchazeci_prihlasky_vysledky.xlsx` | Individuální data uchazečů (5 přihlášek, bodové výsledky, důvody) |
| `*_skolobory_kapacity.xlsx` | Plánované kapacity škol/oborů |

Klíčové sloupce: `ss{1-5}_redizo`, `ss{1-5}_kkov`, `ss{1-5}_prijat`, `ss{1-5}_duvod_neprijeti`, `c_procentni_skor`, `m_procentni_skor`.

---

## 🔧 Technologie

| Technologie | Použití |
|-------------|---------|
| **Streamlit** | UI framework |
| **Pandas** | Zpracování dat |
| **Plotly** | Interaktivní grafy |
| **FPDF2** | Generování PDF |
| **OpenPyXL** | Čtení Excel souborů |
| **PDFPlumber** | Extrakce dat z PDF |

---

## 📚 Dokumentace

- **[CHANGELOG.md](CHANGELOG.md)** — Historie všech verzí a změn
- **[ARCHITECTURE.md](ARCHITECTURE.md)** — Technická architektura, datový tok, klíčové koncepty
- **[CONTRIBUTING.md](CONTRIBUTING.md)** — Pokyny pro vývojáře a pravidla pro Git workflow

---

## 📄 Licence

Tento projekt je licencován pod licencí MIT — viz soubor [LICENSE](LICENSE).
