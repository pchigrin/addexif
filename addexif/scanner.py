from pathlib import Path
from PIL import Image
import piexif
import yaml


def get_all_exif(image_path):
    """Extract all EXIF data from an image."""
    try:
        exif_dict = piexif.load(str(image_path))
        exif_data = {}

        for ifd_name in ("0th", "Exif", "GPS"):
            ifd = exif_dict.get(ifd_name, {})
            for tag, value in ifd.items():
                tag_name = piexif.TAGS[ifd_name][tag]["name"]
                try:
                    if isinstance(value, bytes):
                        value = value.decode("utf-8", errors="ignore")
                    else:
                        value = str(value)

                    value = value.replace('\0', '').strip()
                    if value:
                        exif_data[tag_name] = value
                except Exception:
                    pass

        return exif_data if exif_data else None
    except Exception:
        return None


def find_common_exif(exif_list):
    """Return only EXIF tags with identical values across all images."""
    if not exif_list:
        return {}

    common = {}
    first_exif = exif_list[0]

    for tag, value in first_exif.items():
        if all(exif.get(tag) == value for exif in exif_list):
            common[tag] = value

    return common


def scan_and_save(folder, recursive=False, output_path="exif.yaml"):
    """Scan folder for JPEG images and save common EXIF to YAML."""
    folder = Path(folder)
    image_files = []

    if recursive:
        image_files = list(folder.glob("**/*.jpg")) + list(folder.glob("**/*.jpeg"))
    else:
        image_files = list(folder.glob("*.jpg")) + list(folder.glob("*.jpeg"))

    if not image_files:
        print(f"No JPEG images found in {folder}")
        return

    print(f"Found {len(image_files)} JPEG image(s)")

    exif_list = []
    for image_path in image_files:
        exif_data = get_all_exif(image_path)
        if exif_data:
            exif_list.append(exif_data)
            print(f"  ✓ {image_path.name}")
        else:
            print(f"  - {image_path.name} (no EXIF data)")

    if not exif_list:
        print("No EXIF data found in any images")
        return

    common_exif = find_common_exif(exif_list)

    if not common_exif:
        print("Warning: No EXIF tags common to all images")
        return

    with open(output_path, "w") as f:
        yaml.dump(common_exif, f, default_flow_style=False, sort_keys=False)

    print(f"✓ Found {len(common_exif)} common EXIF tag(s)")
