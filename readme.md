Yes this was made by AI, That i cant code for shit, dont complain that i dont care

# Modkit, Siren, and Light ID Checker

This Python script scans all `carcols.meta` files in your FiveM resource directory, extracts Modkit IDs, Siren IDs, and Light IDs, and lists them in a report. Duplicate Modkit IDs are shown at the top.

## Features

- Finds all Modkit IDs (`<Kits>...<id value="..."/>...`)
- Finds all Siren IDs (`<Sirens>...<id value="..."/>...`)
- Finds all Light IDs (`<Lights>...<id value="..."/>...`)
- Lists duplicate Modkit IDs and their resource folders
- Outputs results in `modkits_report.txt` in the format:  
  Example:
  ```
  DUPLICATE MODKIT IDs:
  ID 188: 4 times
    gb_admiral
    gb_neonct
    gb_schlagenr
    gb_schlagensp

  ALL MODKIT IDs:
  ID 959: gb_811s2
  ...

  SIREN IDs:
  ID 6808: gb_sultanrsxpol
  ...

  LIGHT IDs:
  ID 96: gb_811s2
  ...
  ```

## Dependencies

- [Python 3.7 or newer](https://www.python.org/downloads/)
- No external libraries required (uses only Python standard library)

## Usage

1. Place `check_modkits.py` in your main resource folder (e.g. `d:\Fivem Server\Blue-Box`)
2. **To scan a different folder:**  
   Edit the `root_dir` variable at the top of `check_modkits.py` and set it to your desired resource directory path.  
   Example:  
   ```python
   root_dir = r"d:\Your\Custom\Resource\Folder"
   ```
3. Open a terminal in VS Code or Command Prompt.
4. Run the script:
   ```
   python check_modkits.py
   ```
5. View the results in `modkits_report.txt` in the same folder.

## Customization

- Edit `root_dir` in the script if your resource folder is in a different location.

---

If you have any issues or want to add features,
