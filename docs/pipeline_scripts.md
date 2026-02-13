
# Pipeline scripts

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

## Pipeline to generate consensus amplicon sequences

- **Script**:  [`ngspeciesid_pipeline_polished.sh`](../scripts/ngspeciesid_pipeline_polished.sh)
- **Description**: Pipeline to run NGSpeciesID to cluster and form a consensus sequences from long-read amplicon data. The output is further parsed to combine the output per sample into a single FASTA file
- **Dependencies**: NGSpeciesID
- **Tags**: #Amplicon, #consensus_sequences, #clustering, #Long-read-sequencing
- **Usage**: `ngspeciesid_pipeline_polished.sh -r <desired_read_nr> -a <aln_thres> -m <mapped_thres> -d <run_dir> -i <input_dir> -o <output_dir> -l <log_dir> -p <polishing_method>`
- **Input**: A number of FASTQ files in the specified input directory
- **Output**: A single FASTA file per FASTQ file

## Autocycler (bash mode)

- **Script**:  [`autocycler_bash.sh`](../scripts/autocycler_bash.sh)
- **Description**: Autocycler is a tool to generate genome assemblies from FASTQ files using multiple assemblers. This is a bash script that uses GNU parallel to run run autocycler on FASTQ files from different samples. Assemblies are generated in parallel with canu, flye, miniasm, necat, nextdenovo and raven.
- **Dependencies**: Autocycler, GNU parallel
- **Tags**: #Genome_assembly, #Pipeline, #Short-read
- **Usage**: `bash autocycler_bash.sh -d folder_with_fastq -t 10 -m 5`
- **Input**:  Folder with FASTQ files
- **Output**: results folder with different outputs for each step of the analysis. The combined assembly can be found in results/autocycler_out


## Autocycler (SLURM mode)

- **Script**:  [`autocycler_array.sh`](../scripts/autocycler_array.sh)
- **Description**: Autocycler is a tool to generate genome assemblies from FASTQ files using multiple assemblers. This is a SLURM script that uses GNU parallel to run run autocycler on FASTQ files from different samples. Assemblies are generated in parallel with canu, flye, miniasm, necat, nextdenovo and raven.
- **Dependencies**: Autocycler, GNU parallel
- **Tags**: #Genome_assembly, #Pipeline, #Short-read
- **Usage**: Before submitting, edit the script and provide the path to the data folder and the minimum cpus per assembly depending on the amount of resources the script is requesting. In this example two genomes are reconstructer (array 1-2) with 32 cpus per array. `sbatch autocycler_array.sh`
- **Input**:  Folder with FASTQ files
- **Output**: results folder with different outputs for each step of the analysis. The combined assembly can be found in results/autocycler_out

## FeGenie (edited py script)

- **Script**:  [`FeGenie_gbk.py`](../scripts/pipeline_scripts/FeGenie_gbk.py)
- **Description**: [FeGenie](https://github.com/Arkadiy-Garber/FeGenie) is HMM-based identification and categorization of iron genes and iron gene operons in genomes and metagenome assemblies. This is an edited version that can be placed in the conda fegenie bin folder if one wants to work with prokka/prodigal gbk files as the v1.2 of the script otherwise generates an incorrect orf id
- **Dependencies**: Autocycler, GNU parallel
- **Tags**: #annotations , #iron
- **Usage**: For more information, see [here](https://scienceparkstudygroup.github.io/ibed-bioinformatics-page/source/core_tools/fegenie.html)
- **Input**:  See above
- **Output**: See above