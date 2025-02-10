
## Prune alignment

- **Script**:  [`alignment_pruner.pl`](scripts/data_processing/alignment_pruner.pl)
- **Description**: Script to filter gappy or unconserved columns from a sequence alignment (gap-based, chi2)
- **Dependencies**: MooseX (`install bioconda::perl-moosex-app`), `cpanm List::MoreUtils`, `cpanm Bio::AlignIO`, ...
- **Tags**: #Phylogeny, #pruning, #alignment, #alignment_filtering
- **Source**: https://github.com/novigit/davinciCode/blob/master/perl/alignment_pruner.pl
- **Usage**: `perl alignment_pruner.pl--file alignment.fna --chi2_prune f0.05 > pruned.aln`
- **Input**: Sequence alignment
- **Output**: Pruned sequence alignment

## Filter fasta (perl)

- **Script**:  [`screen_list_new.pl`](scripts/data_processing/screen_list_new.pl)
- **Description**:  Filter a fasta file for/against a list of entry names. If a third argument is given the list entries will be kept
- **Dependencies**:  
- **Tags**: #FASTA, #Filter_entries
- **Usage**: `perl screen_list.pl <list> <fasta file> <<keep?>>`
- **Input**: Fasta file
- **Output**: Filtered fasta file

## Filter fasta (python)

- **Script**:  [`screen_fasta.py`](scripts/data_processing/screen_fasta.py)
- **Description**: Filter sequences from a fasta file based on patterns or exact matches stored in a list. The elements of the list can either be kept or removed
- **Dependencies**: biopython
- **Tags**: #FASTA, #Filter_entries
- **Usage**: `python screen_fasta.py file.fasta pattern_file <--remove> <--exact>`
- **Input**: Fasta file
- **Output**: Filtered fasta file


## Drop gappy sequence

- **Script**:  [`faa_drop.py`](scripts/data_processing/faa_drop.py)
- **Description**: Drops sequences from a sequence alignment if that sequences has too many gaps
- **Dependencies**: bioperl
- **Tags**: #alignment, #alignment_filtering 
- **Usage**: To remove sequences with 50% gaps: `python fasta_drop.py original_aln.fas new_aln.fas 0.5`
- **Input**: Alignment
- **Output**: Trimmed alignment


## Split fasta file

- **Script**:  [`Split_Multifasta.py`](scripts/data_processing/Split_Multifasta.py )
- **Description**: 
- **Dependencies**: 
- **Tags**: 
- **Usage**: 
- **Input**: 
- **Output**: 