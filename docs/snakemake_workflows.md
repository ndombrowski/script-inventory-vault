
Here, you find an explanation of useful Snakemake workflows.

**Table of contents:**

```table-of-contents
title: 
style: nestedList # TOC style (nestedList|nestedOrderedList|inlineFirstLevel)
minLevel: 1 # Include headings from the specified level
maxLevel: 6 # Include headings up to the specified level
includeLinks: true # Make headings clickable
hideWhenEmpty: false # Hide TOC if no headings are found
debugInConsole: false # Print debug info in Obsidian console
```

## Dotplot with minimap2/pafCoordsDotPlotly

- **Script**:  [`minimapdot_readme.md`](../scripts/snakemake_workflows/minimapdot/minimapdot_readme.md)
- **Description**: Generate genome dotplots by aligning all possible combinations of genomes with minimap and generate dotplots via an R package
- **Dependencies**: snakemake, conda/mamba
- **Tags**: #Genome_assembly, #alignment, #visualization, #dotplot  
- **Usage**: `snakemake --snakefile workflow/Snakefile   --configfile config/config.yaml   --cores 1 --use-conda --conda-frontend mamba   --conda-prefix workflow/.snakemake/conda/
- **Input**: Genome fasta files and their name, taxon, path as described in the mapping file
- **Output**: 
	- PAF for each genome comparison
	- PNG/HTML for all dotplot combinations


## Dotplot with LAST

- **Script**:  [`snakelast_readme.md`](../scripts/snakemake_workflows/snakelast/snakelast_readme.md)
- **Description**: Generate genome dotplots by aligning all possible combinations of genomes with LAST and generate dotplots via an last-dotplot
- **Dependencies**: snakemake, conda/mamba
- **Tags**: #Genome_assembly, #alignment, #visualization, #dotplot  
- **Usage**: `snakemake --snakefile workflow/Snakefile   --configfile config/config.yaml   --cores 1 --use-conda --conda-frontend mamba   --conda-prefix workflow/.snakemake/conda/
- **Input**: Genome fasta files and their name, taxon, path as described in the mapping file
- **Output**: 
	- LAST alignment for each genome comparison
	- PNG for all dotplot combinations