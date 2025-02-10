# Data visualization scripts

## Genome visualization

- **Script**:  [`generate_circos_plot.py`](scripts/visualization/generate_circos_plot.py)
- **Description**: Generate circos plots as png from Genbank files. If desired also marks genes of interest in the plot.
- **Dependencies**: pycirclize, numpy, matplotlib
- **Tags**: #visualization, #genome
- **Usage**:  `python python generate_circos_plot.py -i genome.gbk  -o circos_plot.pdf  -g genes_of_interest.txt` 
- **Input**: Genebank files
- **Output**
	- Png for genome of interest
	- ![[Pasted image 20250210110128.png|200]]


## Format Figree

- **Script**:  [`formatFigtree3.pl`](scripts/visualization/formatFigtree3.pl)
- **Description**: Format a newick tree to a figtree format, coloring the leaves depending on the taxa (or anything it's giving in the list with color)
- **Dependencies**: NA
- **Tags**:  #Phylogeny , #Figtree
- **Usage**:  Get list of treefiles with `ls -d "$PWD"/*renamed | tac - > listOfFiles2.list` followed by `perl formatFigtree3.pl listOfFiles2.list -C color_mapping2 -sl 10` to format the list of trees
- **Input**: List of figtree files
- **Output**: List of formatted figrees



