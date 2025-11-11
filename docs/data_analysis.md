# Data analysis scripts

**Table of contents:**

```table-of-contents
title: 
style: nestedList # TOC style (nestedList|nestedOrderedList|inlineFirstLevel)
minLevel: 2 # Include headings from the specified level
maxLevel: 6 # Include headings up to the specified level
includeLinks: true # Make headings clickable
hideWhenEmpty: false # Hide TOC if no headings are found
debugInConsole: false # Print debug info in Obsidian console
```

## In silico PCR

- **Script**:  [`insilico_pcr.py`](../scripts/data_analysis/insilico_pcr.py)
- **Description**: Simulate PCR amplicons from a template sequence using user-specified primers. Handles ambiguous bases (IUPAC) and fuzzy primer matching.
- **Dependencies**: bioperl, regex  
- **Tags**: #PCR, #Amplicon, #data_parsing
- **Source**: 
- **Usage**: 
	```
  	 python scripts/insilico_pcr.py \
    --fasta data/genome/LjRoot44.fna \
    --fasta_out amplicon.fasta \
    --fwd_primer AGAGTTTGATCMTGGCTCAG \
    --rev_primer CGGTTACCTTGTTACGACTT \
    --max_errors 2 \
    --min_len 100 \
    --max_len 2000
    ```
- **Input**: Fasta file with one or multiple sequences, primers
- **Output**: In silico amplicon PCR result


## Pivot vsearch results

- **Script**:  [`pivot_vsearch.py`](../scripts/data_analysis/pivot_vsearch.py)
- **Description**: Takes the tsv output from vsearch (settings: blast6out and allpairs_global) and makes a hierarchical output of sequence identities
- **Dependencies**: pandas, numpy  
- **Tags**: #vsearch, #sequence_identity, #data_parsing
- **Source**: 
- **Usage**: 
	```
  	 python pivot_vsearch.py
    ```
- **Input**: TSV file with vsearch results 
- **Output**: hierarchical table with sequence identities


## Generate OTU tables from idxstats output

- **Script**:  [`idxstats_to_matrix.py`](../scripts/data_analysis/idxstats_to_matrix.py)
- **Description**: Takes a list of idxstats file from different samples and converts it to an OTU-like table. 
- **Dependencies**: pandas, numpy  
- **Tags**: #read_mapping, #table_generation, #idxstats
- **Source**: 
- **Usage**: 
	```
  	 python scripts/idxstats_to_matrix.py -i results/mapping_counts/ -o results/mapping_counts/
    ```
- **Input**: TSV file with the following name pattern `{barcode}_stats.tsv`. barcode can also be a sample id
- **Output**: OTU-like table with counts/sample


## Generate OTU tables from minimap2 PAF output

- **Script**:  [`paf_to_matrix.py`](../scripts/data_analysis/paf_to_matrix.py)
- **Description**: Takes a list of minimap2 paf files from different samples and converts it to an OTU-like table on genus rank 
- **Dependencies**: pandas , pathlib, matplotlib
- **Tags**: #read_mapping, #table_generation, #paf
- **Source**: 
- **Usage**: 
	```
  	 python scripts/paf_to_matrix.py -i results/mapping_counts/ -o results/mapping_counts/ -t data/genome_to_genus.tsv -s results/seqkit/fastq_filtered.tsv
    ```
- **Input**: Minimap2 paf files, a genome to genus mapping and optionally the path to a seqkit stats output (-Toa format)
- **Output**: OTU-like table with counts/sample on genome and genus rank. Also a table on genome rank that indicates multi-mappers
