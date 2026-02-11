#!/usr/bin/env python3
###########################################################
# parse_dbCAN.py
#
# Parse hmmsearch domtblout output for dbCAN annotation
#
# Author: Nina Dombrowski
# Date: 2025-02-11
# Version: 1.0.0
#
# Based on the original hmmscan-parser from http://dbcan-hcc.unl.edu/download/Tools/
# Modified to work with hmmsearch, use pandas and add metadata information
#
# Last updated: 2025-02-11
###########################################################
import pandas as pd
import argparse
import os


def parse_arguments():
    """Parse command line arguments"""
    
    parser = argparse.ArgumentParser(description="""Parse hmmsearch domtblout files against the dbCAN database to identify and annotate carbohydrate-active enzymes. \nFilters by E-value and coverage, removes overlapping domains, and provides both detailed and summary outputs. \nExample: python .\parse_dbCAN.py -i data/domain_results.txt -m data/fam-substrate-mapping-08262025.tsv -o results -e 1e-5 -c 0.30
    """,
    formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "-i", "--input", required=True, help="Input hmmsearch domtblout file"
    )

    parser.add_argument(
        "-m",
        "--metadata",
        required=True,
        help="dbCAN family-substrate mapping file (TSV)",
    )

    parser.add_argument(
        "-o", "--outdir", required=True, help="Output directory for results"
    )

    parser.add_argument(
        "-e",
        "--evalue",
        type=float,
        default=1e-15,
        help="E-value threshold for filtering hits",
    )

    parser.add_argument(
        "-c",
        "--coverage",
        type=float,
        default=0.35,
        help="Coverage threshold for filtering hits (0-1)",
    )

    parser.add_argument(
        "--overlap-threshold",
        type=float,
        default=0.5,
        help="Overlap threshold for removing redundant hits (0-1)",
    )

    return parser.parse_args()


def parse_domtblout(
    filename: str, e_value_threshold: float = 1e-15, coverage_threshold: float = 0.35
) -> pd.DataFrame:
    """
    Read in and extract relevant columns from hmmsearch domtblout.
    Pre-filters values with low E-value and coverage
    """
    df = pd.read_csv(
        filename,
        comment="#",
        header=None,
        usecols=[0, 2, 3, 5, 12, 13, 15, 16, 17, 18],
        names=[
            "seq_name",
            "seq_len",
            "hmm",
            "hmm_length",
            "i_evalue",
            "bitscore",
            "hmm_from",
            "hmm_to",
            "ali_from",
            "ali_to",
        ],
        sep=r"\s+",
    )

    # Clean hmm content
    df["hmm"] = df["hmm"].str.replace(r"\.hmm", "", regex=True)
    df["hmm_id"] = df["hmm"].str.replace(r"_.*", "", regex=True)
    df['i_evalue_formatted'] = df['i_evalue'].apply(lambda x: f"{x:.2e}")
    
    # remove 0 length alignments
    df = df[df["ali_from"] != df["ali_to"]]

    # calculate coverage
    df["coverage"] = (df["ali_to"] - df["ali_from"]) / df["seq_len"]

    # filter low confidence hits
    df = df[
        (df["i_evalue"] <= e_value_threshold) & (df["coverage"] >= coverage_threshold)
    ]

    return df


def remove_overlaps(df: pd.DataFrame, overlap_threshold: float = 0.5) -> pd.DataFrame:
    """
    Takes the domtblout to identify and remove overlapping/redundant dbCAN domain hits on the same sequence.
    """
    # Group hits by sequence
    df = df.sort_values(["seq_name", "ali_from", "ali_to"])

    # Remove if overlap exceeds the overlap_threshold, i.e. 50%, of either domain's length 
    # and keep hit with better e-value
    remove_indices = []

    # Group by seq and check groups with more than one index
    for seq_name, group in df.groupby("seq_name"):
        indices = group.index.tolist()

        # Skip sequences with only one hit - nothing to compare
        if len(indices) <= 1:
            continue
        print(seq_name, group)

        i = 0
        while i < len(indices) - 1:
            current_idx = indices[i]
            next_idx = indices[i + 1]

            current = df.loc[current_idx]
            next_hit = df.loc[next_idx]

            # Calculate overlap
            current_len = current["ali_to"] - current["ali_from"]
            next_len = next_hit["ali_to"] - next_hit["ali_from"]
            overlap = current["ali_to"] - next_hit["ali_from"]
            print(current_len, next_len, overlap, overlap / current_len)

            # Check if significant overlap exists
            if overlap > 0 and (overlap/current_len > overlap_threshold or 
                    overlap/next_len > overlap_threshold):
                # Remove the hit with worse (higher) E-value
                if current['i_evalue'] < next_hit['i_evalue']:
                    remove_indices.append(next_idx)
                    indices.pop(i + 1)
                elif current['i_evalue'] > next_hit['i_evalue']:
                    remove_indices.append(current_idx)
                    indices.pop(i)
                else:  # E-values are equal, use bitscore as tiebreaker
                    if current['bitscore'] >= next_hit['bitscore']:  # Higher is better
                        remove_indices.append(next_idx)
                        indices.pop(i + 1)
                    else:
                        remove_indices.append(current_idx)
                        indices.pop(i)
            else:
                i += 1

    # Remove marked indices and return
    df = df.drop(remove_indices).reset_index(drop=True)

    return df


def add_metadata(df: pd.DataFrame, metadata: str) -> pd.DataFrame:
    """
    Adds dbCAN metadata to the filtered dbCAN hmmsearch results
    """
    mapping = pd.read_csv(
        metadata, sep="\t", usecols=["Family", "Name", "_Substrate_curated"]
    )

    # If a family has more than one Name or substrate, condense into one column separated by semicolon
    mapping = mapping.groupby("Family", as_index=False).agg(
        {
            "Name": lambda x: (
                "; ".join(x.dropna().unique()) if x.notna().any() else None
            ),
            "_Substrate_curated": lambda x: (
                "; ".join(x.dropna().unique()) if x.notna().any() else None
            ),
        }
    )

    # Merge metadata with the results
    df = df.merge(mapping, left_on="hmm_id", right_on="Family", how="left")

    # Set missing values to "unknown"
    df["Name"] = df["Name"].fillna("unknown")
    df["_Substrate_curated"] = df["_Substrate_curated"].fillna("unknown")

    # Drop redundant Family column
    df = df.drop(columns=["Family"])
    df = df.drop(columns=["i_evalue"])

    column_order = [
        "seq_name", "seq_len", "hmm", "hmm_id", "hmm_length", 
        "i_evalue_formatted", "bitscore", "coverage",
        "hmm_from", "hmm_to", "ali_from", "ali_to",
        "Name", "_Substrate_curated"
    ]
    df = df[column_order]

    return df


def condense_by_gene(df: pd.DataFrame) -> pd.DataFrame:
    """
    If the parsed domtblout has a protein with more than one domain, merge this into one column.
    """
    # Select relevant columns
    df["ali_pos"] = df["ali_from"].astype(str) + "-" + df["ali_to"].astype(str)

    # Condense seq_name
    grouped = df.groupby(["seq_name"], as_index=False).agg(
        {
            "hmm_id": lambda x: " | ".join(x.dropna()) if x.notna().any() else None,
            "i_evalue_formatted": lambda x: " | ".join(x.astype(str).dropna().unique()),
            "ali_pos": lambda x: (
                " | ".join(x.dropna().unique()) if x.notna().any() else None
            ),
            "Name": lambda x: " | ".join(x.dropna().unique()),
            "_Substrate_curated": lambda x: " | ".join(x.dropna().unique()),
        }
    )

    return grouped


def main():
    # Arguments
    # metadata_path = "data/fam-substrate-mapping-08262025.tsv"
    # file_path = "data/domain_results.txt"
    # outpath = "results/"
    # e_cutoff = 1e-10
    # cov_cutoff = 0.30
    args = parse_arguments()

    # Ensure output dir exists
    os.makedirs(args.outdir, exist_ok=True)

    # Parsing
    print(f"Parsing {args.input}...")
    df = parse_domtblout(args.input, args.evalue, args.coverage)
    print(f"  Found {len(df)} hits passing E-value and coverage filters")

    # Remove overlapping hits
    print("Removing overlapping hits...")
    df_filt = remove_overlaps(df, args.overlap_threshold)
    print(f"  {len(df_filt)} hits remaining after overlap removal")

    # Add metadata
    print("Adding metadata...")
    df_meta = add_metadata(df_filt, args.metadata)

    # Save detailed results
    detailed_output = os.path.join(args.outdir, "dbcan_detailed.tsv")
    df_meta.to_csv(detailed_output, sep="\t", index=False)
    print(f"  Detailed results saved to {detailed_output}")

    # Provide summary (one row per sequence)
    print("Condensing by gene...")
    df_condensed = condense_by_gene(df_meta)

    # Save condensed results
    summary_output = os.path.join(args.outdir, "dbcan_summary.tsv")
    df_condensed.to_csv(summary_output, sep="\t", index=False)
    print(f"  Summary results saved to {summary_output}")

    print(f"\nDone! Found CAZyme domains in {len(df_condensed)} sequences")


if __name__ == "__main__":
    main()
