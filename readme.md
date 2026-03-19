Yes this was made by AI, That i cant code for shit, dont complain that i dont care

# Modkit Checker

This script scans FiveM vehicle meta files with `carcols` in the filename, extracts modkit IDs and siren IDs, and writes the results into separate report files.

## What the script does

- Walks every subfolder under the configured `root_dir`
- Only scans files whose name contains `carcols`
- Extracts modkit IDs from `<Item><kitName>...</kitName><id value="..."/></Item>` entries
- Extracts siren IDs from `<Sirens>` blocks and `CSirenSetting` nodes
- Avoids mixing light IDs into the siren report
- Detects files that contain multiple `<Kits>`, `<Sirens>`, or `<Lights>` blocks
- Writes each report to its own file inside the `reports` folder

## Output files

When the script runs, it creates these files inside `reports`:

- `duplicate_modkit_ids.txt`
- `duplicate_siren_ids.txt`
- `multiple_sets.txt`
- `all_modkit_ids.txt`
- `all_siren_ids.txt`

## How folders are labeled

For each scanned file, the script uses the file's parent folder as the resource name.

If the file is inside a `data` or `common` folder, it uses the folder above that instead.

## Configuration

Set the folder you want to scan by editing `root_dir` at the top of `check_modkits.py`.

Example:

```python
root_dir = r'D:\Your\FiveM\Resources\Folder'
```

Reports are written to the folder set in `output_dir`:

```python
output_dir = 'reports'
```

## Requirements

- Python 3.7 or newer
- No external packages required

## Usage

1. Open `check_modkits.py`
2. Set `root_dir` to your FiveM resources folder
3. Run the script:

```bash
python check_modkits.py
```

4. Open the generated files in the `reports` folder

## Notes

- The script currently checks files with `carcols` in the filename, not every `.meta` file
- `multiple_sets.txt` can still report repeated `<Lights>` blocks as a structure warning, even though light IDs are no longer extracted into reports
