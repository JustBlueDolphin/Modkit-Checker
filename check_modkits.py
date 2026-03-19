# You can save this as check_modkits.py and run it from your project root.
import os
import re
from collections import defaultdict
import time

# Change this to your root directory vehicle files are located.
root_dir = r'ChangeThisToYourRootDirectory'
output_dir = 'reports'

# Siren parsing is limited to Sirens sections or explicit CSirenSetting nodes
# so light IDs and other Item IDs do not leak into siren reports.
siren_block_pattern = re.compile(r'<Sirens>(.*?)</Sirens>', re.DOTALL)
siren_with_name_pattern = re.compile(r'<Item[^>]*>.*?<name>([^<]+)</name>.*?<id\s+value="(\d+)"\s*/>.*?</Item>', re.DOTALL)
siren_with_name_pattern2 = re.compile(r'<Item[^>]*>.*?<id\s+value="(\d+)"\s*/>.*?<name>([^<]+)</name>.*?</Item>', re.DOTALL)
siren_item_id_pattern = re.compile(r'<Item[^>]*>.*?<id\s+value="(\d+)"\s*/>.*?</Item>', re.DOTALL)
standalone_siren_pattern = re.compile(r'<CSirenSetting>.*?<id\s+value="(\d+)"\s*/>.*?</CSirenSetting>', re.DOTALL)

item_pattern = re.compile(
    r'<Item>\s*<kitName>([^<]+)</kitName>\s*<id\s+value="(\d+)"\s*/>',
    re.DOTALL,
)

modkits = defaultdict(list)
sirens = defaultdict(list)
multi_sets = []


def resolve_folder(filepath):
    folder = os.path.basename(os.path.dirname(filepath))
    if folder.lower() in ('data', 'common'):
        parent_parent = os.path.dirname(os.path.dirname(filepath))
        folder_before = os.path.basename(parent_parent)
        if folder_before:
            return folder_before
    return folder


for subdir, _, files in os.walk(root_dir):
    for file in files:
        if 'carcols' not in file.lower():
            continue

        filepath = os.path.join(subdir, file)
        folder = resolve_folder(filepath)
        print(f'Scanning: {filepath}')

        with open(filepath, encoding='utf-8', errors='ignore') as handle:
            content = handle.read()

        kits_blocks = re.findall(r'<Kits[>\s]', content)
        sirens_blocks = re.findall(r'<Sirens[>\s]', content)
        lights_blocks = re.findall(r'<Lights[>\s]', content)
        if len(kits_blocks) > 1 or len(sirens_blocks) > 1 or len(lights_blocks) > 1:
            multi_sets.append({
                'file': filepath,
                'kits': len(kits_blocks),
                'sirens': len(sirens_blocks),
                'lights': len(lights_blocks),
            })

        sirens_found = 0

        for match in item_pattern.finditer(content):
            kit_name = match.group(1)
            modkit_id = match.group(2)
            modkits[modkit_id].append((kit_name, folder))

        seen_siren_entries = set()
        siren_names_found = set()

        for siren_block in siren_block_pattern.findall(content):
            for pattern in [siren_with_name_pattern, siren_with_name_pattern2]:
                for match in pattern.finditer(siren_block):
                    if pattern == siren_with_name_pattern:
                        siren_name = match.group(1).strip()
                        siren_id = match.group(2)
                    else:
                        siren_id = match.group(1)
                        siren_name = match.group(2).strip()

                    entry = (siren_id, siren_name)
                    if entry in seen_siren_entries:
                        continue

                    sirens[siren_id].append((folder, siren_name))
                    siren_names_found.add(siren_id)
                    seen_siren_entries.add(entry)
                    sirens_found += 1

            for match in siren_item_id_pattern.finditer(siren_block):
                siren_id = match.group(1)
                entry = (siren_id, 'Unknown')
                if siren_id in siren_names_found or entry in seen_siren_entries:
                    continue

                sirens[siren_id].append((folder, 'Unknown'))
                seen_siren_entries.add(entry)
                sirens_found += 1

        for match in standalone_siren_pattern.finditer(content):
            siren_id = match.group(1)
            entry = (siren_id, 'Unknown')
            if entry in seen_siren_entries or siren_id in siren_names_found:
                continue

            sirens[siren_id].append((folder, 'Unknown'))
            seen_siren_entries.add(entry)
            sirens_found += 1

        if sirens_found > 0:
            print(f'  -> Found {sirens_found} sirens in {file}')

        time.sleep(0.1)

modkit_dupes = {key: value for key, value in modkits.items() if len(value) > 1}
modkit_uniques = {key: value for key, value in modkits.items() if len(value) == 1}
siren_dupes = {key: value for key, value in sirens.items() if len(value) > 1}
siren_uniques = {key: value for key, value in sirens.items() if len(value) == 1}

os.makedirs(output_dir, exist_ok=True)


def write_report(filename, header, writer):
    report_path = os.path.join(output_dir, filename)
    with open(report_path, 'w', encoding='utf-8') as out:
        out.write(f'{header}\n')
        out.write(f"{'=' * len(header)}\n\n")
        writer(out)
    return report_path


def write_duplicate_modkits(out):
    if not modkit_dupes:
        out.write('(no duplicate modkit IDs found)\n')
        return

    for modkit_id, entries in modkit_dupes.items():
        out.write(f'ID {modkit_id}\n')
        for kit_name, folder in entries:
            out.write(f'  - Kit Name: {kit_name}\n')
            out.write(f'  - Folder: {folder}\n')
        out.write('\n')


def write_duplicate_sirens(out):
    if not siren_dupes:
        out.write('(no duplicate siren IDs found)\n')
        return

    for siren_id, entries in siren_dupes.items():
        out.write(f'ID {siren_id}\n')
        for folder, name in entries:
            out.write(f'  - Folder: {folder}\n')
            if name != 'Unknown':
                out.write(f'  - Name: {name}\n')
        out.write('\n')


def write_multiple_sets(out):
    if not multi_sets:
        out.write('(no files with multiple sets found)\n')
        return

    for entry in multi_sets:
        out.write(f"File: {entry['file']}\n")
        if entry['kits'] > 1:
            out.write(f"  - <Kits> blocks: {entry['kits']}\n")
        if entry['sirens'] > 1:
            out.write(f"  - <Sirens> blocks: {entry['sirens']}\n")
        if entry['lights'] > 1:
            out.write(f"  - <Lights> blocks: {entry['lights']}\n")
        out.write('\n')


def write_all_modkits(out):
    if not modkit_uniques:
        out.write('(no single-use modkit IDs found)\n')
        return

    for modkit_id, entries in modkit_uniques.items():
        kit_name, folder = entries[0]
        out.write(f'ID {modkit_id}\n')
        out.write(f'  - Kit Name: {kit_name}\n')
        out.write(f'  - Folder: {folder}\n\n')


def write_all_sirens(out):
    if not siren_uniques:
        out.write('(no single-use siren IDs found)\n')
        return

    for siren_id, entries in siren_uniques.items():
        out.write(f'ID {siren_id}\n')
        for folder, name in entries:
            out.write(f'  - Folder: {folder}\n')
            if name != 'Unknown':
                out.write(f'  - Name: {name}\n')
        out.write('\n')


written_reports = [
    write_report('duplicate_modkit_ids.txt', 'DUPLICATE MODKIT IDs', write_duplicate_modkits),
    write_report('duplicate_siren_ids.txt', 'DUPLICATE SIREN IDs', write_duplicate_sirens),
    write_report('multiple_sets.txt', 'FILES WITH MULTIPLE SETS', write_multiple_sets),
    write_report('all_modkit_ids.txt', 'ALL MODKIT IDs', write_all_modkits),
    write_report('all_siren_ids.txt', 'ALL SIREN IDs', write_all_sirens),
]

print('Done! Reports written to:')
for report_path in written_reports:
    print(f'  - {report_path}')