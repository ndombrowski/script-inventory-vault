import pandas as pd
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Extract intron sizes from a GTF file.")
parser.add_argument("-i", "--input", required=True, help="Path to the GTF file.")
parser.add_argument("-o", "--output", required=True, help="Path to save the output CSV file.")
args = parser.parse_args()

# Function to parse GTF attributes
def parse_attributes(attr):
    return {k: v.strip('"') for k, v in (item.split(" ") for item in attr.strip(";").split("; ") if item)}

# Load the GTF file
gtf_data = []
with open(args.input, "r") as gtf:
    for line in gtf:
        if line.startswith("#"):
            continue  # Skip header lines
        parts = line.strip().split("\t")
        if parts[2] == "exon":  # Only process exon lines
            gtf_data.append(parts)

# Convert to DataFrame
columns = ["seqname", "source", "feature", "start", "end", "score", "strand", "frame", "attributes"]
gtf_df = pd.DataFrame(gtf_data, columns=columns)
gtf_df["start"] = gtf_df["start"].astype(int)
gtf_df["end"] = gtf_df["end"].astype(int)

# Parse attributes
gtf_df["attributes"] = gtf_df["attributes"].apply(parse_attributes)
gtf_df["transcript_id"] = gtf_df["attributes"].apply(lambda x: x["transcript_id"])
gtf_df["gene_id"] = gtf_df["attributes"].apply(lambda x: x["gene_id"])

# Sort by transcript and exon start position
gtf_df = gtf_df.sort_values(by=["transcript_id", "start"])

# Calculate intron sizes
intron_sizes = []
for transcript, group in gtf_df.groupby("transcript_id"):
    exons = group.sort_values(by="start").reset_index(drop=True)
    for i in range(1, len(exons)):
        intron_start = exons.loc[i - 1, "end"] + 1
        intron_end = exons.loc[i, "start"] - 1
        intron_size = intron_end - intron_start + 1
        intron_sizes.append({
            "transcript_id": transcript,
            "gene_id": exons.loc[i, "gene_id"],
            "seqname": exons.loc[i, "seqname"],
            "strand": exons.loc[i, "strand"],
            "intron_start": intron_start,
            "intron_end": intron_end,
            "intron_size": intron_size
        })

# Convert to DataFrame
intron_df = pd.DataFrame(intron_sizes)

# Save intron sizes to a file
intron_df.to_csv(args.output, index=False)

# Calculate summary statistics
mean_size = intron_df["intron_size"].mean()
median_size = intron_df["intron_size"].median()
max_size = intron_df["intron_size"].max()
min_size = intron_df["intron_size"].min()

# Calculate percentiles
percentile_90 = intron_df["intron_size"].quantile(0.90)
percentile_99 = intron_df["intron_size"].quantile(0.99)
percentile_99_9 = intron_df["intron_size"].quantile(0.999)

# Count transcripts with at least one intron above percentiles
transcripts_above_90 = intron_df[intron_df["intron_size"] > percentile_90]["transcript_id"].nunique()
transcripts_above_99 = intron_df[intron_df["intron_size"] > percentile_99]["transcript_id"].nunique()
transcripts_above_99_9 = intron_df[intron_df["intron_size"] > percentile_99_9]["transcript_id"].nunique()

# Print summary statistics
print(f"Summary Statistics for Intron Sizes:")
print(f"Mean: {mean_size:,.0f} bp")
print(f"Median: {median_size:,.0f} bp")
print(f"Max: {max_size:,.0f} bp")
print(f"Min: {min_size:,.0f} bp")
print(f"90th Percentile: {percentile_90:,.0f} bp")
print(f"99th Percentile: {percentile_99:,.0f} bp")
print(f"99.9th Percentile: {percentile_99_9:,.0f} bp")
print(f"Number of transcripts with at least one intron above 90th percentile: {transcripts_above_90}")
print(f"Number of transcripts with at least one intron above 99th percentile: {transcripts_above_99}")
print(f"Number of transcripts with at least one intron above 99.9th percentile: {transcripts_above_99_9}")
