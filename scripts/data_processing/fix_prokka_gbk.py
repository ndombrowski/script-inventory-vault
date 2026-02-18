#!/usr/bin/env python3
"""
Fix Prokka-generated GenBank files using the original FASTA file as reference.

This script:
1. Reads contig names from the original FASTA file
2. Reads the GenBank file and finds concatenated LOCUS lines
3. Matches each LOCUS to its original contig name
4. Properly separates the contig name from the sequence length

Usage:
    python fix_prokka_gbk.py <fasta_dir> <gbk_dir> <output_dir>

Example:
    python fix_prokka_gbk.py data/genomes data/prokka data/prokka_fixed

Author:
    Nina Dombrowski

Last updated:
    2026-02-13
"""
import sys
import re
import argparse
from pathlib import Path


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Fix Prokka-generated GenBank files using the original FASTA file as reference.",
        epilog="Example: python fix_prokka_gbk.py --fasta_dir data/genomes -gbk_dir data/prokka --output_dir data/prokka_fixed",
    )

    parser.add_argument(
        "--fasta_dir",
        type=str,
        required=True,
        help="Directory containing original FASTA files (.fna)",
    )

    parser.add_argument(
        "--gbk_dir",
        type=str,
        required=True,
        help="Directory containing Prokka GenBank files (.gbk)",
    )

    parser.add_argument(
        "--output_dir",
        type=str,
        required=True,
        help="Directory where fixed GenBank files will be saved",
    )

    parser.add_argument(
        "-d",
        "--delimiter",
        type=str,
        default="-",
        help='Delimiter for smart name truncation of contig names that are too long (default: "-")',
    )

    return parser.parse_args()


def read_fasta_headers(fasta_file):
    """
    Extract all contig names from a FASTA file.
    Returns a list of contig names (without the > prefix).
    """
    contig_names = []
    try:
        with open(fasta_file, "r") as f:
            for line in f:
                if line.startswith(">"):
                    # Get the full header, strip >, and take first field
                    header = line[1:].strip().split()[0]
                    contig_names.append(header)
    except FileNotFoundError:
        print(f"Warning: FASTA file not found: {fasta_file}")

    return contig_names


def find_matching_contig(locus_name_field, contig_names):
    """
    Find which contig name matches the concatenated LOCUS field.

    Args:
        locus_name_field: The problematic field like "GCF_000005845.2-NC_000913.34641652"
        contig_names: List of original contig names like ["GCF_000005845.2-NC_000913.3"]

    Returns:
        (contig_name, length) tuple, or (None, None) if no match
    """

    # For each contig name, check if the locus field starts with it (ignoring trailing digits)
    for contig_name in contig_names:
        # The locus field should start with the contig name
        # Then have additional digits (the length) appended

        # Escape special regex characters in contig name
        escaped_contig = re.escape(contig_name)

        # Try to match: contig_name followed by just digits (the length)
        # The contig might end with a number (like .3), and length gets appended
        pattern = f"^{escaped_contig}(\\d+)$"
        match = re.match(pattern, locus_name_field)

        if match:
            length = match.group(1)
            return contig_name, length

    return None, None


def fix_locus_line(line, contig_names, delimiter="-"):
    """
    Fix a LOCUS line using the original contig names from FASTA.

    GenBank LOCUS line format:
    01-05      'LOCUS'
    06-12      spaces
    13-28      Locus name
    29-29      space
    30-40      Length of sequence, right-justified
    41-41      space
    42-43      bp
    44-44      space
    45-47      spaces, ss-, ds-, or ms-
    48-53      NA, DNA, RNA, etc. Left justified
    54-55      space
    56-63      'linear' or 'circular'
    64-64      space
    65-67      Division code
    68-68      space
    69-79      Date (dd-MMM-yyyy)

    Args:
        line: The LOCUS line to fix
        contig_names: List of contig names from FASTA
        delimiter: Character to use for smart truncation (default: "-")
    """

    if not line.startswith("LOCUS"):
        return line

    parts = line.split()
    if len(parts) < 3:
        return line

    locus_name_field = parts[1]

    # Try to find matching contig and extract length
    contig_name, length = find_matching_contig(locus_name_field, contig_names)

    # If matching failed, return original line
    if contig_name is None or length is None:
        return line

    # Limit name to reasonable length for GenBank format
    name = contig_name
    #if delimiter in name:
    #    # Split by delimiter and keep components from the end until we exceed 16 chars
    #    parts_list = name.split(delimiter)
    #    name = parts_list[-1]
    #else:
    #   # No delimiter found, just use last 16 characters
    #    name = name #name[-16:]

    # Extract other components from original line with fallbacks
    molecule_type = parts[3] if len(parts) > 3 else "DNA"
    topology = parts[4] if len(parts) > 4 else "linear"
    division = parts[5] if len(parts) > 5 and len(parts[5]) == 3 else "   "
    date = (
        parts[6]
        if len(parts) > 6
        else parts[5] if len(parts) > 5 and "-" in parts[5] else "01-JAN-2000"
    )

    # Construct the properly formatted LOCUS line
    fixed_line = f"LOCUS       {name:<16} {length:>11} bp    {molecule_type:<6}  {topology:<8} {division} {date}\n"

    return fixed_line


def fix_genbank_file(fasta_file, gbk_file, output_file):
    """
    Fix a GenBank file using its corresponding FASTA file.
    """

    # Read contig names from FASTA
    contig_names = read_fasta_headers(fasta_file)

    if not contig_names:
        print(f"  Error: No contigs found in {fasta_file}")
        return False

    print(f"  Found {len(contig_names)} contigs in FASTA")

    # Process GenBank file
    try:
        with open(gbk_file, "r") as infile, open(output_file, "w") as outfile:
            locus_count = 0
            for line in infile:
                if line.startswith("LOCUS"):
                    locus_count += 1
                    fixed_line = fix_locus_line(line, contig_names)
                    outfile.write(fixed_line)
                else:
                    outfile.write(line)

        return True

    except Exception as e:
        print(f"  Error processing files: {e}")
        return False


def find_matching_files(fasta_dir, gbk_dir):
    """
    Find pairs of FASTA and GenBank files that match.

    Matches based on filename stems. Works with any naming scheme:
    - GCF_000005845.fna matches GCF_000005845.gbk
    - MAG01.fna matches MAG01.gbk
    - sample_001.fna matches sample_001.gbk

    Also handles files with different suffixes before the extension:
    - GCF_000005845.2_ASM584v2_genomic_cleaned.fna matches GCF_000005845.gbk
    - MAG01_assembly.fna matches MAG01.gbk

    Matching priority:
    1. Exact stem match (MAG01 == MAG01)
    2. Stem is prefix of other (MAG01 matches MAG01_assembly or MAG01.2)
    """
    fasta_dir = Path(fasta_dir)
    gbk_dir = Path(gbk_dir)

    # Get all FASTA files with their stems
    fasta_files = {}
    for f in fasta_dir.glob("*.fna"):
        fasta_files[f.stem] = f
    for f in fasta_dir.glob("*.fasta"):
        fasta_files[f.stem] = f

    # Get all GenBank files with their stems
    gbk_files = {f.stem: f for f in gbk_dir.glob("*.gbk")}

    # Find matches
    matches = []
    matched_gbk = set()

    # First pass: exact matches
    for fasta_stem, fasta_file in fasta_files.items():
        if fasta_stem in gbk_files:
            matches.append((fasta_stem, fasta_file, gbk_files[fasta_stem]))
            matched_gbk.add(fasta_stem)

    # Second pass: prefix matches (for cases like MAG01.fna and MAG01_assembly.gbk)
    for fasta_stem, fasta_file in fasta_files.items():
        if fasta_stem in matched_gbk:
            continue

        # Check if FASTA stem is a prefix of any unmatched GBK stem
        for gbk_stem, gbk_file in gbk_files.items():
            if gbk_stem in matched_gbk:
                continue

            # Check if one is a prefix of the other
            # (separated by _ or . or - to avoid partial matches like MA matching MAG)
            if (
                gbk_stem.startswith(fasta_stem + "_")
                or gbk_stem.startswith(fasta_stem + ".")
                or gbk_stem.startswith(fasta_stem + "-")
                or fasta_stem.startswith(gbk_stem + "_")
                or fasta_stem.startswith(gbk_stem + ".")
                or fasta_stem.startswith(gbk_stem + "-")
            ):
                matches.append((fasta_stem, fasta_file, gbk_file))
                matched_gbk.add(gbk_stem)
                break

    return matches


def main():
    args = parse_arguments()

    fasta_dir = Path(args.fasta_dir)
    gbk_dir = Path(args.gbk_dir)
    output_dir = Path(args.output_dir)

    # Validate input directories
    if not fasta_dir.exists():
        print(f"Error: FASTA directory not found: {fasta_dir}")
        sys.exit(1)

    if not gbk_dir.exists():
        print(f"Error: GenBank directory not found: {gbk_dir}")
        sys.exit(1)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find matching file pairs
    matches = find_matching_files(fasta_dir, gbk_dir)

    if not matches:
        print("Error: No matching FASTA and GenBank file pairs found!")
        print("Make sure files have matching accession numbers (e.g., GCF_000005845)")
        sys.exit(1)

    print(f"\nFound {len(matches)} matching file pairs:")
    for base, fasta, gbk in matches:
        print(f"  {base}: {fasta.name} + {gbk.name}")
    print()

    # Process each pair
    success_count = 0
    for base, fasta_file, gbk_file in matches:
        output_file = output_dir / gbk_file.name

        print(f"Processing: {base}")
        print(f"  FASTA: {fasta_file.name}")
        print(f"  GenBank: {gbk_file.name}")

        if fix_genbank_file(fasta_file, gbk_file, output_file):
            print(f"  Created: {output_file.name}")
            success_count += 1
        else:
            print(f"  Failed")
        print()

    print("=" * 80)
    print(f"Done! Fixed files are in: {output_dir}")


if __name__ == "__main__":
    main()
