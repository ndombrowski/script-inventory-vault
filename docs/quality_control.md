## Check strandedness from de novo assembly

- **Script**:  [`check_strand_incl_samtools.py`](scripts/quality_control/check_strand_incl_samtools.py)
- **Description**: Check correct strandedness from RNA-seq data 
- **Dependencies**: subprocess, samtools
- **Tags**: #RNA-seq, #Alignment, #Strandedness, #BAM_processing, #Quality_control
- **Usage**: `python check_strand_incl_samtools.py -b File.bam -s R1_strand_info.txt -o strand_table.txt`
- **Input**: Bam file
- **Output**: 
	- Flag for each mapped R1 read (R1_strand_info.txt)
	- Reads on plus versus minus strand (and ratio) for all R1 reads (strand_table.txt)


## Extract sequence length and GC

- **Script**:  [`fasta_length_gc.py`](scripts/quality_control/fasta_length_gc.py)
- **Description**: Calculate the length and GC content for each record of a fasta file
- **Dependencies**: biopython
- **Tags**: #Quality_control, #FASTA
- **Usage**: `python length_gc.py example.fasta`
- **Input**: Nucleotide fasta file
- **Output**: Table with the record id, gc content and sequence length


