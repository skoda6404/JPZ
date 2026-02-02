import pdfplumber
import re
import json

pdf_path = 'seznam_jednotlivych_oboru_vzdelani_a_skupin_oboru_vzdelani.pdf'
output_map_path = 'kkov_map.json'
output_groups_path = 'kkov_groups.json'

mapping = {}
groups = {}

# Regex for KKOV code: e.g. 16-01-M/01 -> Field
pattern_field = re.compile(r'^\s*(\d{2}-\d{2}-[A-Z]/\d{2})\s+(.+)$')
# Regex for Group: e.g. 16 Ekologie... -> Group
pattern_group = re.compile(r'^\s*(\d{2})\s+(.+)$')

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if not text: continue
        
        for line in text.split('\n'):
            # Check for Field
            match_field = pattern_field.match(line)
            if match_field:
                code = match_field.group(1).strip()
                name = match_field.group(2).strip()
                mapping[code] = name
                continue
            
            # Check for Group
            match_group = pattern_group.match(line)
            if match_group:
                grp_code = match_group.group(1).strip()
                grp_name = match_group.group(2).strip()
                groups[grp_code] = grp_name

print(f"Extracted {len(mapping)} fields and {len(groups)} groups.")

with open(output_map_path, 'w', encoding='utf-8') as f:
    json.dump(mapping, f, ensure_ascii=False, indent=4)

with open(output_groups_path, 'w', encoding='utf-8') as f:
    json.dump(groups, f, ensure_ascii=False, indent=4)
