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

    if value == "%CURRENT%":
        return datetime.now().isoformat()

    if value in ("%FILE%", "%FILE_CREATION%"):
        stat = os.stat(image_path)
        # macOS: st_birthtime, others: st_ctime or use mtime as fallback
        creation_time = getattr(stat, "st_birthtime", stat.st_mtime)
        return datetime.fromtimestamp(creation_time).isoformat()

    if value == "%FILE_MODIFICATION%":
        stat = os.stat(image_path)
        return datetime.fromtimestamp(stat.st_mtime).isoformat()

    return value


def load_yaml_exif(yaml_path):
    """Load EXIF data from YAML file."""
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)
    return data or {}


def write_exif_to_image(image_path, exif_dict):
    """Write EXIF data to a JPEG image."""
    try:
        img = Image.open(image_path)

        # Convert dict to piexif format
        exif_bytes = piexif.dump({"0th": {}, "Exif": {}, "GPS": {}})

        for key, value in exif_dict.items():
            tag_id = None

            # Search for tag in standard EXIF tags
            for ifd_name in ("0th", "Exif"):
                for tid, tag_info in piexif.TAGS[ifd_name].items():
                    if tag_info["name"] == key:
                        tag_id = tid
                        ifd = ifd_name
                        break
                if tag_id:
                    break

            if tag_id:
                try:
                    if isinstance(value, str):
                        exif_bytes_dict = piexif.load(exif_bytes)
                        exif_bytes_dict[ifd][tag_id] = (value.encode("utf-8"),)
                        exif_bytes = piexif.dump(exif_bytes_dict)
                except Exception:
                    pass

        img.save(image_path, exif=exif_bytes)
        return True
    except Exception as e:
        print(f"  Error writing EXIF to {image_path.name}: {e}")
        return False


def write_from_yaml(folder, yaml_path, recursive=False, force_write=False):
    """Write EXIF data from YAML to images without EXIF."""
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

    print(f"Found {len(image_files)} JPEG image(s)")

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

        if write_exif_to_image(image_path, processed_exif):
            print(f"  ✓ {image_path.name}")
            processed += 1
        else:
            print(f"  ✗ {image_path.name} (write failed)")

    print(f"✓ Processed {processed} image(s), skipped {skipped}")
