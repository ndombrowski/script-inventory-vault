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

## Reverse complement

- **Script**:  [`reverse_complement.py`](../scripts/bioinformatics/reverse_complement.py)
- **Description**: Generates the reverse complement of a sequence. 
- **Dependencies**: Bio
- **Tags**: #DNA, #reverse_complement, #FASTA 
- **Usage**: `python reverse_complement.py`
- **Input**: A fasta file, a string or an input when prompted
- **Output**: 
	- When a fasta file is given then an output file with the reverse complement for each sequence id is given
	- Otherwise the reverse complement is printed to the screen