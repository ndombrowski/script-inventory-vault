# Sed snippets

## Remove header line

```bash
sed 1d nbci_data/assembly_summary.txt
```


## Replace tab with comma

```bash
sed -i 's/\t/,/g' input/mapping.csv
```


## Edit NCBI ftp link to download specific file

```bash
# Get link for fna files and download them
sed -r 's|(https://ftp.ncbi.nlm.nih.gov/genomes/all/)(GCA/)([0-9]{3}/)([0-9]{3}/)([0-9]{3}/)(GCA_.+)|\1\2\3\4\5\6/\6_genomic.fna.gz|' ../nbci_data/ftp_gtp_reps > ftp_gtp_reps_fna 

for i in $(cat ftp_gtp_reps_fna); do 
    wget $i 
done

# Get link for faa files
sed -r 's|(https://ftp.ncbi.nlm.nih.gov/genomes/all/)(GCA/)([0-9]{3}/)([0-9]{3}/)([0-9]{3}/)(GCA_.+)|\1\2\3\4\5\6/\6_protein.faa.gz|' ../../nbci_data/ftp_gtp_reps  > ftp_gtp_reps_faa
```


### Format a silva fasta file

```bash
sed 's/;;/;NA/g' db/silva/general/silva-ref-modified.fasta | \
  sed '/^>/!s/U/T/g'| \
  awk '/^>/ {if(NR!=1) printf("\n%s\n",$0); else printf("%s\n",$0); next; } { printf("%s",$0);} END {printf("\n");}' > db/silva/kraken/library/silva-ref-modified.fna
```

**Explanation**

- `sed 's/;;/;NA/g'`: Replace missing values with NA
- `sed '/^>/!s/U/T/g'`: Replace U with T in non-header lines
- Reformat sequences so that
	- Header lines always start on a new line
	- Sequence lines are concatenated without line breaks
	- Ensures that the final sequence ends with a new line
