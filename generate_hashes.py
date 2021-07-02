from pathlib import Path
import pooch

for p in sorted(list(Path('.').rglob('*'))):
    if str(p).startswith('.') or p.name.startswith('.'):
        continue

    if p.is_dir():
        continue

    file_hash = pooch.file_hash(p)
    print(f"'{p}': '{file_hash}',")
