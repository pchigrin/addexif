from pathlib import Path
from datetime import datetime
from PIL import Image
import piexif
import yaml
import os


def has_exif(image_path):
    """Check if an image has existing EXIF data."""
    try:
        exif_dict = piexif.load(str(image_path))
        return bool(exif_dict.get("0th") or exif_dict.get("Exif") or exif_dict.get("GPS"))
    except Exception:
        return False


def process_datetime_placeholder(value, image_path):
    """Replace datetime placeholders with actual values."""
    if not isinstance(value, str):
        return value

    # EXIF datetime format: YYYY:MM:DD HH:MM:SS
    exif_format = "%Y:%m:%d %H:%M:%S"

    if value == "%CURRENT%":
        return datetime.now().strftime(exif_format)

    if value in ("%FILE%", "%FILE_CREATION%"):
        stat = os.stat(image_path)
        # macOS: st_birthtime, others: st_ctime or use mtime as fallback
        creation_time = getattr(stat, "st_birthtime", stat.st_mtime)
        return datetime.fromtimestamp(creation_time).strftime(exif_format)

    if value == "%FILE_MODIFICATION%":
        stat = os.stat(image_path)
        return datetime.fromtimestamp(stat.st_mtime).strftime(exif_format)

    return value


def load_yaml_exif(yaml_path):
    """Load EXIF data from YAML file."""
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)
    return data or {}


def convert_exif_value(value, tag_type):
    """Convert YAML value to piexif format based on tag type."""
    # piexif tag types: 1=BYTE, 2=ASCII, 3=SHORT, 4=LONG, 5=RATIONAL,
    # 6=SBYTE, 7=UNDEFINED, 8=SSHORT, 9=SLONG, 10=SRATIONAL, 11=FLOAT, 12=DOUBLE
    
    if tag_type == 2:  # ASCII string
        if isinstance(value, str):
            return value.encode("utf-8")
        return value
    
    elif tag_type == 3 or tag_type == 8:  # SHORT or SSHORT
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return value
        return value
    
    elif tag_type == 4 or tag_type == 9:  # LONG or SLONG
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return value
        return value
    
    elif tag_type == 5 or tag_type == 10:  # RATIONAL or SRATIONAL
        if isinstance(value, (list, tuple)):
            return tuple(value)
        elif isinstance(value, str):
            # Parse string representation of tuple like "(72, 1)"
            try:
                value = value.strip()
                if value.startswith("(") and value.endswith(")"):
                    value = value[1:-1]  # Remove parentheses
                parts = value.split(",")
                if len(parts) == 2:
                    return (int(parts[0].strip()), int(parts[1].strip()))
            except (ValueError, IndexError):
                pass
        return value

    elif tag_type == 7:  # UNDEFINED (bytes)
        if isinstance(value, str):
            # Handle escaped characters like "\x01\x02\x03"
            return value.encode("utf-8")
        return value
    
    return value


def write_exif_to_image(image_path, exif_dict, dry_run=False):
    """Write EXIF data to a JPEG image."""
    try:
        img = Image.open(image_path)

        # Initialize IFD structure
        ifd_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}}

        for key, value in exif_dict.items():
            tag_id = None
            ifd_name = None
            tag_type = None

            # Search for tag in standard EXIF tags
            for ifd in ("0th", "Exif", "GPS", "1st"):
                if ifd not in piexif.TAGS:
                    continue
                for tid, tag_info in piexif.TAGS[ifd].items():
                    if tag_info["name"] == key:
                        tag_id = tid
                        ifd_name = ifd
                        tag_type = tag_info.get("type", 2)  # Default to ASCII
                        break
                if tag_id:
                    break

            if tag_id and ifd_name:
                try:
                    converted_value = convert_exif_value(value, tag_type)
                    ifd_dict[ifd_name][tag_id] = converted_value
                except Exception as e:
                    # Skip tags that can't be converted
                    pass

        # Convert to EXIF bytes
        try:
            exif_bytes = piexif.dump(ifd_dict)
        except KeyError:
            # If dump fails due to invalid tags, try without problematic IFDs
            exif_bytes = piexif.dump({"0th": ifd_dict.get("0th", {}), 
                                      "Exif": ifd_dict.get("Exif", {}),
                                      "GPS": ifd_dict.get("GPS", {})})

        if not dry_run:
            img.save(image_path, exif=exif_bytes)
        return True
    except Exception as e:
        print(f"  Error writing EXIF to {image_path.name}: {e}")
        return False


def write_from_yaml(folder, yaml_path, recursive=False, force_write=False, dry_run=False):
    """Write EXIF data from YAML to images."""
    folder = Path(folder)
    exif_data = load_yaml_exif(yaml_path)

    if not exif_data:
        print("Error: No EXIF data in YAML file")
        return

    if recursive:
        image_files = list(folder.glob("**/*.jpg")) + list(folder.glob("**/*.jpeg"))
    else:
        image_files = list(folder.glob("*.jpg")) + list(folder.glob("*.jpeg"))

    if not image_files:
        print(f"No JPEG images found in {folder}")
        return

    mode_label = "[DRY RUN] " if dry_run else ""
    print(f"{mode_label}Found {len(image_files)} JPEG image(s)")

    processed = 0
    skipped = 0

    for image_path in image_files:
        has_existing = has_exif(image_path)

        if has_existing and not force_write:
            print(f"  - {image_path.name} (already has EXIF, skipping)")
            skipped += 1
            continue

        # Process datetime placeholders
        processed_exif = {}
        for key, value in exif_data.items():
            processed_exif[key] = process_datetime_placeholder(value, image_path)

        if dry_run:
            print(f"  ✓ {image_path.name}")
            for tag, value in processed_exif.items():
                print(f"      {tag}: {value}")
            processed += 1
        elif write_exif_to_image(image_path, processed_exif, dry_run=False):
            print(f"  ✓ {image_path.name}")
            processed += 1
        else:
            print(f"  ✗ {image_path.name} (write failed)")

    if dry_run:
        print(f"✓ [DRY RUN] Would process {processed} image(s), would skip {skipped}")
    else:
        print(f"✓ Processed {processed} image(s), skipped {skipped}")
