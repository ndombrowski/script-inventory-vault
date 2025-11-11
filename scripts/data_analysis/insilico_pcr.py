#!/usr/bin/env python3
"""
Simulate PCR amplicons from a template sequence using user-specified primers.
Handles ambiguous bases (IUPAC) and fuzzy primer matching.

Online tools for sanity checking:
https://en.vectorbuilder.com/tool/sequence-alignment/f64b388e-4ba1-407a-a4d9-09b1667f0547.html
https://primerdigital.com/tools/epcr.html (not gives non rc for fwd_rc+rev)

python scripts/insilico_pcr.py \
    --fasta data/genome/LjRoot44.fna \
    --fasta_out amplicon.fasta \
    --fwd_primer AGAGTTTGATCMTGGCTCAG \
    --rev_primer CGGTTACCTTGTTACGACTT \
    --max_errors 2 \
    --min_len 100 \
    --max_len 2000
"""

import argparse
from Bio import SeqIO
from Bio.Seq import Seq 
import regex

# --------------------- Argument parsing --------------------- #
parser = argparse.ArgumentParser(
    description="Simulate PCR amplicons from a template FASTA using forward and reverse primers."
)
parser.add_argument("--fasta", required=True, help="Input template FASTA file")
parser.add_argument("--fasta_out", required=True, help="Output FASTA file for extracted amplicons")
parser.add_argument("--fwd_primer", required=True, help="Forward primer sequence (IUPAC allowed)")
parser.add_argument("--rev_primer", required=True, help="Reverse primer sequence (IUPAC allowed)")
parser.add_argument("--max_errors", type=int, default=1, help="Maximum number of errors allowed in fuzzy primer matching")
parser.add_argument("--min_len", type=int, default=100, help="Minimum amplicon length")
parser.add_argument("--max_len", type=int, default=2000, help="Maximum amplicon length")

args = parser.parse_args()

fasta = args.fasta
fasta_out = args.fasta_out
fwd_primer = args.fwd_primer
rev_primer = args.rev_primer
max_errors = args.max_errors
min_len = args.min_len
max_len = args.max_len


# --------------------- IUPAC mapping for ambiguous bases -------------------- #
IUPAC = {
    "A": "A", "C": "C", "G": "G", "T": "T",
    "R": "[AG]", "Y": "[CT]", "S": "[GC]", "W": "[AT]",
    "K": "[GT]", "M": "[AC]", "B": "[CGT]", "D": "[AGT]",
    "H": "[ACT]", "V": "[ACG]", "N": "[ACGT]"
}

# ----------------------------- Define functions ----------------------------- #
def iupac_to_regex(seq):
    """Convert IUPAC pattern to regex"""
    new_string = []
    
    for base in seq:
        base = base.upper()
        if base not in IUPAC:
            raise KeyError(f"Invalid IUPAC base '{base}' in sequence '{seq}' ")
        new_string.append(IUPAC[base])
        
    return "".join(new_string)

def fuzzy_summary(match):
    """Return summary of fuzzy match errors"""
    subs, ins, dels = match.fuzzy_counts
    total_errors = sum(match.fuzzy_counts)
    if total_errors == 0:
        return "exact match"
    else:
        return f"fuzzy match with {subs} substitutions, {ins} insertions, {dels} deletions (total errors: {total_errors})"
    

# ---------------------------- Read in Fasta file ---------------------------- #
# use SeqIO.read when working with a single fasta
# use SeqIO.parse when working with multiple sequences
records = list(SeqIO.parse(fasta, "fasta")) 
record_dict = {record.id: record for record in records}


# ----------------------------- Deal with primers ---------------------------- #
fwd_primer_regex = iupac_to_regex(fwd_primer)
fwd_primer_rc_regex = iupac_to_regex(str(Seq(fwd_primer).reverse_complement()))
rev_primer_regex = iupac_to_regex(rev_primer)
rev_primer_rc_regex = iupac_to_regex(str(Seq(rev_primer).reverse_complement()))


# --------------------- Find positions were primers match -------------------- #
fwd_matches = []
fwd_rc_matches = []
rev_matches = []
rev_rc_matches = []

for record in records:
    seq_string = str(record.seq).upper()
    header_string = record.id

    # Search all four orientations
    fwd_hits = list(regex.finditer(f"({fwd_primer_regex}){{e<={max_errors}}}", seq_string, regex.IGNORECASE | regex.BESTMATCH ))
    fwd_rc_hits = list(regex.finditer(f"({fwd_primer_rc_regex}){{e<={max_errors}}}", seq_string, regex.IGNORECASE | regex.BESTMATCH))
    rev_hits = list(regex.finditer(f"({rev_primer_regex}){{e<={max_errors}}}", seq_string, regex.IGNORECASE | regex.BESTMATCH))
    rev_rc_hits = list(regex.finditer(f"({rev_primer_rc_regex}){{e<={max_errors}}}", seq_string, regex.IGNORECASE | regex.BESTMATCH))

    # Store matches with contig id
    for m in fwd_hits:
        fwd_matches.append((header_string, m))
    for m in fwd_rc_hits:
        fwd_rc_matches.append((header_string, m))
    for m in rev_hits:
        rev_matches.append((header_string, m))
    for m in rev_rc_hits:
        rev_rc_matches.append((header_string, m))


# -------------------- Print information about mismatches -------------------- #
print("\nForward primer matches:")
for id, m in fwd_matches:
    print(f"contig={id}  start={m.start()}, end={m.end()}, {fuzzy_summary(m)}")

print("\nForward RC primer matches:")
for id, m in fwd_rc_matches:
    print(f"contig={id}  start={m.start()}, end={m.end()}, {fuzzy_summary(m)}")

print("\nReverse primer matches:")
for id, m in rev_matches:
    print(f"contig={id}  start={m.start()}, end={m.end()}, {fuzzy_summary(m)}")

print("\nReverse RC primer matches:")
for id, m in rev_rc_matches:
    print(f"contig={id}  start={m.start()}, end={m.end()}, {fuzzy_summary(m)}")



# -------------------------- Find sensible amplicons ------------------------- #
amplicons = []
contigs_with_sensible = set()  # Track contigs with "normal" amplicons

# fwd + rev_rc (original orientation)
for f_contig_id, f in fwd_matches:
    for r_contig_id, r in rev_rc_matches:
        if f_contig_id == r_contig_id and r.start() > f.end():
            length = r.end() - f.start()
            if min_len <= length <= max_len:
                amplicons.append((f_contig_id, f, r, length, "fwd+rev_rc"))
                contigs_with_sensible.add(f_contig_id)

# fwd_rc + rev (flipped orientation)
for f_contig_id, f in fwd_rc_matches:
    for r_contig_id, r in rev_matches:
        if r_contig_id == f_contig_id and f.start() > r.end():
            length = f.end() - r.start()
            if min_len <= length <= max_len:
                amplicons.append((f_contig_id, f, r, length, "fwd_rc+rev"))
                contigs_with_sensible.add(f_contig_id)


# ---------------------- Handle single-end edge cases ----------------------- #
edge_distance = 1500  # configurable if desired

for record in records:
    contig_id = record.id
    if contig_id in contigs_with_sensible:
        continue  # Skip edge-case search for this contig

    seq_len = len(record.seq)

    # Forward primer near contig end
    for f in [m for cid, m in fwd_matches if cid == contig_id]:
        rev_hits_here = [r for cid, r in rev_rc_matches + rev_matches if cid == contig_id]
        if not rev_hits_here and seq_len - f.end() <= edge_distance:
            amp_seq = str(record.seq[f.start():])
            length = len(amp_seq)
            if min_len <= length <= max_len:
                amplicons.append((contig_id, f, None, length, "fwd_to_end"))
                print(f"Edge amplicon: {contig_id} fwd_to_end start={f.start()+1} end={seq_len} len={length}")

    # Reverse primer near contig start
    for r in [m for cid, m in rev_rc_matches + rev_matches if cid == contig_id]:
        fwd_hits_here = [f for cid, f in fwd_matches + fwd_rc_matches if cid == contig_id]
        if not fwd_hits_here and r.start() <= edge_distance:
            amp_seq = str(record.seq[:r.end()])
            length = len(amp_seq)
            if min_len <= length <= max_len:
                amplicons.append((contig_id, None, r, length, "rev_to_start"))
                print(f"Edge amplicon: {contig_id} rev_to_start start=1 end={r.end()} len={length}")

if not amplicons:
    raise ValueError("No plausible amplicon pairs found (check length thresholds or primer orientation)")

print(f"Total plausible amplicons: {len(amplicons)}")


# ------------------ Extract and save the amplicon sequence ------------------ #
with open(fasta_out, "w") as out_f:
    for n, (contig_id, f_match, r_match, length, orientation) in enumerate(amplicons, start=1):
        record = record_dict[contig_id]

        if orientation == "fwd+rev_rc":
            amp_seq = str(record.seq[f_match.start():r_match.end()])
            start, end = f_match.start(), r_match.end()
        elif orientation == "fwd_rc+rev":
            amp_seq = str(record.seq[r_match.start():f_match.end()].reverse_complement())
            start, end = r_match.start(), f_match.end()
        elif orientation == "fwd_to_end":
            amp_seq = str(record.seq[f_match.start():])
            start, end = f_match.start(), len(record.seq)
        elif orientation == "rev_to_start":
            amp_seq = str(record.seq[:r_match.end()])
            start, end = 0, r_match.end()
        else:
            continue  # skip unknown orientation
        
        out_f.write(f">{record.id}_from{start}_to{end}_len{length}_orientation_{orientation}\n")
        for j in range(0, len(amp_seq), 80):
            out_f.write(amp_seq[j:j+80] + "\n")

        print(f"Amplicon {n}: Contig={contig_id} start={start+1} end={end} inclusive length={end-start} orientation={orientation}")
