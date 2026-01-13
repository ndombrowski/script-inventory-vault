# Utility scripts

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

## Search index

- **Script**:  [`search_scripts.py`](../scripts/utilities/search_scripts.py)
- **Description**:  Search index for script of interest
- **Dependencies**: fuzzywuzzy, python-Levenshtein
- **Tags**: #searching
- **Usage**: `python ../scripts/utilities/search_scripts.py`


## Scrape KEGG to COG

- **Script**:  [`scrape_kegg_to_cog.py`](../scripts/utilization/scrape_kegg_to_cog.py)
- **Description**:  For each KEGG ID finds associated COG IDs. If a list of KEGG IDs is available then also can be used in a loop
- **Dependencies**: BeautifulSoup, requests, pandas
- **Tags**: #KEGG
- **Usage**: `python scrape_kegg_to_cog.py KEGG-ID outputDir`
- **Input**: KEGG ID
- **Output**: CSV linking KEGG to COG

## Scrape KEGG module

- **Script**:  [`scrape_module_and_kegg.py`](../scripts/utilization/scrape_module_and_kegg.py)
- **Description**: For each KEGG module finds associated KEGG IDs in order how the appear in the pathway
- **Dependencies**: BeautifulSoup, requests, pandas, numpy
- **Tags**: #KEGG
- **Usage**: `python scrape_module_and_kegg.py ModuleID outputDir`
- **Input**: Module ID
- **Output**: Table with all KEGG ID found in a module


## Scrape KEGG pathway hierarchies

- **Script**:  [`scrape_pathway_hierarchy.py`](../scripts/utilization/scrape_pathway_hierarchy.py)
- **Description**: For each KEGG pathway lists the higher categories that can be used for, i.e., pathway enrichment analyses
- **Dependencies**: BeautifulSoup, requests, pandas, re
- **Tags**: #KEGG
- **Usage**: `python scrape_pathway_hierarchy.py`
- **Input**:  NA
- **Output**: Table with all all KEGG pathways and higher hierarchies
