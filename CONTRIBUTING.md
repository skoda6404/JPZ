# Pokyny pro přispěvatele (Contributing Guide)

## Git workflow

Projekt používá dvě hlavní větve:

| Větev | Účel |
|-------|------|
| `main` | **Produkční** větev. Stabilní, odladěná verze aplikace. |
| `dev` | **Vývojová** větev. Probíhající práce, nové funkce, experimenty. |

### Pravidla

1. **Vývoj probíhá vždy v `dev`** (nebo ve feature větvi z `dev`).
2. **Nikdy nepushujte přímo do `main`**.
3. **Merge do `main`** se provádí pouze po schválení (review):
   ```bash
   git checkout main
   git merge dev --no-ff -m "Release vX.Y.Z: popis změn"
   git push origin main
   ```
4. **Po merge** se vrátíte na `dev` pro další vývoj:
   ```bash
   git checkout dev
   ```

---

## Jak přidat novou metriku

1. **Výpočet**: Přidejte výpočet do `src/analysis.py` → funkce `calculate_kpis()`.
2. **Nápověda**: Přidejte klíč do `METRIC_HELP` v `src/ui_components.py`.
3. **KPI karta**: Přidejte řádek do `render_kpi_cards()` v `src/ui_components.py`.
4. **Srovnání**: Přidejte klíč do `comparable_metrics` v `app.py`.
5. **PDF**: Aktualizujte `create_pdf_report()` v `src/pdf_generator.py`.

---

## Jak přidat nový rok dat

1. Umístěte soubory `PZ{ROK}_kolo{X}_*.xlsx` do kořenového adresáře projektu.
2. Aplikace automaticky detekuje nový rok a nabídne ho v UI.

---

## Konvence kódu

- **Jazyk**: Python 3.12+ s type hints kde je to užitečné.
- **UI texty**: Česky.
- **Komentáře v kódu**: Anglicky.
- **Commit messages**: Formát `Tag (branch): Description`, např. `Feature (dev): Added new metric`.
- **Formátování**: PEP 8, pragmaticky.

---

## Testování

```bash
# Spuštění sanity checku (globální kontrola dat)
python sanity_check.py

# Debug specifické školy
python debug_upice.py
```

---

## Zálohy

Před každým releasem se doporučuje vytvořit ZIP zálohu:

```bash
# PowerShell
Compress-Archive -Path .\* -DestinationPath "JPZ_backup_$(Get-Date -Format yyyyMMdd).zip" -Force
```
