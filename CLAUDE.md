# AddExif — Project Documentation

## Project Overview

**AddExif** is a Python console utility for managing EXIF metadata in JPEG images. It provides two main workflows:

1. **Scan**: Extract common EXIF tags from images and save to YAML
2. **Write**: Apply EXIF metadata from YAML to images lacking metadata

## Directory Structure

```
addexif/
├── .git/                          # Git repository
├── .venv/                         # Python virtual environment
├── .gitignore                     # Git ignore rules
├── dependencies.txt               # Python dependencies
├── CLAUDE.md                      # This file
├── README.md                      # User-facing documentation
├── addexif/
│   ├── __init__.py               # Package marker
│   ├── __main__.py               # Console entry point
│   ├── cli.py                    # Command routing (scan/write)
│   ├── scanner.py                # Image scanning & EXIF extraction
│   └── writer.py                 # EXIF writing with placeholder support
```

## Main Functions

### 1. Scan (`addexif scan`)

**Purpose**: Extract common EXIF data from JPEG images and save to YAML.

**Behavior**:
- Scans specified folder (default: current directory) for `.jpg`/`.jpeg` files
- Flat scan by default; use `-r` flag for recursive subdirectory scan
- Identifies EXIF tags that have **identical values across all images**
- Saves common tags to YAML file (flat structure, one tag per line)
- Output: `exif.yaml` by default; use `-o FILENAME` to customize

**Command Examples**:
```bash
addexif scan .                               # Scan current folder
addexif scan /photos -r -o common.yaml      # Recursive with custom output
```

### 2. Write (`addexif write`)

**Purpose**: Apply EXIF metadata from YAML to images without EXIF data.

**Behavior**:
- Reads EXIF data from YAML file
- Processes datetime placeholders in values:
  - `%CURRENT%` → current system date/time
  - `%FILE%` → file creation time (alias for %FILE_CREATION%)
  - `%FILE_CREATION%` → file creation time (stat.st_birthtime on macOS)
  - `%FILE_MODIFICATION%` → file modification time
- Writes EXIF to images **without existing EXIF** by default
- Use `-fw` (force write) flag to override and replace existing EXIF
- Use `-d` (dry run) flag to preview changes without modifying files
- Flat scan by default; use `-r` flag for recursive subdirectory scan

**Command Examples**:
```bash
addexif write . exif.yaml              # Write to folder
addexif write . exif.yaml -fw -r       # Recursive, force-write existing EXIF
addexif write . exif.yaml -d           # Preview changes without modifying
addexif write . exif.yaml -d -fw -r    # Dry run with recursion and force-write
```

**Dry Run Output**:
When using `-d` flag, the command shows:
- List of files that would be processed
- All EXIF tags that would be applied to each file
- Total count of files that would be processed/skipped
- No files are actually modified

## YAML Format

Flat key-value structure, one EXIF tag per line:

```yaml
DateTimeOriginal: 2024-01-15T10:30:00
Make: Canon
Model: EOS 5D Mark IV
GPSInfo: 40.7128,-74.0060
```

Datetime values support placeholders:
```yaml
DateTimeOriginal: %CURRENT%           # Use current system time
DateTimeOriginal: %FILE_CREATION%     # Use image file creation time
DateTimeOriginal: %FILE%              # Same as %FILE_CREATION%
```

## Key Design Decisions

| Aspect | Design |
|--------|--------|
| **Scan scope** | Flat by default, recursive with `-r` flag |
| **Common tags** | Only tags with identical values across all images |
| **Write scope** | Skip images with existing EXIF by default, force with `-fw` |
| **Dry run** | Preview changes without modifying files using `-d` flag |
| **DateTime** | Support %CURRENT%, %FILE%, %FILE_CREATION%, %FILE_MODIFICATION% |
| **Output format** | Flat YAML (key: value pairs) |
| **Default output** | `exif.yaml` in current directory |
| **CLI design** | Subcommand-based (scan/write) |

## Dependencies

- **Pillow** (>=10.0.0) — Image loading and metadata handling
- **piexif** (>=1.1.3) — EXIF data reading and writing
- **PyYAML** (>=6.0) — YAML file parsing
- **python-dateutil** (>=2.8.0) — DateTime utilities for placeholder processing

Managed in `dependencies.txt` and installed in `.venv/`.

## Setup & Development

```bash
# Initialize
python3 -m venv .venv
source .venv/bin/activate
pip install -r dependencies.txt

# Run
python -m addexif scan .
python -m addexif write . exif.yaml

# or after installing in editable mode:
pip install -e .
addexif scan .
```

## Building & Releasing

### Local build (standalone executable)

```bash
pip install pyinstaller
pyinstaller --onefile --name addexif addexif/__main__.py
# Output: dist/addexif (or dist/addexif.exe on Windows)
```

### Automated releases (GitHub Actions)

Releases are automatically built for Windows, Ubuntu, and macOS when you push a git tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions will:
1. Build standalone executables for all platforms
2. Create a GitHub Release
3. Attach binaries for download

No Python installation required to run released binaries.

## Error Handling

- Gracefully skip corrupted images (log warning, continue scanning)
- Exit with clear message if no JPEG images found
- Validate YAML structure before writing
- Warn if no common EXIF tags found during scan

## Git & Version Control

Initialized with `git init`. Standard Python `.gitignore` excludes:
- `.venv/`
- `__pycache__/`
- `*.pyc`
- `.egg-info/`

## Testing

Test files and fixtures live in `test_images/` (not committed; create locally for testing).

**Verification workflow**:
1. Create test JPEGs with known EXIF
2. Run `addexif scan test_images/ -o test_output.yaml`
3. Verify YAML contains only common tags
4. Run `addexif write test_images/ test_output.yaml -d`
5. Verify dry run output shows correct tags and files
6. Run `addexif write test_images/ test_output.yaml`
7. Verify EXIF written to images without metadata
8. Test datetime placeholders
9. Test `-fw` flag to override existing EXIF
10. Test `-d` flag with various combinations (`-d -fw`, `-d -r`, etc.)
