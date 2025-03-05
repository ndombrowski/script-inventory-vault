
# General bash snippets

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

## Filter hmmsearch output

```bash
#format the full table and only select sequences above a certain evalue
sed 's/ \+ /\t/g' annotations/NCBI_COGs/sequence_results.txt | sed '/^#/d'| sed 's/ /\t/g'| awk -F'\t' -v OFS='\t' '{print $1, $3, $6, $5}' | awk -F'\t' -v OFS='\t' '($4 + 0) <= 1E-3'  > annotations/NCBI_COGs/sequence_results_red_e_cutoff.txt

#get best hit based on bit score, and then evalue (in case two sequences have the same bitscore)
sort -t$'\t' -k3,3gr -k4,4g annotations/NCBI_COGs/sequence_results_red_e_cutoff.txt | sort -t$'\t' --stable -u -k1,1  | sort -t$'\t' -k3,3gr -k4,4g >  annotations/NCBI_COGs/All_NCBI_COGs_hmm.txt
```


## Remove lines with pattern from a file

```bash
# -f takes pattern from a file
# -v inverts match (allowing us to remove things)
# -w match whole word (in case we do not want to work with patterns)
# -i in case we want to ignore the case
fgrep -v -f $seq_to_remove annotations/NCBI_COGs/All_NCBI_COGs_hmm.txt
```


## Use wget with target directory

```bash
wget https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/016/756/315/GCF_016756315.1_ASM1675631v1/GCF_016756315.1_ASM1675631v1_genomic.fna.gz -P db/references
```


## Get nanopore basemodel

```bash
zcat data/Nanopore_J4_SuperBasecalling.fastq.gz |  grep -oP 'model_version_id=\K[^ ]+' | sort | uniq
```

Note: Tested on the sequencing output from the Uva molecular lab


## Calculate average protein length for a number of files

```bash
for i in {1..10}; do
  filename=$(basename results/v1_chopper_flye/polishing/medaka/prokka/medaka_r${i}.faa)
  avg_length=$(seqtk seq results/v1_chopper_flye/polishing/medaka/prokka/medaka_r${i}.faa | awk 'NR % 2 == 0' | awk '{sum += length($0); n++} END {print sum/n;}')
  echo "File: ${filename}, Average Length: ${avg_length}"
done
```

**Explanation**

- `seqtk seq` converts a fasta file to a readable sequence format and puts each sequence into a unique line so that first comes the header then the sequence until the full file is processed
- **`awk 'NR % 2 == 0'`**: Filters only the sequence lines from the FASTA file (i.e., it skips the header lines). Here this divides the the current row by two and returns the remainder
	- odd numbers give 1
	- even numbers give 0
- `length($0)` calculates the length of each sequence
- `sum += length($0)`: Accumulates the length of each sequence
- `n++`: Counts the number of sequences


## Calculate the number of sequences in a file

```bash
zcat file.fastq.gz | $(( $(wc -l) /4 ))
```


## Shorten NCBI fasta file names

```bash
for file in *.fna.gz; do
    new_name=$(echo "$file" | sed -E 's/(GCF_[0-9]+\.[0-9]+).*\.fna\.gz/\1.fna.gz/')
    mv -v "$file" "$new_name"
done
```

**Explanation**

- `(GCF_[0-9]+\.[0-9]+)`: This matches a string starting with GCF_ followed by a series of digits (`[0-9]+`), a period (`\.`), and more digits (`[0-9]+`). Since we use brackets around the term, this allows us to capture the first part of the filename (like GCF_000123456.1).
- - **`.*`**: Matches any characters after the captured `GCF_` part (including the version number, etc.).
- `\.fna\.gz`: Matches the `.fna.gz` extension.
- `\1.fna.gz`: Replaces the entire filename with just the captured part (the `GCF_*` part) and appends `.fna.gz` to it, effectively removing anything after the first `GCF_*` part and preserving the extension.
- Use mv with verbose (`-v`) to display what is being renamed to what


## For prokka file headers remove everything after a space

```bash
for i in results/faa/*faa; do
    cut -f1 -d " " "$i" > "$i.tmp" && mv "$i.tmp" "$i"
done
```


## Make list of genome IDs

```bash
ls data/genomes/fna/*fna | xargs -n1 basename | sed 's/\.[^.]*$//' > file_lists/genomes_fna
```

**Explanation**:

- Get a list of all genomes of interest
- get the basename from the full path
- `sed 's/\.[^.]*$//'` remove the file extension (i.e. everything after the last dot)


## Add a header to file

```bash
echo -e "accession\tIPR\tIPRdescription\tIPR_PFAM\tIPR_PFAMdescription" | cat - Annotations/Sulfur_genes/IPRscan/temp2 > Annotations/Sulfur_genes/IPRscan/IPR_results.tsv
```


## Generate mapping files

### SampleID, file path, read direction

```bash
#generate manifest file
for file in data/*.gz; do
    path=$(echo $file | sed 's/^/$PWD\//g')
    sample_lane=$(echo $file | cut -f2 -d "/" | cut -f3 -d "_")
    sample=$(echo $file | cut -f2 -d "/" | cut -f1 -d "-")
    
    if [[ $file =~ "_R1_" ]]; then
        direction="forward"
    elif [[ $file =~ "_R2_" ]]; then
        direction="reverse"
    else
        direction="unknown"
    fi

echo "${sample}-${sample_lane},$path,$direction"
done > temp

echo "sample-id,absolute-filepath,direction" | cat - temp > manifest.csv
```


## Separate info for R1 and R2

```bash
#generate manifest file
for file in data/*.gz; do
 if [[ $file == *_R1_*gz ]]; then
    sample_lane=$(echo $file | cut -f2 -d "/" | cut -f3 -d "_")
    name=$(echo $file | cut -f2 -d "/" | cut -f1 -d "-")
    sample=$(echo "${name}-${sample_lane}")

    r1_file=$(echo $file | cut -f2 -d "/")
    r2_file=$(echo $r1_file | sed 's/_R1/_R2/')

    echo -e "$sample\t$r1_file\t$r2_file\t$name\t$name"
  fi
done > temp

echo -e "library\tr1_file\tr2_file\tsample\trun" | cat - temp > sample_dadasnake.tsv
```


## Check file for unicode errors

```bash
# View problematic lines
LC_ALL=C grep -n '[^[:print:][:space:]]' cog_mapping.txt

# Clean issues
iconv -f utf-8 -t utf-8//IGNORE cog_mapping.txt > cog_mapping_cleaned.txt

# Sanith Check
LC_ALL=C grep -n '[^[:print:][:space:]]' cog_mapping_cleaned.txt
grep COG0507 cog_mapping.txt
```

Problems can, for example, look something like this: " ATPase/5�-3�_helicase_helicase_"


## Make a comma separated list for certain files

```bash
# Find all R1 and R2 files and replace line break with comma
R1_files=$(ls ${input_dir}/*_R1_trim.fastq.gz | tr '\n' ',')
R2_files=$(ls ${input_dir}/*_R2_trim.fastq.gz | tr '\n' ',')

# Remove the trailing comma from the lists
R1_files=${R1_files%,}
R2_files=${R2_files%,} 
```


## Do a uniprot request

```bash
# Make list with IDs of interest
uniprot_list=$(awk '{print $4}' <(sed 1d 03_data/annotations/manual/TrophicModePrediction/hmm_to_trophic_mode_uniq.tsv) | sort | uniq | paste -sd ',' -)

#{"jobId":"a79963e8f9e4e1f7feee0349885ca3ba27b5f70d"}
curl --request POST 'https://rest.uniprot.org/idmapping/run' \
  --form "ids=${uniprot_list}" \
  --form 'from="UniProtKB_AC-ID"' \
  --form 'to="UniRef90"'

# Check if the results are ready
curl -i 'https://rest.uniprot.org/idmapping/status/a79963e8f9e4e1f7feee0349885ca3ba27b5f70d'

# Download results
curl -s "https://rest.uniprot.org/idmapping/uniref/results/stream/a79963e8f9e4e1f7feee0349885ca3ba27b5f70d" > 03_data/annotations/manual/results.json 

# found 453 hits 
grep -oP "from" 03_data/annotations/manual/results.json | wc -l

# Parse results
python 01_workflows_and_scripts/extract_json.py -i 03_data/annotations/manual/results.json  -o 03_data/annotations/manual/uniprot_to_name.txt
```


## awk-add-filename-as-col

```bash
awk 'BEGIN{FS=OFS="\t"} NR==1 {print "NAME", $0; next} {print FILENAME, $0}' file
```

**Description**:  

- For the first row `(NR==1)` → Prints "NAME" + the first row of the file.
- For all other rows → Prints FILENAME + each row.


## Bash functions

Functions in bash have the following format: 

```bash
function name {
	commands
	return
} 
```

We might also encounter this simpler form:

```bash
name () {
	commands
	return
}
```

Minimal example:

```bash
report_disk_space() {
	df -h
	return
}

report_disk_space
```