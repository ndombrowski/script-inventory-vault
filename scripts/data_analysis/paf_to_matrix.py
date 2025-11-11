import pandas as pd
from pathlib import Path
import argparse
import sys 
import matplotlib.pyplot as plt

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate OTU tables and summary read counts from per-sample mapping stats files."
    )
    parser.add_argument(
        "-i", "--input_folder",
        type=str,
        default="results/mapping_counts",
        help="Folder containing barcode*_stats.tsv files (default: results/mapping_counts)"
    )
    parser.add_argument(
        "-o", "--output_folder",
        type=str,
        default="results/mapping_counts",
        help="Folder to write output files (default: results/mapping_counts)"
    )
    parser.add_argument(
        "-t", "--taxa_mapping",
        type=str,
        default="data/genome_to_genus.tsv",
        help="Two column tab-delimited file with the genome and genus information (default: data/genome_to_genus.tsv)"
    )
    parser.add_argument(
        "-s", "--stats_file",
        type=str,
        default=None,
        help="Optional: path to the seqkit stats output (-Toa format)"
    )
    parser.add_argument(
        "--cov",
        type=float, 
        default=0.9, 
        help="Minimum query coverage threshold (default: 0.9)")
    parser.add_argument(
        "--id", 
        type=float, 
        default=0.9, 
        help="Minimum sequence identity threshold (default: 0.9)")
    parser.add_argument(
        "--mapq", 
        type=int, 
        default=30, 
        help="Minimum MAPQ threshold (default: 30, keeps multimappers (mapq 0)")

    return parser.parse_args()


def read_paf_with_AS(paf_file):
    """
    Reads a PAF file, keeping the first 12 standard columns and the AS:i: optional field.
    Returns a DataFrame with AS as a separate column.
    """
    rows = []
    with open(paf_file) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split("\t")
            # First 12 standard columns
            std_cols = parts[:12]
            # Look for AS:i:<value> in optional fields
            AS = None
            for opt in parts[12:]:
                if opt.startswith("AS:i:"):
                    AS = int(opt.split(":")[-1])
                    break
            # Append row (first 12 + AS)
            rows.append(std_cols + [AS])
    
    # Create DataFrame
    colnames = [
        "qname","qlen","qstart","qend","strand",
        "tname","tlen","tstart","tend","nmatch",
        "alen","mapq","AS"
    ]
    df = pd.DataFrame(rows, columns=colnames)
    return df


def main():
    # ----------------------------- Define parameters ---------------------------- #
    args = parse_args()
    input_folder = Path(args.input_folder)
    taxon_path=Path(args.taxa_mapping)
    stats_path = Path(args.stats_file) if args.stats_file else None
    
    coverage_threshold = args.cov
    identity_threshold = args.id
    mapq_threshold = args.mapq
    
    output_folder = Path(args.output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    # For testing (change to true for testing)
    if False:  
        input_folder = Path("../results/mapping_counts/")
        taxon_path = Path("../data/genome_to_genus.tsv")
        stats_path = Path("../results/seqkit/fastq_filtered.tsv")
        output_folder = Path("../results/mapping_counts/")
        coverage_threshold = 0.9   # minimum fraction of query covered
        identity_threshold = 0.9   # optional, if you compute identity from AS/optional tags
        mapq_threshold = 30

     # ------------------------------- Read in taxa info --------------------------- #
    taxon_df = pd.read_csv(taxon_path, sep="\t")
    if "tname" not in taxon_df.columns:
        taxon_df.columns = ["tname", "genus"]
        
        
    # ------------------------------- Read in PAFs ------------------------------- #
    all_files = list(input_folder.glob("barcode*.paf"))
    dfs = []

    # On all files
    for paf_file in all_files:
        barcode = paf_file.stem
        df = read_paf_with_AS(paf_file)
        df["sample"] = barcode
        dfs.append(df)

    if not dfs:
        sys.exit("No PAF files found in input folder. Exiting.")

    df = pd.concat(dfs, ignore_index=True)

    
    # ------------------------------ Filter PAFs -------------------------------- #
    # Convert numeric columns to integers
    df = df.copy()
    numeric_cols = ["qlen","qstart","qend","tlen","tstart","tend","nmatch","alen","mapq","AS"]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
    
    # Calculate query coverage and identity
    df["qcov"] = (df.qend - df.qstart + 1) / df.qlen
    df["identity"] = df["nmatch"] / df["alen"].replace(0, pd.NA)

    # Visualize the data distribution of key parameters
    for col, bins in [("qcov", 50), ("identity", 100), ("mapq", 100)]:
        plt.figure()
        df[col].hist(bins=bins)
        plt.title(col)
        plt.xlabel(col)
        plt.ylabel("Count")
        plt.savefig(output_folder / f"{col}_hist.png")
        plt.close()
        
    # Filter on query coverage, sequency identity and mapq to discard uncertain hits
    # But keep multimappers (map=0)
    df = df[(df.qcov >= coverage_threshold) &
            (df.identity >= identity_threshold) &
            ((df.mapq == 0) | (df.mapq >= mapq_threshold))]


    # ------------------- Generate table including multimappers ------------------ #
    # Count reads per target 
    counts_multi = df.groupby(["sample", "tname"]).size().reset_index(name="reads")
    otu_table_multi = counts_multi.pivot(index = "tname", columns = "sample", values = "reads").fillna(0).astype(int)
    otu_table_multi_tax = taxon_df.merge(otu_table_multi, on = "tname", how = "right").set_index("tname")


    # -------------------- Generate table with best-hits only -------------------- #
    # Select best hit per query (highest qcov, then highest AS, highest mapq, longest aln as tie breaker)
    df_best = df.sort_values(
        ["qname", "qcov", "AS", "mapq", "alen"], 
        ascending=[True, False, False, False, False]
    ).drop_duplicates("qname")

    # Count reads per target 
    counts = df_best.groupby(["sample", "tname"]).size().reset_index(name="reads")
        
    # Add unmapped reads if stats are provided
    if stats_path and stats_path.exists():
        stats = pd.read_csv(stats_path, sep = "\t")
        stats["sample"] = stats["file"].apply(lambda x: Path(x).stem.split(".")[0])  
        
        mapped_seqs = counts.groupby("sample")["reads"].sum()
        barcode_total_seqs = stats.groupby("sample")["num_seqs"].sum()
        unmapped_seqs = (barcode_total_seqs - mapped_seqs).reset_index()
        unmapped_seqs.columns = ["sample", "reads"] 
        unmapped_seqs["tname"] = "unassigned"
        unmapped_seqs = unmapped_seqs[["sample", "tname", "reads"]]

        counts = pd.concat([counts, unmapped_seqs], ignore_index=True)

    # Generate OTU table
    otu_table = counts.pivot(index="tname", columns="sample", values="reads").fillna(0).astype(int)
    otu_table_tax = taxon_df.merge(otu_table, on = "tname", how = "right").set_index("tname")


    # ---------------- Generate table with best-hits and taxonomy ---------------- #
    # Combine with counts and deal with unassigned reads    
    counts_tax = counts.merge(taxon_df, on='tname', how='left').fillna("unassigned")
    
    # Merge counts on genus level
    counts_genus = counts_tax.groupby(["sample", "genus"], as_index=False)["reads"].sum()
    
    # Generate OTU table  
    otu_table_genus = counts_genus.pivot(index="genus", columns="sample", values="reads").fillna(0).astype(int)


    # ------------------------------- Write to file ------------------------------ #
    otu_table_tax.to_csv(output_folder / "otu_table.tsv", sep="\t")
    otu_table_multi_tax.to_csv(output_folder / "otu_table_multimappers.tsv", sep = "\t", index= False)
    otu_table_genus.to_csv(output_folder / "otu_table_genus.tsv", sep="\t") 

    print(f"otu_table.tsv, otu_table_multimappers.tsv and otu_table_genus.tsv written to {output_folder}")


if __name__ == "__main__":
    main()
