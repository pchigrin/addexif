# AddExif

A Python console utility for managing EXIF metadata in JPEG images.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r dependencies.txt
```

## Usage

### Scan for common EXIF data

Extract EXIF tags that have identical values across all images:

```bash
python -m addexif scan .                             # Current folder
python -m addexif scan /path/to/images -r            # Recursive
python -m addexif scan . -o custom_exif.yaml         # Custom output
```

### Write EXIF data to images

Apply EXIF metadata from YAML to images without existing EXIF:

```bash
python -m addexif write . exif.yaml                  # Write to images without EXIF
python -m addexif write . exif.yaml -fw              # Force overwrite existing EXIF
python -m addexif write . exif.yaml -fw -k           # Overwrite YAML tags only
python -m addexif write . exif.yaml -r               # Recursive
python -m addexif write . exif.yaml -d               # Preview changes (dry run)
python -m addexif write . exif.yaml -d -fw -k -r     # Dry run with all options
```

## YAML Format

Flat key-value structure:

```yaml
DateTimeOriginal: 2024-01-15T10:30:00
Make: Canon
Model: EOS 5D Mark IV
```

Datetime values support placeholders:
- `%CURRENT%` — current system date/time
- `%FILE%` — file creation time
- `%FILE_CREATION%` — file creation time
- `%FILE_MODIFICATION%` — file modification time

**Tip**: Use `-d` flag with write command to preview how placeholders will be expanded:
```bash
python -m addexif write . exif.yaml -d
```

## See Also

- `CLAUDE.md` — detailed project structure and design decisions
