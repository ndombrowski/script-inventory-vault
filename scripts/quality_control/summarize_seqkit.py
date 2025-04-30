import pandas as pd
import argparse 
import tabulate

# Apply comma formatting to large numbers (optional but helpful)
def format_number(val):
    if pd.isnull(val):
        return val
    if abs(val) >= 1000 and isinstance(val, (int, float)):
        return f"{val:,.2f}"
    return val

def main(): 
  # Setup argument parser 
  parser = argparse.ArgumentParser(description="Summarize seqkit stats")
  parser.add_argument("-i", "--input", required=True, help="Input file")
  parser.add_argument("-o", "--output", required=True, help="Output file")  
  args = parser.parse_args() 

  # Get input file 
  df = pd.read_csv(args.input, sep = "\t")

  # Get columns of interest
  df_red = df[['num_seqs', 'sum_len', 'min_len', 'avg_len', 'max_len', 'AvgQual', 'GC(%)' ]].copy()

  # Calculate total, min, max, mean, median for each column 
  stats = df_red.agg(['sum', 'min', 'max', 'mean', 'median'])

  # Format output
  stats = stats.transpose().round(1)

  # Format output
  stats_formatted = stats.map(format_number) 

  # Replace 'sum' column values with '-' where not applicable
  for idx in stats_formatted.index:
      if idx not in ['num_seqs', 'sum_len']:
          stats_formatted.at[idx, 'sum'] = '-'

  # Save formatted stats to output file
  stats_formatted.to_csv(args.output, sep="\t", index=True)

  # Print markdown formatted table to console
  print("## Seqkit stats summary")
  print(stats_formatted.to_markdown())
  print("\n\n")

if __name__ == "__main__":
    main()
