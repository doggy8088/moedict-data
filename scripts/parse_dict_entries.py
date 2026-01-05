#!/usr/bin/env python3
"""
Script to parse the moe dictionary data file (dict‑revised.json) and split it
into individual JSON files, one per dictionary entry.  The script reads the
source JSON file, iterates through each entry, and writes a new file in
``output_dir`` using the entry's ``title`` as the filename.  If multiple
entries share the same title, an index is appended to the filename to
disambiguate them.  Filenames are sanitised to avoid characters that are
illegal in most filesystems.

Usage:

    python parse_dict_entries.py --input dict-revised.json --output_dir entries

The script will create the output directory if it does not exist.
"""

import argparse
import json
import os
import re
from collections import defaultdict

def sanitise_filename(name: str) -> str:
    """Sanitise a string so it can be used as a filename.

    This function removes or replaces characters that are invalid in most
    filesystems, such as slashes and colons.  It also strips whitespace at
    both ends.  Unicode characters (including Chinese) are preserved.

    Args:
        name: The original title to be sanitised.

    Returns:
        A safe filename string.
    """
    # Replace path separators and other invalid characters with underscores
    # Invalid characters on Windows (also safe on Unix): \ / : * ? " < > |
    invalid_chars = r"[\\/:*?\"<>|]"
    name = re.sub(invalid_chars, "_", name)
    name = name.strip()
    return name

def split_dictionary(input_file: str, output_dir: str) -> None:
    """Split the MoE dictionary JSON into individual files.

    Args:
        input_file: Path to the source ``dict-revised.json`` file.
        output_dir: Directory where individual JSON files will be written.
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Load the entire JSON array.  The file is ~70 MB, which fits comfortably
    # in memory; using a streaming parser would add complexity without much
    # benefit here.
    with open(input_file, 'r', encoding='utf-8') as f:
        entries = json.load(f)

    # Track counts for duplicate titles
    seen_counts: defaultdict[str, int] = defaultdict(int)

    for entry in entries:
        title = entry.get('title')
        if not title:
            # Skip entries without a title field
            continue
        safe_title = sanitise_filename(title)
        count = seen_counts[safe_title]
        if count > 0:
            filename = f"{safe_title}_{count}.json"
        else:
            filename = f"{safe_title}.json"
        seen_counts[safe_title] += 1
        output_path = os.path.join(output_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as out_f:
            json.dump(entry, out_f, ensure_ascii=False, indent=2)

def main() -> None:
    parser = argparse.ArgumentParser(description='Split MoE dictionary JSON file into individual entry files.')
    parser.add_argument('--input', required=True, help='Path to dict-revised.json')
    parser.add_argument('--output_dir', required=True, help='Directory to store individual entry JSON files')
    args = parser.parse_args()

    split_dictionary(args.input, args.output_dir)

if __name__ == '__main__':
    main()
