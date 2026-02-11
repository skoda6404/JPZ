# Changelog

Všechny významné změny v projektu JPZ budou zaznamenány v tomto souboru.

## [2.0.0] - 2026-02-11

### Přidáno

- **Detailní rozbor školy**: Kompletní analytický dashboard pro jednotlivé školy.
- **KPI karty**: 6 klíčových metrik — přihlášky, úspěšnost, index přetlaku, kapacitní odmítnutí, P1 věrnost, kvalita ztracených.
- **Analýza přelivu**: 3 kategorie vizualizace kam odešli nepřijatí studenti (vyšší priorita, kapacita, nesplnění podmínek).
- **Popisky přelivu**: Detailní formát „Škola (Obor)" u cílových škol.
- **Koláčový graf důvodů nepřijetí**: Procentuální zastoupení důvodů nepřijetí.
- **Srovnání priorit**: Dva sloupcové grafy (%) — priority přihlášek vs. priority přijatých.
- **Graf rozložení bodů**: Bodový graf přijatých uchazečů přímo v detailu školy.
- **Navigace proklikem**: Kliknutí na řádek tabulky otevře detail školy.
- **Tlačítko "Zpět na srovnání"**: S automatickým zapamatováním výběru škol a oborů.
- **Export do PDF a CSV**: Stažení reportu přímo z detailu školy.
- **Srovnání kvality**: Průměrné body přijatých vs. ztracených uchazečů.
- **Index čistého převisu**: Výpočet vhodných uchazečů na 1 volné místo.

### Změněno

- **Synchronizované osy**: Všechny grafy přelivu sdílejí stejné měřítko osy X.
- **Dynamická výška grafů**: Automatická úprava výšky dle počtu položek.
- **Číselné popisky**: Počty žáků zobrazeny přímo u sloupců grafů.
- **Robustní navigace**: Přepracovaný systém navigace pomocí pending flags.
- **Konzistentní RED_IZO**: Normalizace RED_IZO kódů jako stringů.
- **Správné filtrování nepřijatých**: Podpora `Prijat != 1` pro kompatibilitu napříč ročníky.
- **Automargin**: Plotly automaticky vypočítá prostor pro popisky.

### Opraveno

- **StreamlitAPIException**: Odstraněny chyby při navigaci mezi pohledy.
- **Prázdné grafy přelivu**: Opraveno mapování studentů pomocí Student_UUID.
- **Překrývání textu**: Opraveno renderování grafů s malým počtem položek.

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
