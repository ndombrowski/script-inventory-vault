#!/bin/bash

# Usage message
usage() {
    echo "Usage: $0 -r <desired_read_nr> -a <aln_thres> -m <mapped_thres> -d <run_dir> -i <input_dir> -o <output_dir> -l <log_dir> -p <polishing_method>"
    echo ""
    echo "Arguments:"
    echo "  -r <desired_read_nr>    Total reads threshold (default: 100). Consider only clusters larger than a fraction of number of total reads"
    echo "  -a <aln_thres>          Alignment threshold (default: 0.4). Minimum aligned fraction of read to be included in the cluster"
    echo "  -m <mapped_thres>       Mapped threshold (default: 0.7). Minimum mapped fraction of read to be included in the cluster"
    echo "  -d <run_dir>            A unique name for this run, used to organize output files. Useful when testing different input parameters."
    echo "  -i <input_dir>          The directory containing input FASTQ files. Workflow does not work on compressed files or files with an extension other than fastq."
    echo "  -o <output_dir>         The base directory where output files will be saved."
    echo "  -l <log_dir>            The directory where log files will be saved."
    echo "  -p <polishing_method>   The polishing method to use: 'medaka' or 'racon'."
    echo "  -t <threads>           Number of threads to use (default: 20)."
    echo ""
    echo "Description:"
    echo "  This script processes all FASTQ files in the specified input directory. For each FASTQ file:"
    echo "  1. It calculates the total number of reads and an abundance ratio."
    echo "  2. Runs NGSpeciesID on the file using the calculated ratio. Consensus sequences supported by fewer reads will not be taken into account."
    echo "  3. Names the output directories and files based on the FASTQ input filename."
    echo "  4. Extracts information from the NGSpeciesID logs."
    echo "  5. Processes and combines output FASTA files into a single combined FASTA file per sample."
    echo ""
    echo "Example:"
    echo " $0 -r 100 -a 0.8 -m 0.5 -t 20 -d run1 -i /path/to/input_dir -o /path/to/output_dir -l /path/to/log_dir -p medaka"
    echo ""
    echo "In this example, all FASTQ files in '/path/to/input_dir' will be processed individually. Outputs and logs"
    echo "will be saved in '/path/to/output_dir/run1' and '/path/to/log_dir' respectively. Each output file will"
    echo "be named based on the corresponding input filename."
    exit 1
}

# Default values
default_desired_read_nr=100
default_aln_thres=0.4
default_mapped_thres=0.7
default_threads=20 
default_output_dir="./output" 
default_log_dir="./logs" 

# Parse arguments
while getopts "r:a:m:t:d:i:o:l:p:" opt; do
    case "$opt" in
        r) desired_read_nr=$OPTARG ;;
        a) aln_thres=$OPTARG ;;
        m) mapped_thres=$OPTARG ;;
        t) threads=$OPTARG ;;
        d) run_dir=$OPTARG ;;
        i) input_dir=$OPTARG ;;
        o) output_dir=$OPTARG ;;
        l) log_dir=$OPTARG ;;
        p) polishing_method=$OPTARG ;;  
        *) usage ;;
    esac
done

# Set defaults if arguments are not provided
desired_read_nr=${desired_read_nr:-$default_desired_read_nr}
aln_thres=${aln_thres:-$default_aln_thres}
mapped_thres=${mapped_thres:-$default_mapped_thres}
threads=${threads:-$default_threads}
output_dir=${output_dir:-$default_output_dir}
log_dir=${log_dir:-$default_log_dir}

# Fixed variable
fastq_extension=".fastq"

# Ensure required arguments are provided
if [[ -z "$run_dir" || -z "$input_dir" || -z "$output_dir" || -z "$log_dir" ]]; then
    echo "Error: Missing required arguments."
    usage
fi

# Check if NGSpeciesID is available
if ! command -v NGSpeciesID &> /dev/null; then
    echo "Error: NGSpeciesID is not installed or not in your PATH. Please install NGSpeciesID or add it to your PATH."
    exit 1
fi

# Ensure output and log directories exist
mkdir -p "${output_dir}/${run_dir}" "$log_dir"

# Check if input directory contains FASTQ files (compressed files are ignored)
if [[ -z "$(find "$input_dir" -maxdepth 1 -type f -name *"$fastq_extension")" ]]; then
    echo "Error: No FASTQ files found in input directory '$input_dir'."
    exit 1
fi

# Check for compressed files in the input directory (ignored files but issue warning)
compressed_files=$(find "$input_dir" -maxdepth 1 -type f \( -name "*.gz" -o -name "*.bz2" -o -name "*.zip" \))
if [[ -n "$compressed_files" ]]; then
    echo -e "\nWarning: Compressed files detected in the input directory. These will not be processed:"
    echo -e "$compressed_files\n"
fi

# Polishing method logic
if [[ "$polishing_method" == "medaka" ]]; then
    polishing_flag="--medaka"
elif [[ "$polishing_method" == "racon" ]]; then
    polishing_flag="--racon"
else
    echo "Error: Missing polishing method. Please use '-p medaka' or '-p racon'."
    exit 1
fi

# Loop through all relevant files in the input directory to run NGSpeciesID
for input_file in "$input_dir"/*$fastq_extension; do
    # Check if the input file exists
    if [[ ! -f "$input_file" ]]; then
        echo "Error: Input file '$input_file' does not exist or is not accessible."
        continue
    fi

    # Extract the sample name from the filename
    current_sample=$(basename "$input_file" "$fastq_extension")

    echo -e "\nProcessing sample: $current_sample"

    # Count reads (dividing line count by 4 for FASTQ format)
    total_reads=$(( $(cat "$input_file" | wc -l) / 4 ))

    # Sanity check for total_reads
    if [[ "$total_reads" -le 0 ]]; then
        echo "Error: Total reads for '$current_sample' is zero or invalid."
        continue
    fi

    echo "Total reads for $current_sample: $total_reads"

    # Estimate abundance ratio to work with at least $desired_read_nr reads
    estimated_ratio=$(awk "BEGIN {print $desired_read_nr / $total_reads}")
    echo "Abundance ratio for $current_sample: $estimated_ratio"

    # Run NGSpeciesID
    cmd="NGSpeciesID --ont --fastq $input_file --outfolder ${output_dir}/${run_dir}/${current_sample}/ --t $threads --consensus --abundance_ratio $estimated_ratio --aligned_threshold $aln_thres --mapped_threshold $mapped_thres"

    # Add polishing flag only if it's not empty
    if [[ -n "$polishing_flag" ]]; then
        cmd="$cmd $polishing_flag"
    fi

    # Executing the command
    echo "Executing: $cmd"
    $cmd > "$log_dir/ngspeciesID_${run_dir}_${current_sample}.log" 2>&1

    # Check if log file exists
    log_file="$log_dir/ngspeciesID_${run_dir}_${current_sample}.log"
    if [[ ! -f "$log_file" ]]; then
        echo "Error: Log file '$log_file' was not created. Skipping further processing for $current_sample."
        continue
    fi

    # Grep some info from the log file to ensure all went well
    echo "Log summary for $current_sample:"
    grep "singletons were discarded" "$log_file"
    grep "clusters were discarded" "$log_file"
    grep "centers formed" "$log_file"
    grep "consensus formed" "$log_file"

    # Second loop: Process each output fasta file, modify headers, and concatenate
    combined_fasta="${output_dir}/${run_dir}/${current_sample}.fasta"

    echo "Processing FASTA files for sample: $current_sample"
    
    if [[ "$polishing_method" == "medaka" || "$polishing_method" == "racon" ]]; then
        echo -e "Working on files:\n $(find "${output_dir}/${run_dir}/${current_sample}" -type f -path "*/${polishing_method}_cl_id_*/consensus.fasta")"
        find "${output_dir}/${run_dir}/${current_sample}" -type f -path "*/${polishing_method}_cl_id_*/consensus.fasta" | while read fasta_file; do
            if [[ -f "$fasta_file" ]]; then
                sed -E "s/^>consensus_cl_id_([0-9]+)_total_supporting_reads_([0-9]+).*/>${current_sample}_id\1_sr\2/" "$fasta_file"
            else
                echo "Warning: Fasta file '$fasta_file' not found or inaccessible."
            fi
        done > "$combined_fasta"
    else
        # For when polishing_flag is empty (no polishing method specified)
        find "$output_dir/${run_dir}/$current_sample" -maxdepth 1 -name "*.fasta" | while read fasta_file; do
            if [[ -f "$fasta_file" ]]; then
                sed -E "/^>/s/^>consensus_cl_id_([0-9]+)_total_supporting_reads_([0-9]+)/>${current_sample}_id\1_sr\2/" "$fasta_file"
            else
                echo "Warning: Fasta file '$fasta_file' not found or inaccessible."
            fi
        done > "$combined_fasta"
    fi

    # Sanity check for the combined fasta file
    if [[ -f "$combined_fasta" ]]; then
        echo -e "Sanity check for ${current_sample}: \nWe work with so many consensus sequences:"
        grep -c ">" "$combined_fasta"
        echo -e "\nThe sequences have the following file headers:"
        grep ">" "$combined_fasta"
    else
        echo "Error: Combined fasta file for $current_sample was not created."
    fi
done
