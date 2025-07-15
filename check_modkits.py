# You can save this as check_modkits.py and run it from your project root.
import os
import re
from collections import defaultdict

root_dir = r'd:\Fivem Server\Blue-Box'
output_file = 'modkits_report.txt'

modkit_pattern = re.compile(r'<Kits>.*?<id\s+value="(\d+)"\s*/>', re.DOTALL)
siren_pattern = re.compile(r'<Sirens>.*?<id\s+value="(\d+)"\s*/>', re.DOTALL)
light_pattern = re.compile(r'<Lights>.*?<id\s+value="(\d+)"\s*/>', re.DOTALL)

modkits = defaultdict(list)
sirens = defaultdict(list)
lights = defaultdict(list)

# Walk through all files in the directory
for subdir, _, files in os.walk(root_dir):
    for file in files:
        if file == 'carcols.meta':
            filepath = os.path.join(subdir, file)
            folder = os.path.basename(os.path.dirname(filepath))
            with open(filepath, encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Modkit IDs
                for match in modkit_pattern.finditer(content):
                    modkit_id = match.group(1)
                    modkits[modkit_id].append(folder)
                # Siren IDs
                for match in siren_pattern.finditer(content):
                    siren_id = match.group(1)
                    sirens[siren_id].append(folder)
                # Light IDs
                for match in light_pattern.finditer(content):
                    light_id = match.group(1)
                    lights[light_id].append(folder)

# Prepare output
dupes = {k: v for k, v in modkits.items() if len(v) > 1}
uniques = {k: v for k, v in modkits.items() if len(v) == 1}

with open(output_file, 'w', encoding='utf-8') as out:
    out.write('DUPLICATE MODKIT IDs:\n')
    for k, v in dupes.items():
        out.write(f'ID {k}: {len(v)} times\n')
        for folder in v:
            out.write(f'  {folder}\n')
    out.write('\nALL MODKIT IDs:\n')
    for k, v in uniques.items():
        out.write(f'ID {k}: {v[0]}\n')
    out.write('\nSIREN IDs:\n')
    for k, v in sirens.items():
        out.write(f'ID {k}: {", ".join(v)}\n')
    out.write('\nLIGHT IDs:\n')
    for k, v in lights.items():
        out.write(f'ID {k}: {", ".join(v)}\n')

print(f"Done! See {output_file} for results.")