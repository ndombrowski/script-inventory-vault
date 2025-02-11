#!/bin/bash

# Check if argument is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <file_pattern>"
    exit 1
fi

file_pattern="$1"

# Function to extract counts for 0 and 1 from a file
get_counts() {
    local file="$1"
    local total=$(wc -l < "$file")
    local unannotated=$(awk '$6 == 0 {count++} END {print count}' "$file")
    local annotated=$(awk '$6 == 1 {count++} END {print count}' "$file")
    #local non_canonical=$(awk '$5 == 0 {count++} END {print count}' "$file")
    echo "$total $unannotated $annotated"
}

# Loop through each file matching the pattern and print the table
echo "Sample total unannotated annotated"
for file in $file_pattern; do
    if [ -f "$file" ]; then
        sample=$(basename "$file" _SJ.out.tab)
        counts=$(get_counts "$file")
        printf "%s %s\n" "$sample" "$counts"
    else
        echo "File $file not found."
    fi
done
