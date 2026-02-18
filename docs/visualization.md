# Data visualization scripts

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

## Genome visualization

- **Script**:  [`generate_circos_plot.py`](../scripts/visualization/generate_circos_plot.py)
- **Description**: Generate circos plots as png from Genbank files. If desired also marks genes of interest in the plot.
- **Dependencies**: pycirclize, numpy, matplotlib
- **Tags**: #visualization, #genome
- **Usage**:  `python python generate_circos_plot.py -i genome.gbk  -o circos_plot.pdf  -g genes_of_interest.txt` 
- **Input**: Genebank files
- **Output**
	- Png for genome of interest, Example files here: /zfs/omics/projects/sargo/j4_assembly_analysis/results/v3_trycycler/dnaapler/prokka
	- ![[Pasted image 20250210110128.png|200]]


## Format Figree

- **Script**:  [`formatFigtree3.pl`](../scripts/visualization/formatFigtree3.pl)
- **Description**: Format a newick tree to a figtree format, coloring the leaves depending on the taxa (or anything it's giving in the list with color)
- **Dependencies**: NA
- **Tags**:  #Phylogeny , #Figtree
- **Usage**:  Get list of treefiles with `ls -d "$PWD"/*renamed | tac - > listOfFiles2.list` followed by `perl formatFigtree3.pl listOfFiles2.list -C color_mapping2 -sl 10` to format the list of trees
- **Input**: List of figtree files
- **Output**: List of formatted figrees


## Render iqtree treefile (python )

- **Script**:  [`parse_tree.py`](../scripts/visualization/parse_tree.py)
- **Description**: Takes an iqtree treefile and a color file as input and outputs a pdf with the tree as well as a newick file for easier reading in with figtree.
- **Dependencies**: ete3 (pip3 install PyQt5 ete3, otherwise TreeStyle is not found)
- **Tags**:  #Phylogeny , #Figtree
- **Usage**:  `python parse_tree.py --tree trimmed.faa.treefile --colors colors --output py_tree.pdf --midpoint`
- **Input**: 
	- Iqtree treefile
	- Two column table (tab separated) with columns label and column. The taxon labels can be pattern and don't have to be absolute matches to work.
- **Output**: PDF/Newick with tree and colored labels


## Render iqtree treefile (R )

- **Script**:  [`parse_tree.R`](../scripts/visualization/parse_tree.R)
- **Description**: Takes an iqtree treefile and a color file as input and outputs a pdf with the tree as well as a newick file for easier reading in with figtree.
- **Dependencies**: ggtree, phangorn, tidyverse, optparse
- **Tags**:  #Phylogeny , #Figtree
- **Usage**:  `Rscript parse_tree.R --tree trimmed.faa.treefile --colors colors --output tree.pdf --midpoint`
- **Input**: 
	- Iqtree treefile
	- Two column table (tab separated) with columns label and column. The taxon labels can be pattern and don't have to be absolute matches to work
- **Output**: PDF with tree and colored labels


## Visualize all NanoPlot Length and Quality graphs on one

- **Script**:  [`combine_nanoplot_html.py`](../scripts/visualization/combine_nanoplot_html.py)
- **Description**: Combine the individual nanoplot outputs for different barcodes into one. Note that this requires each sample to reside in its own folder, i.e. results/nanoplot/barcode01/file.html. For many files the script can be run by defining a start and end point to keep the output smaller.
- **Dependencies**: 
- **Tags**: #visualization, #combine_plots
- **Usage**:  `python scripts/combine_nanoplot_html.py --base_path results/nanoplot --output_html compiled_nanoplot.html --start_barcode 62 --end_barcode 96` 
- **Input**: `barcode[0-9]` folder with length versus quality html files
- **Output**
	- Combined HTML

