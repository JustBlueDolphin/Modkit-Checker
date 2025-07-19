# You can save this as check_modkits.py and run it from your project root.
import os
import re
from collections import defaultdict
import time  # Import time module for sleep

#Change this to your root directory vehicle files are located | # e.g., 'C:/path/to/your/modkits'
root_dir = r'ChangeThisToYourRootDirectory'
output_file = 'modkits_report.txt'

modkit_pattern = re.compile(r'<Kits>.*?<id\s+value="(\d+)"\s*/>', re.DOTALL)
siren_pattern = re.compile(r'<Sirens>.*?<id\s+value="(\d+)"\s*/>', re.DOTALL)
light_pattern = re.compile(r'<Lights>.*?<id\s+value="(\d+)"\s*/>', re.DOTALL)

# Updated regex to find all <Item> blocks with kitName and id
item_pattern = re.compile(
    r'<Item>\s*<kitName>([^<]+)</kitName>\s*<id\s+value="(\d+)"\s*/>',
    re.DOTALL
)

modkits = defaultdict(list)
sirens = defaultdict(list)
lights = defaultdict(list)

# Walk through all files in the directory
for subdir, _, files in os.walk(root_dir):
    for file in files:
        if 'carcols' in file.lower():
            filepath = os.path.join(subdir, file)
            folder = os.path.basename(os.path.dirname(filepath))
            print(f"Scanning: {filepath}")
            with open(filepath, encoding='utf-8', errors='ignore') as f:
                content = f.read()
                for match in item_pattern.finditer(content):
                    kit_name = match.group(1)
                    modkit_id = match.group(2)
                    modkits[modkit_id].append((kit_name, folder))
                # Sirens and Lights unchanged
                for match in siren_pattern.finditer(content):
                    siren_id = match.group(1)
                    sirens[siren_id].append(folder)
                for match in light_pattern.finditer(content):
                    light_id = match.group(1)
                    lights[light_id].append(folder)
            time.sleep(0.1)  # Increase delay to 0.1 seconds for slower scanning

# Prepare output
dupes = {k: v for k, v in modkits.items() if len(v) > 1}
uniques = {k: v for k, v in modkits.items() if len(v) == 1}

with open(output_file, 'w', encoding='utf-8') as out:
    out.write('==========================\nDUPLICATE MODKIT IDs\n==========================\n\n')
    if not dupes:
        out.write('(no duplicates found)\n\n')
    else:
        for k, v in dupes.items():
            out.write(f'ID {k}\n')
            for kit_name, folder in v:
                out.write(f'  └─ Kit Name: {kit_name}\n')
                out.write(f'  └─ Folder: {folder}\n')
            out.write('\n')

    out.write('==========================\nALL MODKIT IDs\n==========================\n\n')
    for k, v in uniques.items():
        kit_name, folder = v[0]
        out.write(f'ID {k}\n')
        out.write(f'  └─ Kit Name: {kit_name}\n')
        out.write(f'  └─ Folder: {folder}\n\n')

    out.write('==========================\nSIREN IDs\n==========================\n\n')
    for k, v in sirens.items():
        out.write(f'ID {k}\n')
        for folder in v:
            out.write(f'  └─ Folder: {folder}\n')
        out.write('\n')

    out.write('==========================\nLIGHT IDs\n==========================\n\n')
    for k, v in lights.items():
        out.write(f'ID {k}\n')
        for folder in v:
            out.write(f'  └─ Folder: {folder}\n')
        out.write('\n')

print(f"Done! See {output_file} for results.")