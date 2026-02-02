# Changelog

Všechny významné změny v projektu JPZ budou zaznamenány v tomto souboru.

## [1.2.0] - 2026-02-02

### Přidáno

- **Mapování KKOV**: Aplikace nyní automaticky zobrazuje názvy oborů (např. "Gymnázium (8leté)") místo pouhých kódů.
- **Skript pro extrakci**: Přidán skript `extract_kkov.py` pro zpracování PDF seznamu oborů.
- **Plné názvy škol**: Filtr škol nyní zobrazuje úplný název školy dle rejstříku (podle souboru `skoly.csv`).

### Změněno

- **Filtrování**: Vylepšená navigace výběrem škol a oborů s čitelnými názvy.

## [1.1.0] - 2026-01-21

### Přidáno

- **Sloupec "Celkem přihlášek"**: Do tabulky statistik přidán celkový počet uchazečů.
- **Sloupec "Poslední přijatý"**: Zobrazení minimálního bodového zisku přijatého uchazeče (bez zahrnutí cizinců s úlevou).
- **Kompaktní zobrazení**: Sloučení počtu a průměru do jedné buňky (např. "60 / 58.3").
- **Lokalizace**: České popisky ve filtrovacích polích ("Vyberte...").

### Změněno

- **Přejmenování**: Aplikace přejmenována na "JPZ".
- **Design**: Vylepšené formátování tabulky statistik (barevné písmo podle školy).
- **Opravy**: Návrat omylem smazaného kódu pro načítání dat.

## [1.0.0] - 2026-01-21

### Přidáno

- Úvodní verze aplikace.
- Vizualizace pomocí Plotly.
- Základní statistiky a filtrování dat.
