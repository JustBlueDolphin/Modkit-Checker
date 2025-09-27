# You can save this as check_modkits.py and run it from your project root.
import os
import re
from collections import defaultdict
import time  # Import time module for sleep

#Change this to your root directory vehicle files are located | # e.g., 'C:/path/to/your/modkits'
root_dir = r'ChangeThisToYourRootDirectory'
output_file = 'modkits_report.txt'

# Improved regex patterns to catch various siren/light structures
modkit_pattern = re.compile(r'<Kits>.*?<id\s+value="(\d+)"\s*/>', re.DOTALL)

# Multiple patterns for sirens - some files might have different structures
siren_pattern1 = re.compile(r'<Sirens>.*?<id\s+value="(\d+)"\s*/>', re.DOTALL)
siren_pattern2 = re.compile(r'<Item\s+type="CSirenSetting">.*?<id\s+value="(\d+)"\s*/>', re.DOTALL)
siren_pattern3 = re.compile(r'<Item>.*?<id\s+value="(\d+)"\s*/>', re.DOTALL)  # Generic Item with id
siren_pattern4 = re.compile(r'<CSirenSetting>.*?<id\s+value="(\d+)"\s*/>', re.DOTALL)

# Pattern to extract siren names - looks for <name> tags associated with siren IDs
siren_with_name_pattern = re.compile(r'<Item[^>]*>.*?<name>([^<]+)</name>.*?<id\s+value="(\d+)"\s*/>.*?</Item>', re.DOTALL)
siren_with_name_pattern2 = re.compile(r'<Item[^>]*>.*?<id\s+value="(\d+)"\s*/>.*?<name>([^<]+)</name>.*?</Item>', re.DOTALL)

# Multiple patterns for lights
light_pattern1 = re.compile(r'<Lights>.*?<id\s+value="(\d+)"\s*/>', re.DOTALL)
light_pattern2 = re.compile(r'<Item\s+type="CVehicleModelInfoLightSourceData">.*?<id\s+value="(\d+)"\s*/>', re.DOTALL)
light_pattern3 = re.compile(r'<CVehicleModelInfoLightSourceData>.*?<id\s+value="(\d+)"\s*/>', re.DOTALL)

# Updated regex to find all <Item> blocks with kitName and id
item_pattern = re.compile(
    r'<Item>\s*<kitName>([^<]+)</kitName>\s*<id\s+value="(\d+)"\s*/>',
    re.DOTALL
)

modkits = defaultdict(list)
sirens = defaultdict(list)  # Will store tuples of (folder, name)
lights = defaultdict(list)

# Walk through all files in the directory
for subdir, _, files in os.walk(root_dir):
    for file in files:
        if 'carcols' in file.lower():
            filepath = os.path.join(subdir, file)
            # Get the folder name; if it's "data" or "common", use the parent folder instead
            folder = os.path.basename(os.path.dirname(filepath))
            if folder.lower() in ('data', 'common'):
                # climb one level up to get the folder before 'data'/'common'
                parent_parent = os.path.dirname(os.path.dirname(filepath))
                folder_before = os.path.basename(parent_parent)
                if folder_before:  # fallback to original if something odd
                    folder = folder_before
            print(f"Scanning: {filepath}")
            with open(filepath, encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Track if we found sirens/lights in this file
                sirens_found = 0
                lights_found = 0
                
                for match in item_pattern.finditer(content):
                    kit_name = match.group(1)
                    modkit_id = match.group(2)
                    modkits[modkit_id].append((kit_name, folder))
                
                # First try to get sirens with names
                siren_names_found = set()  # Track which sirens we already found with names
                
                # Try patterns that capture both name and ID
                for pattern in [siren_with_name_pattern, siren_with_name_pattern2]:
                    for match in pattern.finditer(content):
                        if pattern == siren_with_name_pattern:
                            siren_name = match.group(1).strip()
                            siren_id = match.group(2)
                        else:  # siren_with_name_pattern2
                            siren_id = match.group(1)
                            siren_name = match.group(2).strip()
                        
                        sirens[siren_id].append((folder, siren_name))
                        siren_names_found.add(siren_id)
                        sirens_found += 1
                
                # Then try patterns that only get ID (for sirens without names or different structure)
                for pattern in [siren_pattern1, siren_pattern2, siren_pattern3, siren_pattern4]:
                    for match in pattern.finditer(content):
                        siren_id = match.group(1)
                        if siren_id not in siren_names_found:  # Only add if we haven't found it with a name
                            sirens[siren_id].append((folder, "Unknown"))
                            sirens_found += 1
                        
                # Try multiple light patterns
                for pattern in [light_pattern1, light_pattern2, light_pattern3]:
                    for match in pattern.finditer(content):
                        light_id = match.group(1)
                        lights[light_id].append(folder)
                        lights_found += 1
                        
                # Print debug info if sirens or lights found
                if sirens_found > 0 or lights_found > 0:
                    print(f"  -> Found {sirens_found} sirens and {lights_found} lights in {file}")
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
        for folder, name in v:
            out.write(f'  └─ Folder: {folder}\n')
            if name != "Unknown":
                out.write(f'  └─ Name: {name}\n')
        out.write('\n')

    out.write('==========================\nLIGHT IDs\n==========================\n\n')
    for k, v in lights.items():
        out.write(f'ID {k}\n')
        for folder in v:
            out.write(f'  └─ Folder: {folder}\n')
        out.write('\n')

print(f"Done! See {output_file} for results.")