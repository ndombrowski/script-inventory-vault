
# Data processing scripts

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

## Prune alignment

- **Script**:  [`alignment_pruner.pl`](../scripts/data_processing/alignment_pruner.pl)
- **Description**: Script to filter gappy or unconserved columns from a sequence alignment (gap-based, chi2)
- **Dependencies**: MooseX (`install bioconda::perl-moosex-app`), `cpanm List::MoreUtils`, `cpanm Bio::AlignIO`, ...
- **Tags**: #Phylogeny, #pruning, #alignment, #alignment_filtering
- **Source**: https://github.com/novigit/davinciCode/blob/master/perl/alignment_pruner.pl
- **Usage**: `perl alignment_pruner.pl--file alignment.fna --chi2_prune f0.05 > pruned.aln`
- **Input**: Sequence alignment
- **Output**: Pruned sequence alignment

## Filter fasta (perl)

- **Script**:  [`screen_list_new.pl`](../scripts/data_processing/screen_list_new.pl)
- **Description**:  Filter a fasta file for/against a list of entry names. If a third argument is given the list entries will be kept
- **Dependencies**:  
- **Tags**: #FASTA, #Filter_entries
- **Usage**: `perl screen_list.pl <list> <fasta file> <<keep?>>`
- **Input**: Fasta file
- **Output**: Filtered fasta file

## Filter fasta (python)

- **Script**:  [`filter_fasta.py`](../scripts/data_processing/filter_fasta.py)
- **Description**: Filter sequences from a fasta file based on patterns or exact matches stored in a list. The elements of the list can either be kept or removed
- **Dependencies**: biopython
- **Tags**: #FASTA, #Filter_entries
- **Usage**: `python filter_fasta.py -i genome.fna -l list.txt -o results/filtered.fna --keep_hits --exact`
- **Input**: Fasta file
- **Output**: Filtered fasta file


## Drop gappy sequence

- **Script**:  [`faa_drop.py`](../scripts/data_processing/faa_drop.py)
- **Description**: Drops sequences from a sequence alignment if that sequences has too many gaps
- **Dependencies**: bioperl
- **Tags**: #alignment, #alignment_filtering 
- **Usage**: To remove sequences with 50% gaps: `python fasta_drop.py original_aln.fas new_aln.fas 0.5`
- **Input**: Alignment
- **Output**: Trimmed alignment


## Split fasta file

- **Script**:  [`Split_Multifasta.py`](../scripts/data_processing/Split_Multifasta.py)
- **Description**: This script takes multifasta file and splits it into several files with a desired amount of sequences
- **Dependencies**: biopytjon
- **Tags**: #FASTA
- **Usage**: `python -m input.fasta -n 1000`
- **Input**: Fasta file
- **Output**: Multiple fasta files 

## Find duplicated marker genes 

- **Script**:  [`find_dubs.py`](../scripts/data_processing/find_dubs.py)
- **Description**: Process COG marker files and find duplicates for easier screening of phylogenetic trees
- **Dependencies**: 
- **Tags**: #Phylogeny, #Quality_control  
- **Usage**: `python3 find_dubs.py --inputfolder FileLists/split/ --search-prefix COG --output FileLists/duplicated_cogs.txt`
- **Input**: Output from a hmmsearch split by markers of interest. I.e. COG0001.txt, COG0002.txt
- **Output**: List of duplicated marker genes found in genomes of interest


## Filter hmmsearch domain search results for non-overlapping domains

- **Script**:  [`filter_domain_hmm.py`](../scripts/data_processing/filter_domain_hmm.py)
- **Description**: Take the parsed output of a hmmsearch domain search and filter the table and discard overlapping domain hits. Note that the filtering here allows for no overlaps, if a little overlap should be allowed then the sub-process in `parse_dbCAN.py` could be considered as well.
- **Dependencies**: Pandas
- **Tags**: #Quality_control , #Filter_entries, #Hmmsearch, #Protein_domains
- **Usage**: 
```bash
	# Clean table and only keep protein ID, protein length, KO, KO_length, c-Evalue, protein_start, protein_end, hmm_from, hmm_to, protein_coverage, hmm_coverage
# Filter by removing hits with cEvalues <= 1E-3
# Filter by removing hits with hmm_coverage lower than  0.5
sed 's/ \+ /\t/g' 03_data/annotations/manual/KEGG/domain_results.txt \
  | sed '/^#/d' \
  | sed 's/ /\t/g' \
  | awk -F'\t' -v OFS='\t' '($12 + 0) <= 1E-3' \
  | awk -F'\t' -v OFS='\t' '{print $1, $3, $4, $6, $12, $18, $19, $17, $16, ($19-$18)/$3, ($17-$16)/$6}' \
  | awk -F'\t' -v OFS='\t' '$11 >= 0.5' > 03_data/annotations/manual/KEGG/domain_results_red_e_cutoff.txt

# Filter hits to find the most reasonable hit for each protein stretch
python3 01_workflows_and_../scripts/filter_domain_hmm.py \
  -i 03_data/annotations/manual/KEGG/domain_results_red_e_cutoff.txt \
  -o 03_data/annotations/manual/KEGG/domain_results_red_e_cutoff_filtered.txt
```
- **Input**: Filtered hmmsearch table
- **Output**: Domain-filtered hmmsearch table
- **Related Snippets**:


## Parse a transdecoder gtf to get cleaner names

- **Script**:  [`edit_transdecoder_gtf.py`](../scripts/data_processing/edit_transdecoder_gtf.py)
- **Description**: Clean gene IDs and transcript IDs in a transdecoder gtf file and shorten them
- **Dependencies**: 
- **Tags**: #GTF, #Transdecoder, #File_cleaning
- **Usage**: `python edit_transdecoder_gtf.py --input transdecoder.gtf --output transdecoder_clean.gft`
- **Input**: Transdecoder gtf
- **Output**: Cleaned transdecoder gtf
- **Related Snippets**:


## Summarize the length of sequences in a fasta file

- **Script**:  [`summarize_protein_length.py`](../scripts/data_processing/summarize_protein_length.py)
- **Description**: Script to analyze protein lengths from a FASTA file and providing basic summary values (min, max, mean, median 95th percentile length and proteins longer than the 95th percentile or custom length value)
- **Dependencies**: Numpy, matplotlib
- **Tags**: #FASTA, #summarize_data 
- **Usage**: `python summarize_proteins.py -i nina_test/transcripts.fasta.transdecoder.pep`
- **Input**: nucleotide or protein fasta file
- **Output**: Basic summary values
- **Related Snippets**:

## Concatenate FASTA alignments

- **Script**:  [`catfasta2phyml.pl`](../scripts/data_processing/catfasta2phyml.pl)
- **Description**: Script to concatenate FASTA alignments to PHYML, PHYLIP, or FASTA format
- **Dependencies**: 
- **Tags**: #Phylogeny, #alignment  
- **Usage**: `perl catfasta2phyml.pl -f -c Alignment/dedup/BMGE/h0.55/* > Alignment/dedup/concatenated/Elife_25_BacV5_v2.faa`
- **Input**: Several trimmed alignments
- **Output**: Concatenated alignment
- **Related Snippets**:


## Replace strings in a tree file 

- **Script**:  [`Replace_tree_names.pl`](../scripts/data_processing/Replace_tree_names.pl)
- **Description**: Take a tab-delimited, 2-column file with original string and string to replace and use this to replace strings in a treefile
- **Dependencies**: 
- **Tags**: #Phylogeny , #searching 
- **Usage**: `perl Replace_tree_names.pl names_to_replace Elife_25_BacV5_v2.treefile > Elife_25_BacV5_v2.treefile_renamed`
- **Input**: List of search-replace terms and treefile
- **Output**: Renamed treefile
- **Related Snippets**:


## Parse results from IPRscan

- **Script**:  [`parse_IPRdomains_vs2_GO_2_ts_sigP.py`](../scripts/data_processing/parse_IPRdomains_vs2_GO_2_ts_sigP.py)
- **Description**: Parse IPRscan result yielding a tab-delimited file with one gene per line and following columns separated  by tabs: GeneID IPRdomain   IPRdescription  PFAMdomain  PFAMdescription KEGGresults
- **Dependencies**: biopython
- **Tags**: #data_parsing, #IPRscan, #annotations
- **Usage**: `python parse_IPRdomains_vs2_GO_2_ts_sigP.py -s thiopac_sulfur_genes.faa -i thiopac_sulfur_genes.faa.tsv -o thiopac_sulfur_genes.faa_parsed.tsv`
- **Input**: Fasta_file with all proteins, Result file of IPR scan
- **Output**: For each protein all relevant domain information
- **Related Snippets**:


## Extract information from a Uniprot json file

- **Script**:  [`uniprot_extract_json.py`](../scripts/data_processing/uniprot_extract_json.py)
- **Description**:  For a given uniprot ID extract the description
- **Dependencies**: json, pandas
- **Tags**: #Uniprot, #data_parsing 
- **Usage**: `python extract_json.py -i results.json  -o uniprot_to_name.txt`
- **Input**: Uniprot json file
- **Output**: Link uniprot name to uniprot description
- **Related Snippets**: [[bash#Do a uniprot request]]


## Filter hmmsearch dbCAN domain hits

- **Script**:  [`parse_dbCAN.py`](../scripts/data_processing/parse_dbCAN.py)
- **Description**: Take the domain table from a dbCAN-hmmsearch search, filters by E-value and coverage, removes overlapping domains, and provides both detailed and summary outputs. Note that the filtering here is a bit less stringent as in `filter_domain_hmm.py` as we allow for some overlap.
- **Dependencies**: Pandas
- **Tags**: #Quality_control , #Filter_entries, #Hmmsearch, #Protein_domains, #CAZy
- **Usage**: 
```bash
## Run search
hmmsearch \
    --tblout results/sequence_results.txt \
    --domtblout results/domain_results.txt \
    --notextw \
    --cpu 4 \
    /zfs/omics/projects/bioinformatics/databases/dbCAN/dbCAN-HMMdb-V14.txt \
    GCF_000970205.faa

## Parse the result (example)
python /zfs/omics/projects/bioinformatics/databases/dbCAN/parse_dbCAN.py  \
	-i results/domain_results.txt \
	-m /zfs/omics/projects/bioinformatics/databases/dbCAN/fam-substrate-mapping-08262025.tsv \
	-o results \
	-e 1e-5 -c 0.30
```
- **Input**:  hmmsearch domain table
- **Output**: Domain-filtered hmmsearch table
- **Related Snippets**:


## Filter diamond blastp hydDB domain hits

- **Script**:  [`parse_diamond_hydDB.py`](../scripts/data_processing/parse_diamond_hydDB.py)
- **Description**: Take the output from a hydDB-diamond blastp search, filters by E-value and it also discards hits below a certain e-value thresholds and below the following percent identities (as recommended [here](https://github.com/GreeningLab/HydDB))
- **Dependencies**: Pandas
- **Tags**: #Quality_control , #Filter_entries, #Diamond,, #Hydrogenase
- **Usage**: 
```bash
## Run search
diamond blastp -q data/genomes.faa \
    --more-sensitive --evalue 1e-3 \
    --threads 5 --max-target-seqs 20 \
    --db /zfs/omics/projects/bioinformatics/databases/hyddb/release2022/hyddb \
    --outfmt 6 qseqid qtitle qlen sseqid salltitles slen qstart qend sstart send evalue bitscore length pident \
    --out results/results.txt

# Parse the data
python /zfs/omics/projects/bioinformatics/databases/hyddb/release2022/parse_diamond_hydDB.py \
    -i results/results.txt \
    -o results/hyddb_parsed.tsv \
    --evalue 1e-5
```
- **Input**:  diamond blastp output table (make sure the right --outfmt is used)
- **Output**: Filtered table
- **Related Snippets**:


## Fix Prokka-generated GenBank files using the original FASTA file as reference

- **Script**:  [`fix_prokka_gbk.py`](../scripts/data_processing/fix_prokka_gbk.py)
- **Description**: Reads contig names from the original FASTA file, then reads the GenBank file and finds concatenated LOCUS lines, then matches each LOCUS to its original contig name and properly separates the contig name from the sequence length. Note: the delimiter is currently not active to work with the FeGenie pipeline
- **Dependencies**: 
- **Tags**: #gbk , #Prokka, #Prodigal
- **Usage**: 
```bash
## Fix several gbk headers
python fix_prokka_gbk.py --fasta_dir data/genomes -gbk_dir data/prokka --output_dir data/prokka_fixed
```
- **Input**:  Folder with gbk files (prokka gbk files) and folder with corresponding genomes (prokka fna files)
- **Output**: Gbk files with fixed locus tag
- **Related Snippets**: