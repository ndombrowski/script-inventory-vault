from Bio import SeqIO
import argparse
import sys
import re

__author__ = "Nina Dombrowski"

parser = argparse.ArgumentParser(description="Filter sequences from a fasta file based on patterns or exact matches stored in a list")
parser.add_argument("fasta_file", help="input fasta file")
parser.add_argument("pattern_file", help="file containing patterns/ids to keep/remove")
parser.add_argument("--remove", action="store_true", help="remove sequences matching patterns")
parser.add_argument("--exact", action="store_true", help="perform exact matches instead of pattern matching")
args = parser.parse_args()

# Read in the pattern list from a file
with open(args.pattern_file, 'r') as pattern_file:
    pattern_list = [line.strip() for line in pattern_file]

# Loop through the fasta file and keep or remove sequences based on the pattern list
with open(args.fasta_file, 'r') as fasta_file:
    for record in SeqIO.parse(fasta_file, 'fasta'):
        keep_seq = False
        
        for pattern in pattern_list:
            if args.exact:
                if record.id == pattern:
                    keep_seq = True
                    break #no need to continue checking
            else:
                if re.search(pattern, record.id):
                    keep_seq = True
                    break

        if (not args.remove and keep_seq) or (args.remove and not keep_seq):
            SeqIO.write(record, sys.stdout, 'fasta')