#!/usr/bin/env python3
###########################################################
# parse_diamond_hydDB.py
#
# Parse diamond blast output for hydDB annotation
#
# Author: Nina Dombrowski
# Date: 2025-02-12
# Version: 1.0.0
#
# Cutoffs based on: https://github.com/GreeningLab/HydDB
#
# Last updated: 2025-02-12
###########################################################

import pandas as pd
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="""Parse and filter diamond blastp hydrogenase search results\nExample: python parse_diamond.py -i data/results.txt -o results/hyddb_parsed.tsv --evalue 1e-5
    """,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Required arguments
    parser.add_argument("-i", "--input", required=True, help="Input HMMER tblout file")

    parser.add_argument(
        "-o", "--output", required=True, help="Output filtered TSV file"
    )

    # Optional filtering arguments
    parser.add_argument(
        "--evalue", type=float, default=1e-10, help="E-value cutoff (default: 1e-10)"
    )

    parser.add_argument(
        "--cutoff-fefe",
        type=float,
        default=45,
        help="Percent identity cutoff for FeFe hydrogenases (default: 45)",
    )

    parser.add_argument(
        "--cutoff-nife-all",
        type=float,
        default=30,
        help="Percent identity cutoff for NiFe Groups 1, 2, 3 (default: 30)",
    )

    parser.add_argument(
        "--cutoff-nife-group-4",
        type=float,
        default=50,
        help="Percent identity cutoff for NiFe Group 4 (default: 50)",
    )

    parser.add_argument(
        "--cutoff-feonly",
        type=float,
        default=50,
        help="Percent identity cutoff for Fe-only hydrogenases (default: 50)",
    )

    return parser.parse_args()


def parse_tblout(
    filename: str,
) -> pd.DataFrame:
    """
    Read in and extract relevant columns from hmmsearch tblout.

    Parameters
    ----------
    filename : str
        Path to HMMER tblout file

    Returns
    -------
    pd.DataFrame
        Parsed dataframe with cleaned hydrogenase annotations
    """
    df = pd.read_csv(
        filename,
        comment="#",
        header=None,
        usecols=[0, 2, 3, 5, 10, 11, 12, 13],
        names=[
            "seq_name",  # 0
            "seq_len",  # 2
            "query",  # 3
            "query_len",  # 5
            "evalue",  # 10
            "bitscore",  # 11
            "aln_length",  # 12
            "pident",  # 13
        ],
        sep="\s+",
    )

    # Clean query
    split_query = df["query"].str.split("|", expand=True)
    if split_query.shape[1] != 3:
        raise ValueError(
            "Query column format incorrect. Expected format: 'ID|Taxonomy|[Hyd_Type]'"
        )

    df[["id", "taxonomy", "hyd"]] = split_query
    df["hyd"] = df["hyd"].str.replace("[", "", regex=False)
    df["hyd"] = df["hyd"].str.replace("]", "", regex=False)

    df = df.drop(columns=["id"])
    df = df.drop(columns=["taxonomy"])

    return df


def filter_table(
    df,
    evalue_cutoff=1e-10,
    cutoff_fefe=45,
    cutoff_nife_all=30,
    cutoff_nife_group_4=50,
    cutoff_feonly=50,
):
    """
    Filters HMMER results using query-specific score thresholds.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing HMMER results
    evalue_cutoff : float
        Maximum E-value threshold (default: 1e-10)
    cutoff_fefe : float
        Minimum score for FeFe queries (default: 45)
    cutoff_nife_all : float
        Minimum score for general NiFe queries (default: 30)
    cutoff_nife_group_4 : float
        Minimum score for NiFe_group_4 queries (default: 50)
    cutoff_feonly : float
        Minimum score for FeOnly queries (default: 50)

    Returns
    -------
    pd.DataFrame
        Filtered results meeting both E-value and query-specific score criteria
    """
    # Apply evalue cutoff
    filtered_df = df[df["evalue"] <= evalue_cutoff].copy()

    # keep only best hit/sequence
    filtered_df = (
        filtered_df.sort_values(
            ["seq_name", "evalue", "bitscore"], ascending=[True, True, False]
        )
        .groupby("seq_name", as_index=False)
        .first()
    )

    # Create boolean masks for each category
    mask_fefe = filtered_df["hyd"].str.startswith("FeFe_Group", na=False) & (
        filtered_df["pident"] >= cutoff_fefe
    )

    mask_nife_group4 = filtered_df["hyd"].str.startswith("NiFe_Group_4", na=False) & (
        filtered_df["pident"] >= cutoff_nife_group_4
    )

    mask_nife_other = (
        filtered_df["hyd"].str.startswith("NiFe_Group", na=False)
        & ~filtered_df["hyd"].str.startswith("NiFe_Group_4", na=False)
        & (filtered_df["pident"] >= cutoff_nife_all)
    )

    mask_feonly = (filtered_df["hyd"] == "Fe") & (
        filtered_df["pident"] >= cutoff_feonly
    )

    # Combine all masks
    final_mask = mask_fefe | mask_nife_group4 | mask_nife_other | mask_feonly

    # Only keep rows that match any category
    return filtered_df[final_mask]


def main():
    # # Arguments
    # filepath = "data/results.txt"
    # outfile = "results/hyddb_parsed.tsv"
    # evalue_cutoff = 1e-10
    # cutoff_fefe = 45
    # cutoff_nife_all = 30
    # cutoff_nife_group_4 = 50
    # cutoff_feonly = 50
    args = parse_arguments()

    # Read in data
    df = parse_tblout(args.input)
    df_filtered = filter_table(
        df,
        evalue_cutoff=args.evalue,
        cutoff_fefe=args.cutoff_fefe,
        cutoff_nife_all=args.cutoff_nife_all,
        cutoff_nife_group_4=args.cutoff_nife_group_4,
        cutoff_feonly=args.cutoff_feonly,
    )

    # Write output
    df_filtered.to_csv(args.output, sep="\t", index=False)
    print(f"Filtered {len(df_filtered)} hits from {len(df)} total hits")
    print(f"Results written to {args.output}")


if __name__ == "__main__":
    main()
