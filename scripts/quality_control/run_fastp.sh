#!/bin/bash
#SBATCH --job-name=fastp
#SBATCH --output=logs/fastp_%A_%a.out
#SBATCH --error=logs/fastp_%A_%a.err
#SBATCH --array=1-27%3
#SBATCH --cpus-per-task=20
#SBATCH --mem=50G
#SBATCH --time=UNLIMITED 

# Activate modules
source ~/.bashrc
mamba activate fastp_0.23.4

# List all R1 fastq.gz files
files=(03_data/raw_reads/*R1.fastq.gz)

# Get the file corresponding to the current SLURM_ARRAY_TASK_ID
file=${files[$SLURM_ARRAY_TASK_ID-1]}

# Extract file_id and sample_id
file_id=$(basename "$file" _R1.fastq.gz)
sample_id=$(echo $file_id | cut -f1,3 -d "_")

# Define output file paths
out1=05_quality_filtering/fastp/v3/${sample_id}_R1_trim.fastq.gz
out2=05_quality_filtering/fastp/v3/${sample_id}_R2_trim.fastq.gz

# Print starting message
timestamp_start=$(date +%Y%m%d_%H%M%S)
echo "Starting FastP analysis $timestamp_start" 
echo "Now trimming $sample_id"

# Run fastp
if [[ -f "$out1" && -f "$out2" ]]; then
    echo "Output files $out1 and $out2 already exist. Skipping fastp for $sample_id."
else
    echo "Now trimming $sample_id"

    # Run fastp
    fastp \
        --in1  03_data/raw_reads/${file_id}_R1.fastq.gz \
        --in2  03_data/raw_reads/${file_id}_R2.fastq.gz \
        --trim_poly_g \
        --qualified_quality_phred 15 \
        --length_required 100 \
        --thread 20 \
        --html 05_quality_filtering/v3/${sample_id}.fastp-trim.report.html \
        --out1 $out1 \
        --out2 $out2

    echo "fastp trimming complete for $sample_id."
fi

# Capture end timestamp
timestamp_end=$(date +%Y%m%d_%H%M%S)
echo "FastP analysis completed at $timestamp_end"
