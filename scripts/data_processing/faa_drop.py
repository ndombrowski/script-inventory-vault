#Drops sequences with too many gaps
#adopted from: https://www.biostars.org/p/434389/

#run as follows to remove sequences with 50% gaps:
#python fasta_drop.py original_aln.fas new_aln.fas 0.5

import sys
from Bio import SeqIO

FastaFile = open(sys.argv[1], 'r')
FastaDroppedFile = open(sys.argv[2], 'w')
drop_cutoff = float(sys.argv[3])

if (drop_cutoff > 1) or (drop_cutoff < 0):
    print('\n Sequence drop cutoff must be in 0-1 range !\n')
    sys.exit(1)

for seqs in SeqIO.parse(FastaFile, 'fasta'):
    name = seqs.id
    seq = seqs.seq
    seqLen = len(seqs)
    gap_count = 0
    for z in range(seqLen):
        if seq[z]=='-':
            gap_count += 1
    if (gap_count/float(seqLen)) >= drop_cutoff:
        print(sys.argv[1] + "\tremoved:"  + ' %s' % name)
    else:
        SeqIO.write(seqs, FastaDroppedFile, 'fasta')

#get the sequence counts
records1 = list(SeqIO.parse(sys.argv[1], "fasta"))
records2 = list(SeqIO.parse(sys.argv[2], "fasta"))
diff = len(records1) - len(records2)

#print("From " + str(len(records1)) + " sequences " + str(diff) + " sequences were removed")

FastaFile.close()
FastaDroppedFile.close()
