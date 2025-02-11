# AWK snippets

## Filter using awk

### Filter using search term

```bash
# Only keep alteromonas related information
awk -F'\t' '$17 ~ /s__[Aa]lteromonas/' metadata/bac120_metadata.tsv

# We can also filter using OR statements
awk -F'\t' '$17 ~ /[Tt]hioalkalivibrio/ || $58 ~ /[Tt]hioalkalivibrio/ || $63 ~ /[Tt]hioalkalivibrio/' bac120_metadata.tsv 
```

### Filter using math

```bash
awk -F'\t' -v OFS="\t" '$3 >=95' metadata/alteromonas_gtdb.tsv
```



## Print columns of interest

```bash
awk -F'\t' -v OFS='\t' '{print $1, $2}' file.txt
```


## Check what is in a awk header and what the column number is

```bash
awk -F'\t' ' { for (i = 1; i <= NF; ++i) print i, $i; exit } ' assembly_summary_2.txt
```

**Explanation**

- `(i = 1; i <= NF; ++i)`: Awk for-loop structure in which NF= number of fields in the input
- `$i` expands to the field in the input data


## Add the filename into the fasta header

```bash
mkdir renamed

for i in *fna; do awk '/>/{sub(">","&"FILENAME"-");sub(/\.fna/,x)}1' $i | cut -f1 -d " " > renamed/$i; done
```


## Split a column based on a delimiter

```bash
awk -F'\t' -v OFS='\t' '{split($1,a,"-")}{print a[1]}' All_NCBI_COGs_hmm.txt
```


## Check for empty fields in csv file and replace with NA

```bash
awk -F',' -v OFS='\t' '{ for(i=1; i<=NF; i++) if($i ~ /^ *$/) $i="NA"}; 1' ncbi_lineages_2023-10-03.csv
```

**Explanation for `{ for(i=1; i<=NF; i++) if($i ~ /^ *$/) $i="NA"}; 1`:**

- Loops through each field (`$i`) in the row (`NF` == number of fields).
- Checks if the field is empty or contains only spaces (`$i ~ /^ *$/`).
- If empty, replaces it with `"NA"`.
- The `1` at the end is an implicit shorthand for `{ print $0 }`, meaning it prints the modified line.

## Calculate average of a column

```bash
# Do math for column with and without header
average_contig_nr=$(awk -F'\t' 'NR>1{sum+=$2} END { print sum/(NR-1)}' test)
average_contig_nr=$(awk -F'\t' '{sum+=$4} END { print sum/NR}' temp3)

echo $average_contig_nr
```

**Explanation**

- `{sum+=$4`: Iterate through each line and add the value of the 4th column to the sum variable
- `END { print sum/NR}`: After reading all lines, print the average of the 4th column by dividing the sum by the total number of lines (NR)


## Add a new column by doing some math

```bash
# Add new column without a new header
awk -F'\t' -v OFS='\t' 'NR>1{norm_value = ($2/100); } {print $0, norm_value }' file > new_file

# Add a header for the new column
awk -F'\t' -v OFS='\t' 'NR==1 {print $0, "Normalized_Value"; next} {print $0, $2/100 }' file > new_file
```

**Explanation**:

- `NR>1{norm_value = ($2/100); }`: For all lines except the first line (NR>1) calculate a new value
- `NR==1 {print $0, "Normalized_Value"; next}`: If it's the first row (`NR==1`), print the original line plus a new column header (`"Normalized_Value"`). By using `next`, we ensure that the first line does not go through further processing.
- For all other values print the new row plus the newly calculated value


## Use a variable in awk (to do math for example)

```bash
# Calculate an average (for data with a header)
average_contig_nr=$(awk -F'\t' 'NR>1{sum+=$2} END { print sum/(NR-1)}' test)

# Subtract the column from the average to get the difference for example
awk -F'\t' -v OFS='\t' -v v1=$average_contig_nr 'NR==1 {print $0, "diff"; next} {print $0, $2-v1 }' test
```


## Extract protein IDs for non-empty annotations

```bash
awk -F'\t' 'NR == 1 { for (i=1; i<=NF; i++) if ($i == "FAMA_ID") col = i } NR > 1 && $col != "-" {print $1}' Annotations/Annotations.txt 
```

**Explanation**:

- `NR == 1`: Check if the current line is the first liine and for this
	- Iterates over all columns (`i=1` to `NF`).
	- Finds the column index where the header is `"FAMA_ID"`
	- Stores this column number in the variable `col`.
- Then we process all lines after the first (`NR>1`)
	- Checks if the value in the `"FAMA_ID"` column is NOT `"-"` (`$col != "-"`).
	- If that is the case, it prints the first column