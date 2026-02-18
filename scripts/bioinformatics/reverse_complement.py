import argparse
from Bio import SeqIO

__author__ = "Nina Dombrowski"
__version__ = "1.0.0"
__date__ = "2026-02-17"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate reverse complement of a DNA sequence. You can either pass a fasta file or a single string with -s. Note, if no argument is given a string can be entered when prompted.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Mutually exclusive group: either sequence, file, or interactive
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument("-s", "--sequence", help="DNA sequence string")
    input_group.add_argument(
        "-i",
        "--input_file",
        help="Path to FASTA file (outputs FASTA with reverse complements)",
    )

    parser.add_argument(
        "-o",
        "--output_file",
        help="Path to output FASTA file (only used with --input_file)",
    )

    return parser.parse_args()


def is_valid_dna(dna: str) -> None:
    """Validates DNA contains only ATCG. Raises ValueError if invalid."""
    for char in dna:
        if char not in "ATCG":
            raise ValueError(f"Invalid nucleotide: {char}")


def reverse_complement(dna: str) -> str:
    """
    Takes a DNA string and generates the reverse complement
    """
    reverse = reverse_string(dna)
    rev_com = complement_dna(reverse)

    return rev_com


def reverse_string(string: str) -> str:
    """
    Takes a string and reverses its order
    """
    return string[::-1]


def complement_dna(dna: str) -> str:
    """
    Generate the complement of a DNA string
    """
    dna_map: dict[str, str] = {
        "A": "T",
        "T": "A",
        "C": "G",
        "G": "C",
    }

    comp = []

    for char in dna:
        comp.append(dna_map[char])

    return "".join(comp)


def process_fasta(records):
    for rec in records:
        seq = str(rec.seq).upper()
        is_valid_dna(seq)
        rev_comp = reverse_complement(seq)
        yield rec.id, rev_comp


def write_out(rows, output):
    with open(output, "w") as out:
        for header, rev_com in rows:
            out.write(f">{header}_revcomp\n{rev_com}\n")


def main():
    args = parse_args()

    # Case 1: File input
    if args.input_file:
        if not args.output_file:
            raise ValueError("Error: --output_file required when using --input_file")

        records = SeqIO.parse(args.input_file, "fasta")
        rev_comp = process_fasta(records)
        write_out(rev_comp, args.output_file)

    # Case 2: Command-line sequence
    elif args.sequence:
        seq = args.sequence.upper()
        is_valid_dna(seq)
        print("Reverse complement is: \n", reverse_complement(seq), sep="")

    # Case 3: Interactive
    else:
        seq = input("Enter nucleotide sequence: ").upper()
        is_valid_dna(seq)
        print("Reverse complement is: \n", reverse_complement(seq), sep="")


if __name__ == "__main__":
    main()
