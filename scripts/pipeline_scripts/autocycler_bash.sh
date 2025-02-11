#!/bin/bash

# Define the usage function
usage() {
    echo "Usage: $0 -d <data_folder> -t <threads> -m <min_cpus_per_assembly>"
    echo "  -d  Path to the folder containing .fastq.gz files (e.g., 'data')"
    echo "  -t  Number of threads to use for each assembly"
    echo "  -m  Minimum number of CPUs per assembly"
    echo "  -h  Show this help message"
}

# Parse command-line arguments
while getopts "d:t:m:h" opt; do
    case $opt in
        d)
            data_folder="$OPTARG"
            ;;
        t)
            THREADS="$OPTARG"
            ;;
        m)
            MIN_CPUS_PER_ASSEMBLY="$OPTARG"
            ;;
        h)
            usage
            exit 0
            ;;
        *)
            usage
            exit 1
            ;;
    esac
done

# Check if required parameters are provided
if [ -z "$data_folder" ] || [ -z "$THREADS" ] || [ -z "$MIN_CPUS_PER_ASSEMBLY" ]; then
    echo "Error: Missing required parameters." | tee -a logs/error.log
    usage | tee -a logs/error.log
    exit 1
fi

# Check if autocycler and GNU parallel are available
if ! command -v autocycler &> /dev/null; then
    echo "Error: autocycler is not installed or not in your PATH. Please install autocycler or add it to your PATH." | tee -a logs/error.log
    exit 1
fi

if ! command -v parallel &> /dev/null; then
    echo "Error: GNU parallel is not installed or not in your PATH. Please install GNU parallel or add it to your PATH." | tee -a logs/error.log
    exit 1
fi

# Calculate the maximum number of possible parallel jobs
MAX_JOBS=$((THREADS / MIN_CPUS_PER_ASSEMBLY))

# Ensure at least one parallel job can be run
if [ "$MAX_JOBS" -lt 1 ]; then
    echo "Error: Not enough CPUs for at least one assembly. Exiting ..." | tee -a logs/error.log
    exit 1
fi

# Generate log folder
mkdir -p logs

# Dynamically generate a list of fastq.gz files in the specified data folder
READS_FILES=($(ls "$data_folder"/*.fastq.gz))

# Check if any files were found; if not, exit with an error message
if [ ${#READS_FILES[@]} -eq 0 ]; then
    echo "Error: No .fastq.gz files found in the folder '$data_folder'. Exiting..." | tee -a logs/error.log
    exit 1
fi

# Process each genome
for READS in "${READS_FILES[@]}"; do
    # Extract genome name from the input file for unique output directories
    GENOME_NAME=$(basename "$READS" .fastq.gz)
    
    # Create a log file specific to the genome
    LOG_FILE="logs/${GENOME_NAME}.log"

    # Redirect all output (including echo and errors) to the specific log file
    exec &> >(tee -a "$LOG_FILE")

    echo "Processing genome: $GENOME_NAME" | tee -a "$LOG_FILE"

    # Step 1: Estimate genome size
    GENOME_SIZE=$(genome_size_raven.sh "$READS" "$THREADS")
    echo "Genome size for $GENOME_NAME: $GENOME_SIZE" | tee -a "$LOG_FILE"

    # Step 2: Subsample the reads
    SUBSAMPLED_DIR="results/${GENOME_NAME}/subsampled_reads"
    mkdir -p "$SUBSAMPLED_DIR"
    autocycler subsample --reads "$READS" --out_dir "$SUBSAMPLED_DIR" --genome_size "$GENOME_SIZE" | tee -a "$LOG_FILE"

    # Step 3: Prepare assemblies directory and jobs file
    ASSEMBLIES_DIR="results/${GENOME_NAME}/assemblies"
    JOBS_FILE="${ASSEMBLIES_DIR}/jobs.txt"
    ASSEMBLIES_LOG_DIR="${ASSEMBLIES_DIR}/logs"

    mkdir -p "$ASSEMBLIES_DIR"
    mkdir -p "$ASSEMBLIES_LOG_DIR"
    rm -f "$JOBS_FILE"

    for ASSEMBLER in canu flye miniasm necat nextdenovo raven; do
        for i in 01 02 03 04; do
            echo "$ASSEMBLER.sh $SUBSAMPLED_DIR/sample_$i.fastq $ASSEMBLIES_DIR/${ASSEMBLER}_$i $MIN_CPUS_PER_ASSEMBLY $GENOME_SIZE" >> "$JOBS_FILE"
        done
    done

    parallel --jobs "$MAX_JOBS" --joblog "$ASSEMBLIES_LOG_DIR/parallel_exec.log" \
        --results "$ASSEMBLIES_LOG_DIR/{%}_{1}_{2}_output.log" < "$JOBS_FILE"

    # Check the exit code from parallel to ensure all jobs completed successfully
    if [ $? -ne 0 ]; then
        echo "Error: One or more jobs failed. Check the logs for more information." | tee -a "$LOG_FILE"
        exit 1
    fi

    # Step 5: Compress assemblies into a unitig graph
    AUTOCYCLER_OUT="results/${GENOME_NAME}/autocycler_out"
    autocycler compress -i "$ASSEMBLIES_DIR" -a "$AUTOCYCLER_OUT" | tee -a "$LOG_FILE"

    # Step 6: Cluster contigs
    autocycler cluster -a "$AUTOCYCLER_OUT" | tee -a "$LOG_FILE"

    # Step 7: Trim and resolve QC-pass clusters
    for CLUSTER in ${AUTOCYCLER_OUT}/clustering/qc_pass/cluster_*; do
        echo "$CLUSTER" | tee -a "$LOG_FILE"
        autocycler trim -c "$CLUSTER" | tee -a "$LOG_FILE"
        autocycler resolve -c "$CLUSTER" | tee -a "$LOG_FILE"
    done

    # Step 8: Combine resolved clusters into a final assembly
    autocycler combine -a "$AUTOCYCLER_OUT" -i ${AUTOCYCLER_OUT}/clustering/qc_pass/cluster_*/5_final.gfa | tee -a "$LOG_FILE"

    # Write completion message
    echo "Genome assembly for $GENOME_NAME completed successfully." | tee -a "$LOG_FILE"
done
