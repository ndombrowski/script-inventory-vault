# Data visualization scripts

## Genome visualization

- **Script**:  [`generate_circos_plot.py`](scripts/visualization/generate_circos_plot.py)
- **Description**: Generate circos plots as png from Genbank files. If desired also marks genes of interest in the plot.
- **Dependencies**: pycirclize, numpy, matplotlib
- **Tags**: #visualization, #genome
- **Usage**:  `python python generate_circos_plot.py -i genome.gbk  -o circos_plot.pdf  -g genes_of_interest.txt` 
- **Output**
	- Png for genome of interest
	- ![[Pasted image 20250210110128.png|200]]


