import pandas as pd
import numpy as np

df = pd.read_csv("results/vsearch/amplicons_identity.tsv", sep="\t", header=None)
df.columns = ["qseqid","sseqid","pident","length","mismatch","gapopen","qstart","qend","sstart","send","evalue","bitscore"]

# Pivot
matrix = df.pivot(index="qseqid", columns="sseqid", values="pident")

# Sort columns by number of non-missing values (descending)
col_order = matrix.notna().sum().sort_values(ascending=False).index
matrix_sorted_cols = matrix[col_order]

# Sort rows by number of non-missing values (descending)
row_order = matrix_sorted_cols.notna().sum(axis=1).sort_values(ascending=False).index
matrix_sorted = matrix_sorted_cols.loc[row_order]

# Print
matrix_sorted.to_csv("results/vsearch/amplicons_identity_matrix.csv")