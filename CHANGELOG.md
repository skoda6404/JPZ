# Changelog

Všechny významné změny v projektu JPZ budou zaznamenány v tomto souboru.

## [3.0.0] - 2026-02-14

### Přidáno

- **Prémiové overlay grafy**: U metrik *Průměr spodních 25 %* a *Index reálné poptávky* se nyní zobrazuje referenční průhledný sloupec (celkový průměr / celkový převis) s přesně umístěným popiskem Δ Delta v mezeře.
- **Index reálné poptávky**: Nový vzorec `(Přijatí + Odmítnutí z kapacity) / Kapacita`. Eliminuje zkreslení u prázdných škol.
- **Strategické KPI**: Nové metriky: *Poptávka skalních zájemců (%)*, *Podíl skalních žáků (%)*, *Intenzita odlivu (%)*, *Podíl náhradních voleb (P3+) (%)*.
- **Varování u nenaplněných škol**: Automatické banery a vizuální upozornění (`⚠️`) u škol s volnou kapacitou.
- **Inteligentní 100% úspěšnost**: Automatická detekce „nenaplněné" školy s hvězdičkou a vysvětlením.
- **Filtr oborů v detailu školy**: Multiselect pro analýzu jednotlivých oborů (KKOV).
- **Uložení/načtení výběru**: Export a import seznamu škol jako JSON.
- **Absolutní počty v grafech priorit**: Popisky nyní zobrazují procenta i absolutní čísla (např. *42 % (150 přihlášek)*).
- **Komplexní nápověda**: Každá KPI metrika obsahuje interaktivní nápovědu pro uchazeče i ředitele.
- **Architektonická dokumentace**: Nový soubor `ARCHITECTURE.md` s popisem datového toku a modulů.

### Změněno

- **Sjednocení výšek grafů**: Všechny srovnávací grafy mají konzistentní kompaktní výšku (35 px na řádek).
- **Formát indexů**: *Index převisu* a *Index reálné poptávky* jsou zobrazeny jako desetinná čísla (1.50) místo procent.
- **Odstranění redundantních legend**: Legendy škol ve srovnávacích grafech byly odebrány (školy jsou identifikovány na ose Y).
- **Centralizace výpočtů**: Veškerá KPI logika je nyní v `src/analysis.py`.
- **Přejmenování metrik**: Intuitivnější české názvy strategických ukazatelů.
- **Zjednodušení výpočtu volných míst**: `Kapacita − Přijatí` (bez dalších úprav).

### Opraveno

- **ValueError (Plotly)**: Odstraněna nekompatibilní vlastnost `dash` u bar markerů.
- **NameError (app.py)**: Opravena reference na neexistující proměnnou `selected_metric`.
- **Načítání výběru škol**: Vyřešena chyba StreamlitAPIException při načítání JSON výběrů.
- **Nápověda „Průměr horních 10 %"**: Opraveno z „uchazečů" na „přijatých".

---

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

---

## [1.2.0] - 2026-02-02

### Přidáno

- **Mapování KKOV**: Automatické zobrazení názvů oborů (např. "Gymnázium (8leté)") místo kódů.
- **Skript pro extrakci**: Přidán skript `extract_kkov.py` pro zpracování PDF seznamu oborů.
- **Plné názvy škol**: Filtr zobrazuje úplný název školy dle rejstříku.

### Změněno

- **Filtrování**: Vylepšená navigace s čitelnými názvy oborů a škol.

---

## [1.1.0] - 2026-01-21

### Přidáno

- **Sloupec „Celkem přihlášek"**: Celkový počet uchazečů v tabulce statistik.
- **Sloupec „Poslední přijatý"**: Minimální bodový zisk přijatého uchazeče.
- **Kompaktní zobrazení**: Sloučení počtu a průměru do jedné buňky.
- **Lokalizace**: České popisky ve filtrovacích polích.

### Změněno

- **Přejmenování** aplikace na „JPZ".
- **Design**: Vylepšené formátování tabulky statistik.

---

## [1.0.0] - 2026-01-21

### Přidáno

- Úvodní verze aplikace.
- Vizualizace pomocí Plotly.
- Základní statistiky a filtrování dat.
