#!/bin/bash
#SBATCH --job-name=genome_assembly  # Job name
#SBATCH --cpus-per-task=32          # CPUs per task, adjust as needed
#SBATCH --array=1-2                 # Job array size (set second number to the number of genomes to be analysed)
#SBATCH --mem=60G                   # Memory per node
#SBATCH --output=logs/%x_%A_%a.out  # Log output directory
#SBATCH --error=logs/%x_%A_%a.err   # Log error directory

# ! User input required: !
# Define general parameters
# 1data_folder should provide the path in which the fastq.gz files are stored
data_folder="data" 
MIN_CPUS_PER_ASSEMBLY=8
THREADS=$SLURM_CPUS_PER_TASK

# ! User input required: !
# Activate conda environment (edit name as needed)
source ~/.bashrc
conda activate autocycler_0.1.2

# Generate log folder
mkdir logs

# Write usage function
usage() {
    echo "Usage: sbatch autocycler_array.sh"
    echo "This script is used to run the autocycler pipeline on multiple genomes in parallel."
    echo "The script is designed to be run as a job array, with each array task corresponding to a different genome."
    echo "The script will automatically detect the .fastq.gz files in the specified data folder and run the autocycler pipeline on each file."
    echo "The script will output the results in the results folder, with each genome having its own subfolder."
    echo "The script will also generate a log file for each genome in the logs folder."
    echo -e "\nThe script requires the following parameters to be set manually:"
    echo "  - data_folder: the path to the folder containing the .fastq.gz files"
    echo "  - THREADS: the number of threads to use for each assembly. Adjust this according to your system's capabilities."
    echo "  - MIN_CPUS_PER_ASSEMBLY: the minimum number of CPUs required for each assembly. Adjust this according to the number of genomes to be analysed and max threads you are using"
}

# Print usage information if prompted
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    usage
    exit 0
fi

# Check if autocycler and GNU parallel are available
if ! command -v autocycler &> /dev/null; then
    echo "Error: autocycler is not installed or not in your PATH. Please install autocycler or add it to your PATH."
    exit 1
fi

if ! command -v parallel &> /dev/null; then
    echo "Error: GNU parallel is not installed or not in your PATH. Please install GNU parallel or add it to your PATH."
    exit 1
fi

# Calculate the maximum number of possible parallel jobs
MAX_JOBS=$((SLURM_CPUS_PER_TASK / MIN_CPUS_PER_ASSEMBLY))

# Ensure at least on parallel job can be run
if [ "$MAX_JOBS" -lt 1 ]; then
    echo "Error: Not enough CPUs for at least one assembly. Exiting ..."
    exit 1
fi

# Dynamically generate a list of fastq.gz files in the specified data folder
READS_FILES=($(ls "$data_folder"/*.fastq.gz))

# Check if any files were found; if not, exit with an error message
if [ ${#READS_FILES[@]} -eq 0 ]; then
    echo "Error: No .fastq.gz files found in the folder '$data_folder'. Exiting..."
    exit 1
fi

# Print the list of detected files
echo "Detected input files:"
for file in "${READS_FILES[@]}"; do
    echo "$file"
done

# Extract the current file to be analysed
READS="${READS_FILES[$SLURM_ARRAY_TASK_ID-1]}"

# Extract genome name from the input file for unique output directories
GENOME_NAME=$(basename "$READS" .fastq.gz)

# Create a log file specific to the genome
LOG_FILE="logs/${GENOME_NAME}.log"
exec &> >(tee -a "$LOG_FILE")

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

# Step 5: Compress assemblies into a unitig graph
AUTOCYCLER_OUT="results/${GENOME_NAME}/autocycler_out"
autocycler compress -i "$ASSEMBLIES_DIR" -a "$AUTOCYCLER_OUT" | tee -a "$LOG_FILE"

# Step 6: Cluster contigs
autocycler cluster -a "$AUTOCYCLER_OUT" | tee -a "$LOG_FILE"

# Step 7: Trim and resolve QC-pass clusters
for CLUSTER in ${AUTOCYCLER_OUT}/clustering/qc_pass/cluster_*; do
    echo "$CLUSTER"
    autocycler trim -c "$CLUSTER" | tee -a "$LOG_FILE"
    autocycler resolve -c "$CLUSTER" | tee -a "$LOG_FILE"
done

# Step 8: Combine resolved clusters into a final assembly
autocycler combine -a "$AUTOCYCLER_OUT" -i ${AUTOCYCLER_OUT}/clustering/qc_pass/cluster_*/5_final.gfa | tee -a "$LOG_FILE"

# Write completion message
echo "Genome assembly for $GENOME_NAME completed successfully." | tee -a "$LOG_FILE"