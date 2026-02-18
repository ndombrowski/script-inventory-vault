import csv
import os
import argparse
from Bio import SeqIO
from pyparsing import Iterator

__author__ = "Nina Dombrowski"
__version__ = "1.0.0"
__date__ = "2026-02-17"


def parse_args():
    parser = argparse.ArgumentParser(
        description="""Calculates per-sequence statistics from a FASTA file and outputs results as CSV. \nFor each sequence, computes: GC content (%), total length, and ambiguous base count. \nNote: Sequences are standardized to uppercase, so soft-masked bases are included in counts. \n\nExample usage: python fasta_record_stats.py -i data/genome.fna -o results/genome_stats.csv
        """,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-i", "--input_file", required=True, help="Path to DNA fasta file"
    )
    parser.add_argument(
        "-o", "--output_file", required=True, help="Path to output csv file"
    )
    return parser.parse_args()


def validate_inputs(input_file:str, output_file:str) -> None:
    """
    Validate that the input file exists and output directory is writable.
    
    Raises:
        FileNotFoundError: If input file or output directory does not exist.
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")

    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        raise FileNotFoundError(f"Output directory not found: {output_dir}")


def gc_stats(sequence: str) -> tuple[float, int, int]:
    """
    Calculate GC content and sequence composition statistics.
    
    GC content is calculated using only unambiguous bases (A, T, C, G).
    Ambiguous bases (N, etc.) are counted but excluded from the percentage.
    
    Args:
        sequence: DNA sequence string (case-insensitive).
    
    Returns:
        Tuple of (gc_percent, total_length, ambiguous_count).
        Returns 0.0 for GC percent if sequence contains no unambiguous bases.
    """
    # Calculate GC content only based on the sequence that contains ATCG
    # and ignore ambiguous bp
    sequence = sequence.upper()
    gc = sequence.count("G") + sequence.count("C")
    at = sequence.count("A") + sequence.count("T")
    unambiguous = gc + at
    total = len(sequence)
    ambiguous = total - unambiguous

    if unambiguous == 0:
        gc_perc = 0.0
    else:
        gc_perc = gc / unambiguous * 100

    return gc_perc, total, ambiguous


def compute_gc_records(records):
    """
    Generate statistics for each sequence record.
    
    Args:
        records: Iterator of Bio.SeqIO records.
    
    Yields:
        Tuple of (record_id, gc_percent, total_length, ambiguous_count).
    """
    for rec in records:
        gc_perc, total_len, ambig_count = gc_stats(str(rec.seq))
        yield rec.id, gc_perc, total_len, ambig_count


def write_gc(rows, output):
    """
    Write sequence statistics to CSV file.
    
    Args:
        rows: Iterator of tuples (header, gc_percent, total_length, ambiguous_count).
        output: Path to output CSV file.
    """
    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["header", "gc_percentage", "total_length_bp", "ambiguous_bp"])
        for header, value, total_bp, ambig_bp in rows:
            writer.writerow([header, round(value, 2), total_bp, ambig_bp])


def main():
    args = parse_args()
    validate_inputs(args.input_file, args.output_file)

    records = SeqIO.parse(args.input_file, "fasta")
    gc_rows = compute_gc_records(records)
    write_gc(gc_rows, args.output_file)


if __name__ == "__main__":
    main()
