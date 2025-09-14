#!/usr/bin/env python3
"""
organize_downloads.py

Usage:
  python organize_downloads.py [--path /Users/you/Downloads] [--dry-run]

Defaults:
  path = ~/Downloads
  --dry-run will only print actions (won't move/create)
"""

from pathlib import Path
import shutil
import argparse
import sys

# ----- configuration: ext -> folder name (lowercase ext keys) -----
TYPES = {
    # videos
    "mp4": "Videos", "mkv": "Videos", "mov": "Videos", "avi": "Videos",
    "flv": "Videos", "wmv": "Videos", "m4v": "Videos",
    # images
    "jpg": "Images", "jpeg": "Images", "png": "Images", "gif": "Images",
    "webp": "Images", "heic": "Images", "svg": "Images", "bmp": "Images",
    "tif": "Images", "tiff": "Images",
    # pdfs / docs
    "pdf": "PDFs",
    "doc": "Documents", "docx": "Documents", "xls": "Documents", "xlsx": "Documents",
    "ppt": "Documents", "pptx": "Documents", "txt": "Documents", "md": "Documents",
    "rtf": "Documents",
    # archives
    "zip": "Archives", "tar": "Archives", "gz": "Archives", "tgz": "Archives",
    "bz2": "Archives", "rar": "Archives", "7z": "Archives",
    # apps / installers
    "dmg": "Apps", "pkg": "Apps", "exe": "Apps", "apk": "Apps",
    # code
    "py": "Code", "js": "Code", "java": "Code", "class": "Code", "jar": "Code",
    # audio (optional)
    "mp3": "Audio", "wav": "Audio", "flac": "Audio", "m4a": "Audio",
}

DEFAULT_FOLDER = "Other"

# ----- helpers -----
def folder_for_ext(ext: str) -> str:
    return TYPES.get(ext.lower(), DEFAULT_FOLDER)

def unique_target(dest_dir: Path, name: str) -> Path:
    """
    If dest_dir/name exists, append ' (1)', ' (2)', ... before the extension.
    """
    dest = dest_dir / name
    if not dest.exists():
        return dest
    stem = dest.stem
    suffix = dest.suffix  # includes leading dot or empty
    i = 1
    while True:
        candidate = dest_dir / f"{stem} ({i}){suffix}"
        if not candidate.exists():
            return candidate
        i += 1

# ----- main -----
def organize(downloads: Path, dry_run: bool = False):
    if not downloads.exists() or not downloads.is_dir():
        print(f"Error: not a directory: {downloads}", file=sys.stderr)
        return 1

    print(f"{'DRY RUN: ' if dry_run else ''}Organizing: {downloads}")

    # iterate files only (no directories), skip hidden files (name starts with '.')
    for item in downloads.iterdir():
        # skip directories and hidden files
        if item.is_dir():
            continue
        if item.name.startswith('.'):
            continue

        # determine extension (without dot)
        if item.suffix:
            ext = item.suffix[1:].lower()
        else:
            ext = ""

        folder_name = folder_for_ext(ext) if ext else DEFAULT_FOLDER
        target_dir = downloads / folder_name

        if not target_dir.exists():
            if dry_run:
                print(f"[DRY RUN] Would create folder: {target_dir}")
            else:
                target_dir.mkdir(parents=True, exist_ok=True)
                print(f"Created folder: {target_dir}")

        target_path = unique_target(target_dir, item.name)
        if dry_run:
            print(f"[DRY RUN] Would move: {item.name} -> {target_path.relative_to(downloads)}")
        else:
            shutil.move(str(item), str(target_path))
            print(f"Moved: {item.name} -> {target_path.relative_to(downloads)}")

    print("Done.")
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Organize Downloads folder by file type.")
    parser.add_argument("--path", "-p", default=str(Path.home() / "Downloads"),
                        help="Path to downloads folder (default: ~/Downloads)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print actions without creating/moving files")
    args = parser.parse_args()

    downloads_path = Path(args.path).expanduser().resolve()
    sys.exit(organize(downloads_path, args.dry_run))
