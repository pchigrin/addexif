import argparse
import sys
from pathlib import Path
from addexif.scanner import scan_and_save
from addexif.writer import write_from_yaml


def main():
    parser = argparse.ArgumentParser(
        prog="addexif",
        description="Manage EXIF metadata in JPEG images"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Extract common EXIF data")
    scan_parser.add_argument(
        "folder",
        nargs="?",
        default=".",
        help="Folder to scan (default: current directory)"
    )
    scan_parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Scan subdirectories recursively"
    )
    scan_parser.add_argument(
        "-o", "--output",
        default="exif.yaml",
        help="Output YAML file (default: exif.yaml)"
    )

    # Write command
    write_parser = subparsers.add_parser("write", help="Write EXIF data to images")
    write_parser.add_argument(
        "folder",
        help="Folder containing images"
    )
    write_parser.add_argument(
        "yaml_file",
        help="YAML file with EXIF data"
    )
    write_parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Process subdirectories recursively"
    )
    write_parser.add_argument(
        "-fw", "--force-write",
        action="store_true",
        help="Override images with existing EXIF data"
    )
    write_parser.add_argument(
        "-d", "--dry-run",
        action="store_true",
        help="Preview changes without modifying files"
    )

    args = parser.parse_args()

    if args.command == "scan":
        try:
            folder = Path(args.folder).resolve()
            if not folder.exists():
                print(f"Error: Folder '{args.folder}' not found", file=sys.stderr)
                return 1

            scan_and_save(
                folder,
                recursive=args.recursive,
                output_path=args.output
            )
            print(f"✓ EXIF data saved to {args.output}")
            return 0
        except Exception as e:
            print(f"Error during scan: {e}", file=sys.stderr)
            return 1

    elif args.command == "write":
        try:
            folder = Path(args.folder).resolve()
            yaml_file = Path(args.yaml_file).resolve()

            if not folder.exists():
                print(f"Error: Folder '{args.folder}' not found", file=sys.stderr)
                return 1
            if not yaml_file.exists():
                print(f"Error: YAML file '{args.yaml_file}' not found", file=sys.stderr)
                return 1

            write_from_yaml(
                folder,
                yaml_file,
                recursive=args.recursive,
                force_write=args.force_write,
                dry_run=args.dry_run
            )
            return 0
        except Exception as e:
            print(f"Error during write: {e}", file=sys.stderr)
            return 1

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
