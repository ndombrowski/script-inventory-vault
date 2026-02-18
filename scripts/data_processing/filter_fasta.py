from collections.abc import Iterator
from Bio.SeqRecord import SeqRecord
from Bio import SeqIO
import os
import re
import argparse

__author__ = "Nina Dombrowski"
__version__ = "1.0.1"
__date__ = "2026-02-18"


def parse_args():
    parser = argparse.ArgumentParser(
        description="""Filter sequences from a fasta file based on patterns or exact matches stored in a list.\n\n The patterns in the list are removed from the original fasta file unless `--keep_hits` is used.\n By default partial patterns are searched, if exact pattern matching is desired use the `--exact` argument.\n Note that exact matching only applies on the sequence ID (text before first space), while partial matching applies searches to the full header line.\n\nExample use: python filter_fasta.py -i genome.fna -l list.txt -o results/filtered.fna --keep_hits --exact
        """,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-i", "--input_file", required=True, help="Path to sequence file"
    )
    parser.add_argument(
        "-l", "--patterns_list", required=True, help="File with patterns to filter"
    )
    parser.add_argument(
        "--keep_hits",
        action="store_true",
        help="Only keep sequences that matches the patterns",
    )
    parser.add_argument(
        "--exact",
        action="store_true",
        help="Match full sequence IDs exactly instead of partial pattern matching. "
    )
    parser.add_argument(
        "-o", "--output_file", required=True, help="Path to output file"
    )
    return parser.parse_args()


def validate_inputs(input_file: str, output_file: str, patterns_file: str) -> None:
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    if not os.path.exists(patterns_file):
        raise FileNotFoundError(f"Pattern file not found: {patterns_file}")
    
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        raise FileNotFoundError(f"Output directory not found: {output_dir}")


def read_list(list_path: str) -> list[str]:
    """
    Reads a one-column file of sequence IDs or patterns and returns them as a list.

    Args:
        list_path: Path to the file containing one pattern per line.

    Returns:
        A list of non-empty, stripped strings.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file contains no valid (non-empty) lines.
    """
    id_list = []
    with open(list_path, "r") as f:
        for line in f:
            stripped = line.strip()
            if stripped:
                id_list.append(stripped)

    if not id_list:
        raise ValueError(
            f"Pattern file '{list_path}' is empty or contains only blank lines. "
            "Nothing to filter."
        )

    print(f"Patterns to search:    {len(id_list)}")
    return id_list


def filter_fasta(
    records: Iterator[SeqRecord], pattern_list: list[str], output_file: str, exact: bool, keep_hits: bool
) -> None:
    """
    Takes a set of fasta sequences and compares it against a list of IDs and filters the fasta sequences accordingly.
    If exact is true then an exact pattern matching is done, otherwise partial patterns are allowed.
    If keep_hits is true then only sequences that match the IDs in the list are kept, otherwise these sequences are discarded from the original file
    """
    pattern_set = set(pattern_list)
    sequences_read = 0
    sequences_written = 0
            
    with open(output_file, "w", encoding="utf-8") as out_handle:
        for record in records:
            sequences_read += 1

            if exact:
                keep_seq = record.id in pattern_set
            else:
                keep_seq = False
                for pattern in pattern_set:
                    search_target = record.description if record.description else record.id
                    if search_target and re.search(pattern, search_target):
                        keep_seq = True
                        break

            # Write the record if:
            #   - keep mode and it matched, OR
            #   - discard mode and it did not match
            if (keep_hits and keep_seq) or (not keep_hits and not keep_seq):
                SeqIO.write(record, out_handle, "fasta")
                sequences_written += 1

    print(f"Sequences read:        {sequences_read}")
    print(f"Sequences written:     {sequences_written}")
    print(f"Output written to:     {output_file}")
    

def main():
    args = parse_args()
    validate_inputs(args.input_file, args.output_file, args.patterns_list)

    records = SeqIO.parse(args.input_file, "fasta")
    id_list = read_list(args.patterns_list)
    print(id_list)
    filter_fasta(records, id_list, args.output_file, args.exact, args.keep_hits)


if __name__ == "__main__":
    main()
