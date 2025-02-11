
# Workflow management scripts

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

## Slurm basic example script

- **Script**:  [`slurm_minimal_example.sh`](../scripts/workflow_management/slurm_minimal_example.sh)
- **Description**: Example script to run a sbatch script while also loading a conda environment
- **Dependencies**: 
- **Tags**: #SLURM 
- **Usage**: `sbatch slurm_minimal_example.sh`
- **Input**: 
- **Output**: 
- **Related Snippets**:


## Submit an R job via slurm

- **Script**:  [`slurm_submit_r.sh`](../scripts/workflow_management/slurm_submit_r.sh)
- **Description**: Example script to run a Rscript via sbatch
- **Dependencies**: 
- **Tags**: #R, #SLURM 
- **Usage**: `sbatch slurm_submit_r.sh`
- **Input**: 
- **Output**: 
- **Related Snippets**:



## Slurm sbatch array

- **Script**:  [`slurm_array_example.sh`](../scripts/workflow_management/slurm_array_example.sh)
- **Description**: Example for submitting an Slurm array job. Includes flexible basename extraction from multiple fastq files and only execution of commands if output file does not exist
- **Dependencies**: 
- **Tags**: #SLURM, #ARRAY
- **Usage**: `sbatch slurm_array_example.sh`
- **Input**: 
- **Output**: 
- **Related Snippets**: