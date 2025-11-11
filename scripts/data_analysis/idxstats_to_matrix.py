import pandas as pd
from pathlib import Path
import re
import argparse
import sys 

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate OTU tables and summary read counts from per-sample mapping stats files."
    )
    parser.add_argument(
        "-i", "--input_folder",
        type=str,
        default="results/mapping_counts",
        help="Folder containing *_stats.tsv files (default: results/mapping_counts)"
    )
    parser.add_argument(
        "-o", "--output_folder",
        type=str,
        default="results/mapping_counts",
        help="Folder to write output files (default: results/mapping_counts)"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    input_folder = Path(args.input_folder)
    output_folder = Path(args.output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    # -------------------------------- Find files -------------------------------- #
    filenames = list(input_folder.glob("barcode*_stats.tsv"))
    
    barcode_list = [f.stem.split("_stats")[0] for f in filenames]
    print(barcode_list)

    if not barcode_list:
        print(f"No files matched the regex pattern '{args.pattern}'")
        sys.exit(1)

    # ------------------------------- Read in data ------------------------------- #
    dfs = []

    for barcode in barcode_list:
        current_file = output_folder / f"{barcode}_stats.tsv" 
        temp_df = pd.read_csv(current_file, 
                            sep = "\t", 
                            names = ["taxon", "length", "mapped", "unmapped" ])
        temp_df["sample"] = barcode
        dfs.append(temp_df)

    df = pd.concat(dfs, ignore_index=True)


    # -------------------------------- Clean up df ------------------------------- #
    df["taxon"] = df["taxon"].str.replace("*", "unassigned")


    # -------------------------- Extract summary values -------------------------- #
    # Total number of mapped reads per sample
    total_mapped = df[["sample", "mapped"]].groupby("sample").sum()


    # --------------------------- Generate count matrix -------------------------- #
    otu_table = df.pivot_table(
        index = "taxon",
        columns = "sample",
        values = "mapped", 
        fill_value = 0
    )


    # ------------------------------- Write to file ------------------------------ #
    total_mapped.to_csv(str(output_folder) + "/mapped_per_sample.tsv", sep = "\t", index = True)
    otu_table.to_csv(str(output_folder) + "/otu_table.tsv", sep = "\t", index = True)

    print(f"Finished! mapped_per_sample.tsv and otu_table.tsv written to {output_folder}")

if __name__ == "__main__":
    main()